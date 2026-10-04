"""MCP server: plan whole buildings as short Python scripts and drop them into a
running Minecraft Java 26.3 server in one placement, with undo.

Run with:  .venv/Scripts/python -m mcmcp.server
"""

from __future__ import annotations

import contextlib
import io
import json
import math
import os
import re
import traceback
from collections import Counter

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.utilities.types import Image

from . import blocks, canvas as canvas_mod
from .canvas import COLORS, DIRS, Canvas, left_of, right_of
from .blocks import OPPOSITE, BlockError
from .engine import NAMESPACE, Engine, EngineError
from .world import AIR, block_name

mcp = MCPServer("minecraft", instructions="""
Edit a Minecraft Java 26.3 world running on a local server. Build whole structures, not block by block:
1. server_status (start_server if needed); get_players to find where the player is.
2. find_build_site / surface_map to pick ground; note the floor y it reports.
3. Write the entire structure as ONE `build` script (functions for repeated rooms/bays, b.at(...) to
   place and rotate them). Run it with dry_run=True first to check size and palette.
4. build for real, then render_build (and cutaway renders of each floor) to check the result visually.
5. Fix with another build, or undo and rebuild. Every build/edit is undoable; regenerate_chunks resets terrain.
Blocks are validated against the 26.3 catalog (block_info to look up ids/properties).
""".strip())
engine = Engine()

MAX_CELLS = 4_000_000

LEAVES_ETC = AIR | {"minecraft:water", "minecraft:short_grass", "minecraft:tall_grass", "minecraft:snow",
                    "minecraft:fern", "minecraft:large_fern", "minecraft:dead_bush", "minecraft:seagrass",
                    "minecraft:tall_seagrass", "minecraft:kelp", "minecraft:kelp_plant", "minecraft:leaf_litter",
                    "minecraft:short_dry_grass", "minecraft:tall_dry_grass", "minecraft:bush", "minecraft:firefly_bush"}


def _ok(obj) -> str:
    return json.dumps(obj, indent=1, default=str)


def _err(e: Exception) -> str:
    return f"ERROR: {e}"


# ---------------------------------------------------------------------------
# server lifecycle
# ---------------------------------------------------------------------------

@mcp.tool()
def server_status() -> str:
    """Is the Minecraft server up? Shows version, players online, world folder and where the build server lives."""
    info = {"server_dir": engine.server_dir, "world_dir": engine.world_dir, "running": engine.is_running()}
    if info["running"]:
        info["version"] = re.sub(r"(?<=\S)(?=(name|data|series|protocol|build_time|pack_resource|pack_data|stable) =)", "; ",
                                 engine.cmd("version"))
        info["players"] = engine.cmd("list")
        info["dimensions"] = engine.world.dimensions()
    p = engine.props
    info["join_address"] = f"{p.get('server-ip') or 'localhost'}:{p.get('server-port', '25565')}"
    return _ok(info)


@mcp.tool()
def start_server(memory_gb: int = 4) -> str:
    """Start the local Minecraft server (Java 26.3, creative, RCON on localhost). Players join at localhost:25565."""
    try:
        return engine.start(memory_gb)
    except EngineError as e:
        return _err(e) + "\n" + engine.log_tail(20)


@mcp.tool()
def stop_server() -> str:
    """Save and stop the server."""
    return engine.stop()


@mcp.tool()
def server_log(lines: int = 40) -> str:
    """Last lines of the server log (chat, errors, joins)."""
    return engine.log_tail(lines)


@mcp.tool()
def run_commands(commands: list[str], dimension: str = "minecraft:overworld") -> str:
    """Run raw Minecraft commands (no leading slash needed) and return each response.
    For anything vanilla: time set day, weather clear, gamemode creative <player>, tp, give, gamerule,
    summon, effect, fillbiome, locate, etc. Use the build tools for construction (undoable, no size limits)."""
    out = []
    for c in commands:
        try:
            out.append(f"> {c}\n{engine.cmd(c, dimension)}")
        except Exception as e:
            out.append(f"> {c}\n{_err(e)}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# building
# ---------------------------------------------------------------------------

BUILD_DOC = """
Plan a structure as a short Python script, then place ALL of it in one go (one structure template,
one command; 100k+ blocks take a second). Every build is undoable with `undo`.

Coordinates in the script are LOCAL to the origin (x, y, z) you pass: +x east, +y up, +z south.
`rotation` (0-3 quarter turns clockwise) turns the whole build, including block states.

Script globals:
  b                     the builder (a View). Nested views: v = b.at(x, y, z, rot) -> own origin/rotation.
  ground(lx, lz)        local y of the terrain surface at local (lx, lz) (ignores plants/leaves/water surface)
  world_block(lx,ly,lz) current world block at a local position (state string) or None
  rng / random          seeded random.Random; math; DIRS, COLORS, OPPOSITE, right_of(d), left_of(d)
  print(...)            output is returned to you

Block arguments: 'stone_bricks', 'oak_stairs[facing=east,half=top]', a list (random pick) or a dict of
weights {'stone_bricks': 6, 'cracked_stone_bricks': 2, 'mossy_stone_bricks': 1}. Invalid ids/properties
fail fast with suggestions. Directions are local: 'north' (-z), 'south' (+z), 'east' (+x), 'west' (-x).

Shapes:      b.set(x,y,z, block, nbt=None)  b.box(x1,y1,z1, x2,y2,z2, block, hollow=False)  b.clear(box)
             b.room(box, wall, floor=None, ceiling=None)   (shell + interior cleared to air)
             b.walls(box, block)  b.floor(x1,z1,x2,z2,y, block)  b.frame(box, block)  (edges; logs auto-axis)
             b.line(x1,y1,z1,x2,y2,z2, block)  b.sphere(cx,cy,cz,r, block, hollow=False)
             b.ellipsoid(cx,cy,cz,rx,ry,rz, block, hollow, half='top'|'bottom')  b.dome(cx,cy,cz,r, block)
             b.cylinder(cx,y,cz,r,height, block, hollow=False, rz=None)  b.pyramid(x1,z1,x2,z2,y, block)
             b.replace(old_id, new, [box])  b.mirror_x(x_plane)  b.unset(x,y,z)  b.get(x,y,z)
Architecture: b.door(x,y,z, facing, 'oak_door', hinge)  (facing = direction you face walking in)
             b.double_door(...)  b.window(box, 'glass_pane')  b.ladder(x,y,z,height,facing)
             b.stairs_run(x,y,z, direction, length, 'stone_brick_stairs', width=1, support=None)
             b.gable_roof(x1,z1,x2,z2,y, stairs, ridge='x'|'z', overhang=1, gable=wall_block, ridge_block=None)
             b.hip_roof(x1,z1,x2,z2,y, stairs, overhang=1, top=None, fill=None)  (corners auto-shape)
             b.flat_roof(x1,z1,x2,z2,y, block, rim=None)  b.foundation(x1,z1,x2,z2,y, block, depth=8)
Furniture:   b.bed(x,y,z, facing, color)  (foot at x,y,z, head toward facing)
             b.chair(x,y,z, facing, 'oak_stairs')  (facing = where the sitter looks)
             b.table(x,y,z)  b.long_table(x1,z1,x2,z2,y,'spruce_slab')  b.sofa(x,y,z, facing, length, seat, arm)
             b.bookshelves(box)  b.lamp(x,y,z, 'lantern', hanging=False)  b.wall_torch(x,y,z, facing)
             b.chest(x,y,z, facing, items=[('bread',16)], double=False)  b.barrel(x,y,z, facing, items)
             b.kitchen(x,y,z, facing, length)  b.carpet(x1,z1,x2,z2,y, color, border=None)  b.plant(x,y,z,'potted_fern')
             b.sign(x,y,z, ['line1','line2'], facing, wall=True)  b.painting(x,y,z, facing, variant)
Entities/commands (run after placement): b.summon('villager', x,y,z, '{NoAI:1b}')  b.command('say hi {x} {y} {z}', x,y,z)
Prefab:      b.house(x,y,z, width=9, depth=7, floors=1, wall, frame, floor_block, roof, glass, door, furnished=True)
             -> furnished timber-frame house, door on the south (+z) side; returns the roof's top y.

Pattern for big builds: write functions that take a view and build a module (room, tower, facade bay),
then stamp them: for i in range(4): bay(b.at(i*8, 0, 0)).   Rotate wings with b.at(x,y,z, rot=1).
Plan the whole thing, then place once. Use dry_run=True to check size/palette without touching the world.
"""


def _exec_script(script: str, origin, dimension: str, seed: int | None, rotation: int):
    c = Canvas(seed)
    root = canvas_mod.View(c, 0, 0, 0, rotation)
    ox, oy, oz = origin
    flushed = {"done": False}

    def _ensure_flush():
        if not flushed["done"]:
            engine.flush()
            flushed["done"] = True

    def ground(lx: int, lz: int) -> int:
        _ensure_flush()
        ax, _, az = root.pos(lx, 0, lz)
        ax, az = ax + ox, az + oz
        w = engine.world
        ch = w.chunk(ax >> 4, az >> 4, dimension)
        if ch is None:
            engine.load_area(dimension, ax, az, ax, az)
            engine.flush()
        top = w.top_block(ax, az, dimension, ignore=_GroundIgnore())
        return (top[0] if top else oy) - oy

    def world_block(lx, ly, lz):
        _ensure_flush()
        ax, ay, az = root.pos(lx, ly, lz)
        return engine.world.block(ax + ox, ay + oy, az + oz, dimension)

    out = io.StringIO()
    g = {
        "b": root, "ground": ground, "world_block": world_block, "rng": c.rng, "random": c.rng, "math": math,
        "DIRS": DIRS, "COLORS": COLORS, "OPPOSITE": OPPOSITE, "right_of": right_of, "left_of": left_of,
        "__builtins__": __builtins__,
    }
    with contextlib.redirect_stdout(out):
        exec(compile(script, "<build script>", "exec"), g)
    return c, out.getvalue()


class _GroundIgnore:
    def __contains__(self, name: str) -> bool:
        return name in LEAVES_ETC or name.endswith("_leaves") or name.endswith("_sapling") or \
            name.endswith("flower") or name.endswith("_tulip") or name in ("minecraft:poppy", "minecraft:dandelion",
                                                                            "minecraft:vine", "minecraft:glow_lichen")


def _summary(c: Canvas, origin, rotation: int) -> dict:
    bb = c.bbox()
    if not bb:
        return {"blocks": 0}
    (x1, y1, z1), (x2, y2, z2) = bb
    ox, oy, oz = origin
    pal = Counter(block_name(s) for s, _ in c.voxels.values())
    return {"blocks": len(c.voxels), "min": (x1 + ox, y1 + oy, z1 + oz), "max": (x2 + ox, y2 + oy, z2 + oz),
            "size": (x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1), "entities": len(c.entities),
            "palette_top": dict(pal.most_common(15)), "distinct_blocks": len(pal)}


@mcp.tool(description=BUILD_DOC)
def build(script: str, x: int, y: int, z: int, name: str = "build", rotation: int = 0,
          dimension: str = "minecraft:overworld", dry_run: bool = False, seed: int | None = None) -> str:
    try:
        c, printed = _exec_script(script, (x, y, z), blocks.ns(dimension), seed, rotation)
    except BlockError as e:
        return _err(e)
    except Exception:
        return "ERROR in build script:\n" + traceback.format_exc(limit=4)
    if len(c.voxels) > MAX_CELLS:
        return _err(f"build has {len(c.voxels)} blocks; split it (max {MAX_CELLS} per build)")
    summary = _summary(c, (x, y, z), rotation)
    if printed:
        summary["printed"] = printed[-4000:]
    if dry_run:
        summary["dry_run"] = True
        return _ok(summary)
    try:
        res = engine.place_canvas(c, (x, y, z), name, dimension)
    except (EngineError, BlockError) as e:
        return _err(e)
    res["palette_top"] = summary["palette_top"]
    if printed:
        res["printed"] = summary["printed"]
    return _ok(res)


@mcp.tool()
def undo(build_id: str | None = None) -> str:
    """Restore the world to how it was before a build (default: the most recent one not yet undone)."""
    try:
        return _ok(engine.undo(build_id))
    except EngineError as e:
        return _err(e)


@mcp.tool()
def list_builds(limit: int = 20, include_undone: bool = False) -> str:
    """Recent builds with ids, bounding boxes and block counts."""
    items = [p.as_dict() for p in engine.history() if include_undone or not p.undone]
    return _ok(items[-limit:])


@mcp.tool()
def edit_region(operation: str, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int,
                block: str = "minecraft:stone", replace_filter: str | None = None,
                dimension: str = "minecraft:overworld") -> str:
    """Quick undoable box edits in absolute coordinates, any size.
    operation: 'fill' (solid), 'clear' (air), 'hollow' (shell, interior air), 'walls', 'outline' (edges),
               'replace' (blocks whose id equals replace_filter become `block`; filter may be a comma list),
               'flatten' (fill layer y1 with `block` and clear everything above it up to y2)."""
    dimension = blocks.ns(dimension)
    try:
        c = Canvas()
        b = c.view()
        xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
        lx, ly, lz = xb - xa, yb - ya, zb - za
        if operation == "fill":
            b.box(0, 0, 0, lx, ly, lz, block)
        elif operation == "clear":
            b.clear(0, 0, 0, lx, ly, lz)
        elif operation == "hollow":
            b.room(0, 0, 0, lx, ly, lz, block)
        elif operation == "walls":
            b.walls(0, 0, 0, lx, ly, lz, block)
        elif operation == "outline":
            b.frame(0, 0, 0, lx, ly, lz, block)
        elif operation == "flatten":
            b.box(0, 0, 0, lx, 0, lz, block)
            if ly:
                b.clear(0, 1, 0, lx, ly, lz)
        elif operation == "replace":
            if not replace_filter:
                return _err("replace needs replace_filter")
            wanted = {blocks.ns(f) for f in replace_filter.split(",")}
            new = blocks.normalize(block)
            cells = engine.read_cells(xa, ya, za, xb, yb, zb, dimension)
            for (ax, ay, az), (st, _) in cells.items():
                if block_name(st) in wanted:
                    c.voxels[(ax - xa, ay - ya, az - za)] = (new, None)
        else:
            return _err(f"unknown operation {operation}")
        return _ok(engine.place_canvas(c, (xa, ya, za), f"{operation} {block}", dimension))
    except (EngineError, BlockError) as e:
        return _err(e)


@mcp.tool()
def copy_region(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, dest_x: int, dest_y: int, dest_z: int,
                rotation: int = 0, move: bool = False, include_air: bool = True,
                dimension: str = "minecraft:overworld", dest_dimension: str | None = None) -> str:
    """Copy (or move) a box to a new place, any size, keeping chest contents/signs. dest = new min corner.
    rotation turns the copy clockwise in quarter turns. Undoable."""
    dimension = blocks.ns(dimension)
    dest_dimension = blocks.ns(dest_dimension or dimension)
    try:
        cells = engine.read_cells(x1, y1, z1, x2, y2, z2, dimension, include_air=include_air)
        xa, ya, za = min(x1, x2), min(y1, y2), min(z1, z2)
        c = Canvas()
        v = canvas_mod.View(c, 0, 0, 0, rotation)
        for (ax, ay, az), (st, be) in cells.items():
            c.voxels[v.pos(ax - xa, ay - ya, az - za)] = (blocks.rotate(st, rotation), be)
        bb = c.bbox()
        shift = (-bb[0][0], -bb[0][1], -bb[0][2])
        c.voxels = {(p[0] + shift[0], p[1] + shift[1], p[2] + shift[2]): val for p, val in c.voxels.items()}
        res = engine.place_canvas(c, (dest_x, dest_y, dest_z), "copy", dest_dimension)
        if move:
            m = Canvas()
            src = set(cells)
            dst = {(p[0] + dest_x, p[1] + dest_y, p[2] + dest_z) for p in c.voxels} if dest_dimension == dimension else set()
            for (ax, ay, az) in src - dst:
                m.voxels[(ax - xa, ay - ya, az - za)] = ("minecraft:air", None)
            if m.voxels:
                res["source_cleared"] = engine.place_canvas(m, (xa, ya, za), "move-clear", dimension)["id"]
        return _ok(res)
    except (EngineError, BlockError) as e:
        return _err(e)


@mcp.tool()
def save_template(name: str, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, include_air: bool = False,
                  dimension: str = "minecraft:overworld") -> str:
    """Save a region as a reusable template 'mcp:<name>' (e.g. a finished furnished room) to stamp elsewhere."""
    try:
        cells = engine.read_cells(x1, y1, z1, x2, y2, z2, dimension, include_air=include_air)
        if not cells:
            return _err("region is empty")
        safe = re.sub(r"[^a-z0-9_./-]", "_", name.lower())
        mn, size = engine.write_template(safe, cells)
        return _ok({"template": f"{NAMESPACE}:{safe}", "size": size, "blocks": len(cells)})
    except EngineError as e:
        return _err(e)


@mcp.tool()
def place_template(template: str, x: int, y: int, z: int, rotation: int = 0,
                   dimension: str = "minecraft:overworld") -> str:
    """Stamp a saved template (from save_template, a previous build id's 'mcp:b_<id>', or import_schematic)
    with its min corner at x,y,z, rotated clockwise in quarter turns. Undoable."""
    try:
        if ":" not in template:
            template = f"{NAMESPACE}:{template}"
        cells = engine.read_template(template)
        c = Canvas()
        v = canvas_mod.View(c, 0, 0, 0, rotation)
        for (lx, ly, lz), (st, be) in cells.items():
            c.voxels[v.pos(lx, ly, lz)] = (blocks.rotate(st, rotation), be)
        bb = c.bbox()
        c.voxels = {(p[0] - bb[0][0], p[1] - bb[0][1], p[2] - bb[0][2]): val for p, val in c.voxels.items()}
        return _ok(engine.place_canvas(c, (x, y, z), f"template {template}", dimension))
    except (EngineError, BlockError) as e:
        return _err(e)


@mcp.tool()
def list_templates() -> str:
    """Templates saved under mcp: (builds are b_<id>, undo snapshots u_<id>)."""
    d = engine.structure_dir()
    names = sorted(f[:-4] for f in os.listdir(d) if f.endswith(".nbt"))
    saved = [n for n in names if not n.startswith(("b_", "u_"))]
    return _ok({"saved": saved, "build_templates": [n for n in names if n.startswith("b_")][-20:]})


@mcp.tool()
def import_schematic(path: str, x: int, y: int, z: int, rotation: int = 0, include_air: bool = False,
                     dimension: str = "minecraft:overworld") -> str:
    """Place a Sponge .schem (WorldEdit) or vanilla structure .nbt file from disk with its min corner at x,y,z. Undoable."""
    from .schematic import load_schematic
    try:
        cells = load_schematic(path, include_air)
        c = Canvas()
        v = canvas_mod.View(c, 0, 0, 0, rotation)
        unknown = Counter()
        for (lx, ly, lz), (st, be) in cells.items():
            try:
                st = blocks.normalize(st)
            except BlockError:
                unknown[block_name(st)] += 1
                continue
            c.voxels[v.pos(lx, ly, lz)] = (blocks.rotate(st, rotation), be)
        bb = c.bbox()
        c.voxels = {(p[0] - bb[0][0], p[1] - bb[0][1], p[2] - bb[0][2]): val for p, val in c.voxels.items()}
        res = engine.place_canvas(c, (x, y, z), f"schematic {os.path.basename(path)}", dimension)
        if unknown:
            res["skipped_unknown_blocks"] = dict(unknown.most_common(10))
        return _ok(res)
    except (EngineError, OSError, ValueError, KeyError) as e:
        return _err(e)


@mcp.tool()
def place_vanilla(kind: str, id: str, x: int, y: int, z: int, dimension: str = "minecraft:overworld") -> str:
    """Generate a vanilla worldgen piece: kind='feature' (trees, ores, rocks: e.g. minecraft:fancy_oak,
    minecraft:mega_spruce) or 'structure' (minecraft:village_plains, minecraft:pillager_outpost...).
    NOT undoable. Use list_registry('feature'|'structure') for ids."""
    if kind not in ("feature", "structure"):
        return _err("kind must be feature or structure")
    added = engine.load_area(blocks.ns(dimension), x - 64, z - 64, x + 64, z + 64)
    try:
        return engine.cmd(f"place {kind} {blocks.ns(id)} {x} {y} {z}", dimension)
    finally:
        engine.release(blocks.ns(dimension), added)


@mcp.tool()
def regenerate_chunks(x1: int, z1: int, x2: int, z2: int, dimension: str = "minecraft:overworld") -> str:
    """Reset an area to freshly generated natural terrain (whole 16x16 chunk columns covering the box).
    Restarts the server (~10 s; players get disconnected). NOT undoable."""
    try:
        return _ok(engine.regenerate_chunks(dimension, x1, z1, x2, z2))
    except EngineError as e:
        return _err(e)


# ---------------------------------------------------------------------------
# reading the world
# ---------------------------------------------------------------------------

@mcp.tool()
def get_block(x: int, y: int, z: int, dimension: str = "minecraft:overworld") -> str:
    """Exact block state (and block entity data, e.g. chest contents) at a position."""
    try:
        cells = engine.read_cells(x, y, z, x, y, z, dimension)
        st, be = cells[(x, y, z)]
        from .nbt import to_snbt
        out = {"block": st, "biome": engine.world.biome(x, y, z, blocks.ns(dimension))}
        if be is not None:
            out["nbt"] = to_snbt(be)[:3000]
        return _ok(out)
    except EngineError as e:
        return _err(e)


_CHARS = "#@%&$ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789*+=?!<>^~"


@mcp.tool()
def scan_region(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, layers: bool = True,
                dimension: str = "minecraft:overworld") -> str:
    """Inspect a box: block counts, plus (layers=True, box <= 48x48 footprint, <= 40 tall) an ASCII map per
    y-level (rows = z north->south, columns = x west->east, '.' = air) with a legend."""
    try:
        cells = engine.read_cells(x1, y1, z1, x2, y2, z2, dimension)
    except EngineError as e:
        return _err(e)
    counts = Counter(block_name(s) for s, _ in cells.values())
    out = [f"box ({min(x1,x2)},{min(y1,y2)},{min(z1,z2)})..({max(x1,x2)},{max(y1,y2)},{max(z1,z2)}), {len(cells)} blocks",
           "counts: " + ", ".join(f"{k.replace('minecraft:', '')}={v}" for k, v in counts.most_common(25))]
    xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
    if layers and xb - xa < 48 and zb - za < 48 and yb - ya < 40:
        legend: dict[str, str] = {}
        for name, _ in counts.most_common():
            if name not in AIR:
                legend[name] = _CHARS[len(legend)] if len(legend) < len(_CHARS) else "?"
        for y in range(yb, ya - 1, -1):
            rows = []
            for z in range(za, zb + 1):
                rows.append("".join("." if block_name(cells[(x, y, z)][0]) in AIR else legend[block_name(cells[(x, y, z)][0])]
                                    for x in range(xa, xb + 1)))
            if any(set(r) != {"."} for r in rows):
                out.append(f"y={y}\n" + "\n".join(rows))
        out.append("legend: " + ", ".join(f"{c}={n.replace('minecraft:', '')}" for n, c in legend.items()))
    return "\n".join(out)


@mcp.tool()
def surface_map(x1: int, z1: int, x2: int, z2: int, step: int = 1, dimension: str = "minecraft:overworld") -> str:
    """Terrain overview for picking build sites: height of the surface at each column (relative to the lowest
    one) and what the top block is. Max 96x96 cells after `step` sampling. Also reports flatness stats."""
    dimension = blocks.ns(dimension)
    xa, xb = sorted((x1, x2)); za, zb = sorted((z1, z2))
    if (xb - xa) // step > 96 or (zb - za) // step > 96:
        return _err("too large; increase step")
    try:
        added = engine.load_area(dimension, xa, za, xb, zb)
        try:
            engine.flush()
        finally:
            engine.release(dimension, added)
    except EngineError as e:
        return _err(e)
    ign = _GroundIgnore()
    grid = []
    tops = Counter()
    for z in range(za, zb + 1, step):
        row = []
        for x in range(xa, xb + 1, step):
            t = engine.world.top_block(x, z, dimension, ignore=ign)
            row.append(t)
            if t:
                tops[block_name(t[1])] += 1
        grid.append(row)
    hs = [t[0] for r in grid for t in r if t]
    if not hs:
        return _err("no terrain found")
    lo = min(hs)
    water = sum(1 for r in grid for t in r if t and engine.world.block(xa, t[0] + 1, za, dimension) == "minecraft:water")
    lines = [f"surface y range {lo}..{max(hs)} (mean {sum(hs)/len(hs):.1f}); cells show height-{lo} (base36)",
             "top blocks: " + ", ".join(f"{k.replace('minecraft:', '')}={v}" for k, v in tops.most_common(8)),
             f"columns x {xa}..{xb} step {step}; rows z {za}..{zb}"]
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    for r in grid:
        lines.append("".join(digits[min(t[0] - lo, 35)] if t else " " for t in r))
    return "\n".join(lines)


@mcp.tool()
def find_build_site(center_x: int, center_z: int, width: int, depth: int, search_radius: int = 96,
                    dimension: str = "minecraft:overworld") -> str:
    """Find the flattest dry patch of width x depth near a point. Returns its corner, ground y and how much
    terrain varies (so you can decide to add a foundation or flatten)."""
    dimension = blocks.ns(dimension)
    xa, za = center_x - search_radius, center_z - search_radius
    xb, zb = center_x + search_radius + width, center_z + search_radius + depth
    try:
        added = engine.load_area(dimension, xa, za, xb, zb, timeout=120)
        try:
            engine.flush()
        finally:
            engine.release(dimension, added)
    except EngineError as e:
        return _err(e)
    ign = _GroundIgnore()
    step = 2
    H = {}
    for x in range(xa, xb + 1, step):
        for z in range(za, zb + 1, step):
            t = engine.world.top_block(x, z, dimension, ignore=ign)
            if t:
                wet = block_name(t[1]) in ("minecraft:water", "minecraft:lava", "minecraft:ice")
                H[(x, z)] = (t[0], wet or engine.world.block(x, t[0] + 1, z, dimension) == "minecraft:water")
    best = None
    for x in range(xa, xb - width + 1, 4):
        for z in range(za, zb - depth + 1, 4):
            pts = [H.get((px, pz)) for px in range(x - x % step, x + width, step) for pz in range(z - z % step, z + depth, step)]
            pts = [p for p in pts if p]
            if not pts or any(p[1] for p in pts):
                continue
            hs = sorted(p[0] for p in pts)
            spread = hs[-1] - hs[0]
            dist = math.hypot(x + width / 2 - center_x, z + depth / 2 - center_z)
            score = spread * 10 + dist * 0.05
            if best is None or score < best[0]:
                best = (score, x, z, hs[len(hs) // 2], spread, hs[0], hs[-1])
    if not best:
        return _err("no dry site found; widen search_radius")
    _, x, z, med, spread, lo, hi = best
    return _ok({"x": x, "z": z, "ground_y": med, "build_floor_y": med + 1, "height_spread": spread,
                "min_y": lo, "max_y": hi, "note": "use foundation() if spread > 1"})


@mcp.tool()
def get_players() -> str:
    """Online players with position, facing and dimension (useful to build where the player is looking)."""
    raw = engine.cmd("list")
    names = [n.strip() for n in raw.split(":", 1)[-1].split(",") if n.strip()]
    out = []
    for n in names:
        def num(path):
            r = engine.cmd(f"data get entity {n} {path}")
            return [float(v) for v in re.findall(r"(-?\d+(?:\.\d+)?)[dfF]", r)]
        pos, rot = num("Pos"), num("Rotation")
        dim = re.findall(r'"([^"]+)"', engine.cmd(f"data get entity {n} Dimension"))
        yaw = rot[0] if rot else 0
        facing = ["south", "west", "north", "east"][int(((yaw % 360) + 45) // 90) % 4]
        out.append({"name": n, "pos": [round(v, 2) for v in pos], "block": [math.floor(v) for v in pos],
                    "yaw": yaw, "pitch": rot[1] if len(rot) > 1 else 0, "facing": facing,
                    "dimension": dim[0] if dim else "minecraft:overworld"})
    return _ok(out)


@mcp.tool()
def block_info(query: str) -> str:
    """Look up blocks: exact id -> its properties and allowed values; otherwise a search ('lantern', 'oak')."""
    try:
        return _ok(blocks.describe(query))
    except BlockError:
        return _ok({"matches": blocks.search(query)})


@mcp.tool()
def list_registry(kind: str, filter: str = "") -> str:
    """Valid ids for kind = 'item', 'entity', 'feature', 'structure', 'biome', 'template_pool'."""
    key = {"item": "minecraft:item", "entity": "minecraft:entity_type"}.get(kind, kind)
    reg = blocks.registries().get(key)
    if reg is None:
        return _err(f"unknown kind; choose from item, entity, feature, structure, biome, template_pool")
    hits = [r for r in reg if filter.lower() in r]
    return _ok({"count": len(hits), "ids": hits[:300]})


@mcp.tool()
def render(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, view: str = "south_east",
           scale: int = 0, cutaway: int | None = None, dimension: str = "minecraft:overworld") -> Image:
    """Render a box to a PNG with real Minecraft textures (isometric) so you can check a build.
    view: 'south_east' | 'south_west' | 'north_east' | 'north_west' (camera direction) or 'top'.
    cutaway: hide everything above this y to look inside (e.g. floor y + 3 shows the furnished interior)."""
    from .render import render_cells
    cells = engine.read_cells(x1, y1, z1, x2, y2, z2, dimension, include_air=False)
    if cutaway is not None:
        cells = {p: v for p, v in cells.items() if p[1] <= cutaway}
    png = render_cells(cells, view=view, scale=scale)
    return Image(data=png, format="png")


@mcp.tool()
def render_build(build_id: str | None = None, view: str = "south_east", margin: int = 3,
                 cutaway: int | None = None) -> Image:
    """Render a build from list_builds (default: latest) with some surrounding terrain."""
    hist = [p for p in engine.history() if not p.undone]
    p = next((h for h in hist if h.id == build_id), None) if build_id else (hist[-1] if hist else None)
    if p is None:
        raise ValueError("no such build")
    return render(p.min[0] - margin, p.min[1] - margin, p.min[2] - margin, p.max[0] + margin, p.max[1] + 1,
                  p.max[2] + margin, view=view, cutaway=cutaway, dimension=p.dimension)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
