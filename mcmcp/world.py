"""Read blocks straight out of a Java Edition world save (Anvil region files).

The server only writes chunks to disk on save, so callers run `save-all flush`
over RCON before reading. Handles both the 26.x folder layout
(world/dimensions/<ns>/<id>/region) and the legacy one (world/region, DIM-1, DIM1),
and both palette styles (26.x `id`/`properties`, legacy `Name`/`Properties`).
"""

from __future__ import annotations

import gzip
import os
import struct
import time
import zlib
from dataclasses import dataclass, field

from . import nbt

AIR = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}

LEGACY_DIMS = {
    "minecraft:overworld": "region",
    "minecraft:the_nether": os.path.join("DIM-1", "region"),
    "minecraft:the_end": os.path.join("DIM1", "region"),
}


def normalize_id(name: str) -> str:
    return name if ":" in name else f"minecraft:{name}"


def state_string(entry) -> str:
    """Palette entry -> 'minecraft:oak_stairs[facing=east,half=top]'."""
    if isinstance(entry, str):
        return entry
    name = entry.get("id") or entry.get("Name") or "minecraft:air"
    props = entry.get("properties") or entry.get("Properties") or {}
    if not props:
        return name
    return name + "[" + ",".join(f"{k}={v}" for k, v in sorted(props.items())) + "]"


def block_name(state: str) -> str:
    return state.split("[", 1)[0]


@dataclass
class Section:
    palette: list[str]
    data: list[int]
    biome_palette: list[str]
    biome_data: list[int]

    @staticmethod
    def _unpack(data: list[int], palette_len: int, count: int, min_bits: int) -> list[int]:
        if palette_len <= 1 or not data:
            return [0] * count
        bits = max(min_bits, (palette_len - 1).bit_length())
        per_long = 64 // bits
        mask = (1 << bits) - 1
        out = []
        for word in data:
            word &= 0xFFFFFFFFFFFFFFFF
            for j in range(per_long):
                out.append((word >> (j * bits)) & mask)
                if len(out) == count:
                    return out
        return out + [0] * (count - len(out))

    _indices: list[int] | None = field(default=None, repr=False)

    def index_at(self, lx: int, ly: int, lz: int) -> int:
        if self._indices is None:
            self._indices = self._unpack(self.data, len(self.palette), 4096, 4)
        return self._indices[(ly << 8) | (lz << 4) | lx]

    def block(self, lx: int, ly: int, lz: int) -> str:
        if len(self.palette) == 1:
            return self.palette[0]
        return self.palette[self.index_at(lx, ly, lz)]

    def biome(self, lx: int, ly: int, lz: int) -> str:
        if not self.biome_palette:
            return "unknown"
        if len(self.biome_palette) == 1:
            return self.biome_palette[0]
        idx = self._unpack(self.biome_data, len(self.biome_palette), 64, 1)
        return self.biome_palette[idx[((ly >> 2) << 4) | ((lz >> 2) << 2) | (lx >> 2)]]


@dataclass
class Chunk:
    cx: int
    cz: int
    sections: dict[int, Section]
    block_entities: dict[tuple[int, int, int], dict]
    min_section: int
    max_section: int
    status: str

    def block(self, x: int, y: int, z: int) -> str:
        sec = self.sections.get(y >> 4)
        if sec is None:
            return "minecraft:air"
        return sec.block(x & 15, y & 15, z & 15)


class World:
    def __init__(self, world_dir: str):
        self.dir = world_dir
        self._cache: dict[tuple[str, int, int], tuple[float, Chunk | None]] = {}
        self._mtimes: dict[str, tuple[float, float]] = {}  # path -> (checked_at, mtime)

    def _mtime(self, path: str) -> float:
        # stat() per block is slow on big scans; re-check each region file at most every 0.5s
        now = time.monotonic()
        hit = self._mtimes.get(path)
        if hit and now - hit[0] < 0.5:
            return hit[1]
        m = os.path.getmtime(path)
        self._mtimes[path] = (now, m)
        return m

    def invalidate(self):
        """Forget cached file timestamps (call right after the server saved)."""
        self._mtimes.clear()

    # -- paths -------------------------------------------------------------
    def region_dir(self, dimension: str = "minecraft:overworld") -> str:
        dimension = normalize_id(dimension)
        ns, path = dimension.split(":", 1)
        modern = os.path.join(self.dir, "dimensions", ns, path, "region")
        if os.path.isdir(modern) or os.path.isdir(os.path.join(self.dir, "dimensions")):
            return modern
        if dimension in LEGACY_DIMS:
            return os.path.join(self.dir, LEGACY_DIMS[dimension])
        return os.path.join(self.dir, "dimensions", ns, path, "region")

    def dimensions(self) -> list[str]:
        out = []
        root = os.path.join(self.dir, "dimensions")
        if os.path.isdir(root):
            for ns in sorted(os.listdir(root)):
                for d in sorted(os.listdir(os.path.join(root, ns))):
                    out.append(f"{ns}:{d}")
        else:
            out = [k for k, v in LEGACY_DIMS.items() if os.path.isdir(os.path.join(self.dir, v))]
        return out

    # -- chunk loading -----------------------------------------------------
    def chunk(self, cx: int, cz: int, dimension: str = "minecraft:overworld") -> Chunk | None:
        rdir = self.region_dir(dimension)
        rpath = os.path.join(rdir, f"r.{cx >> 5}.{cz >> 5}.mca")
        try:
            mtime = self._mtime(rpath)
        except OSError:
            return None
        key = (rdir, cx, cz)
        hit = self._cache.get(key)
        if hit and hit[0] == mtime:
            return hit[1]
        ch = self._load_chunk(rpath, rdir, cx, cz)
        if len(self._cache) > 2048:
            self._cache.clear()
        self._cache[key] = (mtime, ch)
        return ch

    def _load_chunk(self, rpath: str, rdir: str, cx: int, cz: int) -> Chunk | None:
        with open(rpath, "rb") as f:
            idx = 4 * ((cx & 31) + (cz & 31) * 32)
            f.seek(idx)
            (loc,) = struct.unpack(">I", f.read(4))
            if loc == 0:
                return None
            f.seek((loc >> 8) * 4096)
            length, ctype = struct.unpack(">IB", f.read(5))
            raw = f.read(length - 1)
        if ctype & 0x80:  # oversized chunk stored in its own .mcc file
            with open(os.path.join(rdir, f"c.{cx}.{cz}.mcc"), "rb") as f:
                raw = f.read()
            ctype &= 0x7F
        if ctype == 1:
            raw = gzip.decompress(raw)
        elif ctype == 2:
            raw = zlib.decompress(raw)
        elif ctype == 4:
            raise RuntimeError("chunk uses LZ4 compression (region-file-compression=lz4); set it back to deflate")
        root = nbt.read(raw)
        if "Level" in root:  # pre-1.18 wrapper
            root = root["Level"]
        sections: dict[int, Section] = {}
        ys = []
        for s in root.get("sections", root.get("Sections", [])):
            y = s["Y"]
            ys.append(y)
            bs = s.get("block_states")
            if not bs:
                continue
            bio = s.get("biomes", {})
            sections[y] = Section(
                palette=[state_string(e) for e in bs.get("palette", ["minecraft:air"])],
                data=bs.get("data", []),
                biome_palette=list(bio.get("palette", [])),
                biome_data=bio.get("data", []),
            )
        bes = {}
        for be in root.get("block_entities", []):
            bes[(be.get("x"), be.get("y"), be.get("z"))] = be
        y0 = root.get("yPos", min(ys) if ys else -4)
        return Chunk(cx, cz, sections, bes, y0, max(ys) if ys else y0 + 23, root.get("Status", "?"))

    # -- block queries -----------------------------------------------------
    def block(self, x: int, y: int, z: int, dimension: str = "minecraft:overworld") -> str | None:
        ch = self.chunk(x >> 4, z >> 4, dimension)
        if ch is None:
            return None
        return ch.block(x, y, z)

    def block_entity(self, x: int, y: int, z: int, dimension: str = "minecraft:overworld") -> dict | None:
        ch = self.chunk(x >> 4, z >> 4, dimension)
        return ch.block_entities.get((x, y, z)) if ch else None

    def biome(self, x: int, y: int, z: int, dimension: str = "minecraft:overworld") -> str | None:
        ch = self.chunk(x >> 4, z >> 4, dimension)
        if ch is None:
            return None
        sec = ch.sections.get(y >> 4)
        return sec.biome(x & 15, y & 15, z & 15) if sec else None

    def iter_region(self, x1, y1, z1, x2, y2, z2, dimension="minecraft:overworld"):
        """Yield (x, y, z, state) for every block in the box. state is None in ungenerated chunks."""
        xa, xb = sorted((x1, x2))
        ya, yb = sorted((y1, y2))
        za, zb = sorted((z1, z2))
        for cx in range(xa >> 4, (xb >> 4) + 1):
            for cz in range(za >> 4, (zb >> 4) + 1):
                ch = self.chunk(cx, cz, dimension)
                for x in range(max(xa, cx * 16), min(xb, cx * 16 + 15) + 1):
                    for z in range(max(za, cz * 16), min(zb, cz * 16 + 15) + 1):
                        for y in range(ya, yb + 1):
                            yield x, y, z, (ch.block(x, y, z) if ch else None)

    def top_block(self, x: int, z: int, dimension="minecraft:overworld", ignore: set[str] = AIR) -> tuple[int, str] | None:
        """Highest block at (x, z) whose id is not in `ignore`."""
        ch = self.chunk(x >> 4, z >> 4, dimension)
        if ch is None:
            return None
        for sy in sorted(ch.sections, reverse=True):
            sec = ch.sections[sy]
            if len(sec.palette) == 1 and block_name(sec.palette[0]) in ignore:
                continue
            for ly in range(15, -1, -1):
                st = sec.block(x & 15, ly, z & 15)
                if block_name(st) not in ignore:
                    return sy * 16 + ly, st
        return None
