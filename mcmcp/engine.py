"""Everything that touches the running server or its save files.

Placement pipeline for a build:
  1. force-load every chunk the build covers and wait until they're loaded
     (this also generates chunks nobody has visited yet);
  2. `save-all flush`, then read the current blocks there from the region files:
     that snapshot becomes an "undo" structure template;
  3. compile the planned blocks into one structure template (.nbt) in
     world/generated/mcp/structure/ and place it with a single `/place template`;
  4. spawn entities / run follow-up commands, release the force-loads, record history.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import time
import uuid
from dataclasses import dataclass

from . import blocks, nbt
from .canvas import Canvas
from .nbt import COMPOUND, INT, LIST, Tag
from .rcon import Rcon, RconError
from .world import World

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_DIR = os.environ.get("MCMCP_SERVER_DIR", os.path.join(ROOT, "server"))
JAVA = os.environ.get("MCMCP_JAVA") or next(
    (os.path.join(ROOT, "runtime", d, "bin", "java.exe") for d in sorted(os.listdir(os.path.join(ROOT, "runtime")))
     if os.path.isfile(os.path.join(ROOT, "runtime", d, "bin", "java.exe"))), "java") \
    if os.path.isdir(os.path.join(ROOT, "runtime")) else "java"
HISTORY = os.path.join(ROOT, "data", "builds.json")
NAMESPACE = "mcp"


class EngineError(RuntimeError):
    pass


def read_props(path: str) -> dict[str, str]:
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k] = v.replace("\\:", ":")
    return out


@dataclass
class Placement:
    id: str
    name: str
    dimension: str
    origin: tuple[int, int, int]
    min: tuple[int, int, int]
    max: tuple[int, int, int]
    blocks: int
    template: str
    undo_template: str
    created: float
    undone: bool = False

    def as_dict(self):
        return self.__dict__.copy()


class Engine:
    def __init__(self, server_dir: str = SERVER_DIR):
        self.server_dir = server_dir
        self._rcon: Rcon | None = None
        self._world: World | None = None
        self._data_version: int | None = None
        self._proc: subprocess.Popen | None = None

    # -- config / connections ---------------------------------------------
    @property
    def props(self) -> dict[str, str]:
        return read_props(os.path.join(self.server_dir, "server.properties"))

    @property
    def world_dir(self) -> str:
        return os.path.join(self.server_dir, self.props.get("level-name", "world"))

    @property
    def world(self) -> World:
        if self._world is None or self._world.dir != self.world_dir:
            self._world = World(self.world_dir)
        return self._world

    @property
    def rcon(self) -> Rcon:
        if self._rcon is None:
            p = self.props
            if p.get("enable-rcon") != "true":
                raise EngineError("RCON is disabled in server.properties (enable-rcon=true)")
            host = p.get("server-ip") or "127.0.0.1"
            self._rcon = Rcon(host, int(p.get("rcon.port", 25575)), p.get("rcon.password", ""))
        return self._rcon

    def cmd(self, command: str, dimension: str | None = None) -> str:
        if dimension and blocks.ns(dimension) != "minecraft:overworld":
            command = f"execute in {blocks.ns(dimension)} run {command.lstrip('/')}"
        try:
            return self.rcon.command(command)
        except (OSError, ConnectionError) as e:
            raise EngineError(f"server not reachable over RCON ({e}). Start it with start_server.") from e

    def is_running(self) -> bool:
        try:
            self.rcon.command("list")
            return True
        except Exception:
            return False

    @property
    def data_version(self) -> int:
        if self._data_version is None:
            m = re.search(r"data = (\d+)", self.cmd("version"))
            self._data_version = int(m.group(1)) if m else 5023
        return self._data_version

    # -- lifecycle ----------------------------------------------------------
    def start(self, memory_gb: int = 4, wait: float = 120) -> str:
        if self.is_running():
            return "already running"
        log_dir = os.path.join(self.server_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        out = open(os.path.join(log_dir, "mcp-console.log"), "ab")
        flags = 0
        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        self._proc = subprocess.Popen(
            [JAVA, f"-Xmx{memory_gb}G", f"-Xms{min(memory_gb, 2)}G", "-jar", "server.jar", "nogui"],
            cwd=self.server_dir, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, creationflags=flags)
        t0 = time.time()
        while time.time() - t0 < wait:
            if self._proc.poll() is not None:
                raise EngineError(f"server exited with code {self._proc.returncode}; see logs/latest.log")
            if self.is_running():
                self._data_version = None
                return f"started in {time.time() - t0:.0f}s (pid {self._proc.pid})"
            time.sleep(1)
        raise EngineError("server did not open RCON in time; see logs/latest.log")

    def stop(self) -> str:
        if not self.is_running():
            return "not running"
        try:
            self.rcon.command("stop")
        except Exception:
            pass
        self.rcon.close()
        for _ in range(60):
            time.sleep(1)
            if not self.is_running():
                return "stopped"
        return "stop requested"

    def log_tail(self, lines: int = 40) -> str:
        p = os.path.join(self.server_dir, "logs", "latest.log")
        if not os.path.exists(p):
            return ""
        with open(p, encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-lines:])

    # -- chunk loading ------------------------------------------------------
    def flush(self):
        self.cmd("save-all flush")
        self.world.invalidate()

    def forced_chunks(self, dimension: str) -> set[tuple[int, int]]:
        out = self.cmd("forceload query", dimension)
        return {(int(a), int(b)) for a, b in re.findall(r"\[(-?\d+), (-?\d+)\]", out)}

    def load_area(self, dimension: str, x1: int, z1: int, x2: int, z2: int, timeout: float = 60) -> list[tuple[int, int]]:
        """Force-load the chunks covering the box; returns the ones we added (to release later)."""
        cx1, cx2 = sorted((x1 >> 4, x2 >> 4))
        cz1, cz2 = sorted((z1 >> 4, z2 >> 4))
        want = {(cx, cz) for cx in range(cx1, cx2 + 1) for cz in range(cz1, cz2 + 1)}
        if len(want) > 4096:
            raise EngineError(f"area spans {len(want)} chunks; split it into smaller builds (max 4096)")
        have = self.forced_chunks(dimension)
        added = sorted(want - have)
        # forceload accepts a rectangle of at most 256 chunks per command
        for gx in range(cx1, cx2 + 1, 16):
            for gz in range(cz1, cz2 + 1, 16):
                ex, ez = min(gx + 15, cx2), min(gz + 15, cz2)
                self.cmd(f"forceload add {gx * 16} {gz * 16} {ex * 16} {ez * 16}", dimension)
        pending = set(want)
        t0 = time.time()
        while pending and time.time() - t0 < timeout:
            for cx, cz in list(pending):
                if "passed" in self.cmd(f"execute if loaded {cx * 16} 0 {cz * 16}", dimension):
                    pending.discard((cx, cz))
            if pending:
                time.sleep(0.25)
        if pending:
            self.release(dimension, added)
            raise EngineError(f"{len(pending)} chunks did not load within {timeout}s")
        return added

    def release(self, dimension: str, chunks: list[tuple[int, int]]):
        # With several builders working side by side, one releasing a shared border chunk would
        # unload it under a neighbour; they set MCMCP_KEEP_FORCELOAD=1 and the area is released after.
        if os.environ.get("MCMCP_KEEP_FORCELOAD") == "1":
            return
        for cx, cz in chunks:
            self.cmd(f"forceload remove {cx * 16} {cz * 16}", dimension)

    # -- structure templates -----------------------------------------------
    def structure_dir(self, namespace: str = NAMESPACE) -> str:
        d = os.path.join(self.world_dir, "generated", namespace, "structure")
        os.makedirs(d, exist_ok=True)
        return d

    def write_template(self, name: str, cells: dict[tuple[int, int, int], tuple[str, Tag | None]],
                       entities: list | None = None) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """Write cells (absolute coords) as a structure. Returns (min corner, size)."""
        xs, ys, zs = zip(*cells)
        mn = (min(xs), min(ys), min(zs))
        size = (max(xs) - mn[0] + 1, max(ys) - mn[1] + 1, max(zs) - mn[2] + 1)
        palette: dict[str, int] = {}
        pal_out = []
        blist = []
        for (x, y, z), (state, be) in cells.items():
            idx = palette.get(state)
            if idx is None:
                idx = palette[state] = len(pal_out)
                block_id, props = blocks.parse(state)
                entry = {"id": block_id}
                if props:
                    entry["properties"] = dict(props)
                pal_out.append(entry)
            rec = {"pos": Tag(LIST, [Tag(INT, x - mn[0]), Tag(INT, y - mn[1]), Tag(INT, z - mn[2])]), "state": Tag(INT, idx)}
            if be is not None:
                rec["nbt"] = be
            blist.append(rec)
        root = {
            "DataVersion": Tag(INT, self.data_version),
            "size": Tag(LIST, [Tag(INT, v) for v in size]),
            "palette": pal_out,
            "blocks": blist,
            "entities": Tag(LIST, entities or []),
        }
        path = os.path.join(self.structure_dir(), f"{name}.nbt")
        with open(path, "wb") as f:
            f.write(nbt.write_root(root))
        return mn, size

    def read_template(self, template: str) -> dict[tuple[int, int, int], tuple[str, Tag | None]]:
        """Load a structure file (ours or any namespace under generated/) into relative cells."""
        ns_, _, name = blocks.ns(template).partition(":")
        path = os.path.join(self.world_dir, "generated", ns_, "structure", f"{name}.nbt")
        if not os.path.exists(path):
            raise EngineError(f"no template file at {path}")
        with open(path, "rb") as f:
            root = nbt.read(f.read(), typed=True)
        palettes = root.get("palette") or (root["palettes"].value[0] if "palettes" in root else Tag(LIST, []))
        pal = []
        for e in palettes.value:
            d = e.value
            name_ = (d.get("id") or d.get("Name")).value
            props = d.get("properties") or d.get("Properties")
            pal.append(blocks.fmt(name_, {k: v.value for k, v in props.value.items()}) if props else name_)
        out = {}
        for b in root["blocks"].value:
            bd = b.value
            x, y, z = (t.value for t in bd["pos"].value)
            out[(x, y, z)] = (pal[bd["state"].value], bd.get("nbt"))
        return out

    # -- snapshots ----------------------------------------------------------
    def snapshot(self, positions, dimension: str) -> dict[tuple[int, int, int], tuple[str, Tag | None]]:
        """Current world state at the given absolute positions (call after flush)."""
        w = self.world
        out = {}
        typed_cache: dict[tuple[int, int], dict] = {}
        for (x, y, z) in positions:
            st = w.block(x, y, z, dimension) or "minecraft:air"
            be = None
            ch = w.chunk(x >> 4, z >> 4, dimension)
            if ch and (x, y, z) in ch.block_entities:
                key = (x >> 4, z >> 4)
                if key not in typed_cache:
                    typed_cache[key] = self._typed_block_entities(x >> 4, z >> 4, dimension)
                raw = typed_cache[key].get((x, y, z))
                if raw is not None:
                    be = Tag(COMPOUND, {k: v for k, v in raw.items() if k not in ("x", "y", "z", "keepPacked")})
            out[(x, y, z)] = (st, be)
        return out

    def _typed_block_entities(self, cx: int, cz: int, dimension: str) -> dict:
        import struct
        import zlib
        rdir = self.world.region_dir(dimension)
        with open(os.path.join(rdir, f"r.{cx >> 5}.{cz >> 5}.mca"), "rb") as f:
            f.seek(4 * ((cx & 31) + (cz & 31) * 32))
            (loc,) = struct.unpack(">I", f.read(4))
            f.seek((loc >> 8) * 4096)
            length, ctype = struct.unpack(">IB", f.read(5))
            raw = f.read(length - 1)
        root = nbt.read(zlib.decompress(raw) if ctype == 2 else raw, typed=True)
        out = {}
        for be in root.get("block_entities", Tag(LIST, [])).value:
            d = be.value
            out[(d["x"].value, d["y"].value, d["z"].value)] = d
        return out

    # -- history ------------------------------------------------------------
    @contextlib.contextmanager
    def _history_lock(self, timeout: float = 60):
        """Cross-process lock so parallel builders don't lose each other's history entries."""
        lock = HISTORY + ".lock"
        os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
        t0 = time.time()
        while True:
            try:
                os.mkdir(lock)
                break
            except FileExistsError:
                if time.time() - os.path.getmtime(lock) > 120:   # stale lock from a crashed process
                    os.rmdir(lock)
                    continue
                if time.time() - t0 > timeout:
                    raise EngineError("timed out waiting for the build-history lock")
                time.sleep(0.05)
        try:
            yield
        finally:
            os.rmdir(lock)

    def history(self) -> list[Placement]:
        if not os.path.exists(HISTORY):
            return []
        with open(HISTORY, encoding="utf-8") as f:
            return [Placement(**{**d, "origin": tuple(d["origin"]), "min": tuple(d["min"]), "max": tuple(d["max"])})
                    for d in json.load(f)]

    def _save_history(self, items: list[Placement]):
        os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
        with open(HISTORY, "w", encoding="utf-8") as f:
            json.dump([p.as_dict() for p in items], f, indent=1)

    # -- the main operation -------------------------------------------------
    def place_cells(self, cells: dict[tuple[int, int, int], tuple[str, Tag | None]], name: str,
                    dimension: str = "minecraft:overworld", origin=(0, 0, 0),
                    entities: list | None = None, commands: list | None = None) -> dict:
        """Place absolute-coordinate cells as one template, with an undo snapshot."""
        if not cells:
            raise EngineError("nothing to place: the build produced no blocks")
        dimension = blocks.ns(dimension)
        t0 = time.time()
        xs, ys, zs = zip(*cells)
        mn, mx = (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
        lo, hi = self.height_limits(dimension)
        if mn[1] < lo or mx[1] > hi:
            raise EngineError(f"build spans y {mn[1]}..{mx[1]} but {dimension} allows {lo}..{hi}")
        bid = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:4]
        added = self.load_area(dimension, mn[0], mn[2], mx[0], mx[2])
        try:
            self.flush()
            before = self.snapshot(cells.keys(), dimension)
            changed = {p: v for p, v in cells.items()
                       if v[1] is not None or blocks.canonical(before[p][0]) != blocks.canonical(v[0])}
            undo = {p: before[p] for p in changed}
            if not changed:
                return {"id": None, "message": "every planned block already matches the world; nothing placed"}
            tpl, utpl = f"b_{bid}", f"u_{bid}"
            pmn, _ = self.write_template(tpl, changed)
            self.write_template(utpl, undo)
            res = self.cmd(f"place template {NAMESPACE}:{tpl} {pmn[0]} {pmn[1]} {pmn[2]}", dimension)
            if "Loaded template" not in res:
                raise EngineError(f"/place template failed: {res}")
            # Replacing blocks can pop attached things (torches, carpets, plants) off as items; sweep them up.
            post = [self.cmd(f"kill @e[type=item,x={mn[0]},y={mn[1]},z={mn[2]},"
                             f"dx={mx[0] - mn[0] + 1},dy={mx[1] - mn[1] + 1},dz={mx[2] - mn[2] + 1}]", dimension)]
            for eid, ex, ey, ez, snbt in entities or []:
                post.append(self.cmd(f"summon {eid} {ex} {ey} {ez} {snbt}".strip(), dimension))
            for c, (ax, ay, az) in commands or []:
                post.append(self.cmd(c.replace("{x}", str(ax)).replace("{y}", str(ay)).replace("{z}", str(az)), dimension))
        finally:
            self.release(dimension, added)
        cmn = tuple(min(p[i] for p in changed) for i in range(3))
        cmx = tuple(max(p[i] for p in changed) for i in range(3))
        pl = Placement(bid, name, dimension, tuple(origin), cmn, cmx, len(changed),
                       f"{NAMESPACE}:{tpl}", f"{NAMESPACE}:{utpl}", time.time())
        with self._history_lock():
            hist = self.history()
            hist.append(pl)
            self._save_history(hist)
        errors = [p for p in post[1:] if p and ("Unknown" in p or "Incorrect" in p or "rror" in p or "Invalid" in p)]
        return {"id": bid, "name": name, "dimension": dimension, "blocks_changed": len(changed),
                "blocks_planned": len(cells), "min": cmn, "max": cmx,
                "size": [cmx[i] - cmn[i] + 1 for i in range(3)], "seconds": round(time.time() - t0, 2),
                "entities": len(entities or []), "post_errors": errors[:5]}

    def place_canvas(self, canvas: Canvas, origin: tuple[int, int, int], name: str,
                     dimension="minecraft:overworld") -> dict:
        ox, oy, oz = origin
        cells = {(x + ox, y + oy, z + oz): v for (x, y, z), v in canvas.voxels.items()}
        ents = [(e, x + ox, y + oy, z + oz, s) for e, x, y, z, s in canvas.entities]
        cmds = [(c, (x + ox, y + oy, z + oz)) for c, (x, y, z) in canvas.commands]
        return self.place_cells(cells, name, dimension, origin, ents, cmds)

    def undo(self, build_id: str | None = None) -> dict:
        hist = self.history()
        live = [p for p in hist if not p.undone]
        if not live:
            raise EngineError("nothing to undo")
        target = next((p for p in live if p.id == build_id), None) if build_id else live[-1]
        if target is None:
            raise EngineError(f"no active build with id {build_id}")
        later = [p for p in live if p.created > target.created and _overlaps(p, target)]
        added = self.load_area(target.dimension, target.min[0], target.min[2], target.max[0], target.max[2])
        try:
            res = self.cmd(f"place template {target.undo_template} {target.min[0]} {target.min[1]} {target.min[2]}",
                           target.dimension)
        finally:
            self.release(target.dimension, added)
        if "Loaded template" not in res:
            raise EngineError(f"undo failed: {res}")
        a, b_ = target.min, target.max
        self.cmd(f"kill @e[type=item,x={a[0]},y={a[1]},z={a[2]},dx={b_[0] - a[0] + 1},dy={b_[1] - a[1] + 1},dz={b_[2] - a[2] + 1}]",
                 target.dimension)
        with self._history_lock():
            hist = self.history()
            for p in hist:
                if p.id == target.id:
                    p.undone = True
            self._save_history(hist)
        out = {"undone": target.id, "name": target.name, "blocks": target.blocks}
        if later:
            out["warning"] = "later builds overlapped this one and may now be partly overwritten: " + \
                             ", ".join(p.id for p in later)
        return out

    def height_limits(self, dimension: str) -> tuple[int, int]:
        if dimension == "minecraft:overworld":
            return -64, 319
        if dimension in ("minecraft:the_nether", "minecraft:the_end"):
            return 0, 255
        return -2032, 2031

    # -- regeneration --------------------------------------------------------
    def regenerate_chunks(self, dimension: str, x1: int, z1: int, x2: int, z2: int) -> dict:
        """Delete chunks from the save so the game regenerates them from the seed (natural terrain).
        Stops the server while editing region files, then starts it again."""
        import struct
        dimension = blocks.ns(dimension)
        cx1, cx2 = sorted((x1 >> 4, x2 >> 4))
        cz1, cz2 = sorted((z1 >> 4, z2 >> 4))
        chunks = [(cx, cz) for cx in range(cx1, cx2 + 1) for cz in range(cz1, cz2 + 1)]
        if len(chunks) > 1024:
            raise EngineError("max 1024 chunks per call")
        was_running = self.is_running()
        if was_running:
            for cx, cz in chunks:
                self.cmd(f"forceload remove {cx * 16} {cz * 16}", dimension)
            self.stop()
        rdir = self.world.region_dir(dimension)
        base = os.path.dirname(rdir)
        removed = 0
        for sub in ("region", "entities", "poi"):
            d = os.path.join(base, sub)
            for cx, cz in chunks:
                path = os.path.join(d, f"r.{cx >> 5}.{cz >> 5}.mca")
                if not os.path.exists(path):
                    continue
                with open(path, "r+b") as f:
                    i = 4 * ((cx & 31) + (cz & 31) * 32)
                    f.seek(i)
                    if struct.unpack(">I", f.read(4))[0]:
                        f.seek(i)
                        f.write(bytes(4))       # location entry
                        f.seek(4096 + i)
                        f.write(bytes(4))       # timestamp entry
                        removed += sub == "region"
        self._world = None
        if was_running:
            self.start()
        return {"chunks_regenerated": removed, "chunks_requested": len(chunks),
                "note": "builds inside these chunks are gone; their undo entries no longer apply"}

    # -- region reading helpers ---------------------------------------------
    def read_cells(self, x1, y1, z1, x2, y2, z2, dimension="minecraft:overworld", include_air=True):
        """World contents of a box (absolute coords) as cells, with block entity data. Loads + flushes first."""
        dimension = blocks.ns(dimension)
        added = self.load_area(dimension, min(x1, x2), min(z1, z2), max(x1, x2), max(z1, z2))
        try:
            self.flush()
        finally:
            self.release(dimension, added)
        xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
        positions = [(x, y, z) for x in range(xa, xb + 1) for y in range(ya, yb + 1) for z in range(za, zb + 1)]
        cells = self.snapshot(positions, dimension)
        if not include_air:
            cells = {p: v for p, v in cells.items() if v[0] not in ("minecraft:air", "minecraft:cave_air", "minecraft:void_air")}
        return cells


def _overlaps(a: Placement, b: Placement) -> bool:
    return a.dimension == b.dimension and all(a.min[i] <= b.max[i] and b.min[i] <= a.max[i] for i in range(3))
