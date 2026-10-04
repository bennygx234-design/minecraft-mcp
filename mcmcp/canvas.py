"""The building API that build scripts run against.

A script gets `b`, a View onto a Canvas. Every coordinate is local to the build
origin: +x east, +y up, +z south. Nothing touches the world until the whole
canvas is compiled into one structure template and placed in a single command.

Views can be nested with `b.at(x, y, z, rot)`; a nested view has its own origin
and rotation (quarter turns clockwise seen from above) and rotates block states
(stairs, doors, logs, beds...) along with positions. Write a furnished room once
as a function taking a view, then stamp it anywhere at any rotation.

A block argument may be a state string ('oak_stairs[facing=east,half=top]'), a
list (uniform random pick per block) or a dict of weights
({'stone_bricks': 6, 'cracked_stone_bricks': 2, 'mossy_stone_bricks': 1}).
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Iterable

from . import blocks
from .blocks import HORIZONTAL, OPPOSITE, rot_dir
from .nbt import BYTE, COMPOUND, INT, LIST, STRING, Tag, parse_snbt

AIR = "minecraft:air"
DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
COLORS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
          "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]


def right_of(facing: str) -> str:
    return rot_dir(facing, 1)


def left_of(facing: str) -> str:
    return rot_dir(facing, -1)


class Canvas:
    def __init__(self, seed: int | None = None):
        self.voxels: dict[tuple[int, int, int], tuple[str, Tag | None]] = {}
        self.entities: list[tuple[str, float, float, float, str]] = []  # id, x, y, z, snbt
        self.commands: list[str] = []  # run after placement; {x},{y},{z} filled per call site
        self.rng = random.Random(seed)
        self.notes: list[str] = []

    def bbox(self):
        if not self.voxels:
            return None
        xs, ys, zs = zip(*self.voxels)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def view(self) -> "View":
        return View(self, 0, 0, 0, 0)


class View:
    """A positioned, rotated window onto a Canvas. All builder methods live here."""

    def __init__(self, canvas: Canvas, ox: int, oy: int, oz: int, rot: int):
        self.c, self.ox, self.oy, self.oz, self.rot = canvas, ox, oy, oz, rot % 4
        self._pick_cache: dict[Any, Callable[[], str]] = {}

    # -- transforms ---------------------------------------------------------
    def _xz(self, x: float, z: float) -> tuple[float, float]:
        for _ in range(self.rot):
            x, z = -z, x
        return x, z

    def pos(self, x: int, y: int, z: int) -> tuple[int, int, int]:
        """Local -> canvas coordinates."""
        rx, rz = self._xz(x, z)
        return int(round(rx)) + self.ox, int(y) + self.oy, int(round(rz)) + self.oz

    def dir(self, d: str) -> str:
        """Local direction -> canvas direction."""
        return rot_dir(d, self.rot)

    def at(self, x: int, y: int, z: int, rot: int = 0) -> "View":
        """A child view with its origin at local (x, y, z), turned `rot` quarter turns clockwise."""
        ax, ay, az = self.pos(x, y, z)
        return View(self.c, ax, ay, az, self.rot + rot)

    @property
    def rng(self) -> random.Random:
        return self.c.rng

    # -- block resolution ---------------------------------------------------
    @staticmethod
    def _prep(block: str) -> str:
        s = blocks.normalize(block)
        name, props = blocks.parse(s)
        # placed leaves decay unless marked persistent
        if name.endswith("_leaves") and not any(k == "persistent" for k, _ in props):
            s = blocks.fmt(name, dict(props) | {"persistent": "true"})
        return s

    def _picker(self, block) -> Callable[[], str]:
        key = block if isinstance(block, str) else repr(block)
        p = self._pick_cache.get(key)
        if p:
            return p
        if isinstance(block, str):
            s = blocks.rotate(self._prep(block), self.rot)
            p = lambda: s
        elif isinstance(block, dict):
            states = [blocks.rotate(self._prep(k), self.rot) for k in block]
            weights = list(block.values())
            p = lambda: self.c.rng.choices(states, weights)[0]
        else:
            states = [blocks.rotate(self._prep(k), self.rot) for k in block]
            p = lambda: self.c.rng.choice(states)
        self._pick_cache[key] = p
        return p

    def _put(self, x, y, z, picker, nbt=None):
        self.c.voxels[self.pos(x, y, z)] = (picker(), nbt)

    # -- primitives ---------------------------------------------------------
    def set(self, x: int, y: int, z: int, block, nbt: str | dict | Tag | None = None):
        """One block. nbt: SNBT string like '{Items:[...]}' for block entities."""
        if isinstance(nbt, str):
            nbt = parse_snbt(nbt)
        elif isinstance(nbt, dict):
            nbt = Tag(COMPOUND, nbt)
        self._put(x, y, z, self._picker(block), nbt)

    def get(self, x: int, y: int, z: int) -> str | None:
        v = self.c.voxels.get(self.pos(x, y, z))
        return v[0] if v else None

    def unset(self, x: int, y: int, z: int):
        """Remove a planned block so the world keeps whatever is there."""
        self.c.voxels.pop(self.pos(x, y, z), None)

    def box(self, x1, y1, z1, x2, y2, z2, block, hollow: bool = False):
        """Solid cuboid (inclusive corners). hollow=True leaves only the shell; interior untouched."""
        p = self._picker(block)
        xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
        for x in range(xa, xb + 1):
            for y in range(ya, yb + 1):
                for z in range(za, zb + 1):
                    if hollow and xa < x < xb and ya < y < yb and za < z < zb:
                        continue
                    self._put(x, y, z, p)

    fill = box

    def clear(self, x1, y1, z1, x2, y2, z2):
        """Carve to air."""
        self.box(x1, y1, z1, x2, y2, z2, AIR)

    def room(self, x1, y1, z1, x2, y2, z2, block, floor=None, ceiling=None):
        """Hollow shell with the interior cleared to air; optional distinct floor/ceiling blocks."""
        self.box(x1, y1, z1, x2, y2, z2, block, hollow=True)
        xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
        if xb - xa > 1 and yb - ya > 1 and zb - za > 1:
            self.clear(xa + 1, ya + 1, za + 1, xb - 1, yb - 1, zb - 1)
        if floor:
            self.box(xa, ya, za, xb, ya, zb, floor)
        if ceiling:
            self.box(xa, yb, za, xb, yb, zb, ceiling)

    def walls(self, x1, y1, z1, x2, y2, z2, block):
        """Four vertical sides of a box, no floor or roof."""
        xa, xb = sorted((x1, x2)); za, zb = sorted((z1, z2))
        self.box(xa, y1, za, xb, y2, za, block)
        self.box(xa, y1, zb, xb, y2, zb, block)
        self.box(xa, y1, za, xa, y2, zb, block)
        self.box(xb, y1, za, xb, y2, zb, block)

    def floor(self, x1, z1, x2, z2, y, block):
        self.box(x1, y, z1, x2, y, z2, block)

    def frame(self, x1, y1, z1, x2, y2, z2, block):
        """The 12 edges of a box (beams/pillars). Logs get the right axis automatically."""
        xa, xb = sorted((x1, x2)); ya, yb = sorted((y1, y2)); za, zb = sorted((z1, z2))
        def axis(b, a):
            return f"{b}[axis={a}]" if isinstance(b, str) and "[" not in b and "axis" in blocks.catalog().get(blocks.ns(b), {}).get("p", {}) else b
        for x in (xa, xb):
            for z in (za, zb):
                self.box(x, ya, z, x, yb, z, axis(block, "y"))
        for y in (ya, yb):
            for z in (za, zb):
                self.box(xa, y, z, xb, y, z, axis(block, "x"))
            for x in (xa, xb):
                self.box(x, y, za, x, y, zb, axis(block, "z"))

    def line(self, x1, y1, z1, x2, y2, z2, block):
        p = self._picker(block)
        n = max(abs(x2 - x1), abs(y2 - y1), abs(z2 - z1), 1)
        for i in range(n + 1):
            t = i / n
            self._put(round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t), round(z1 + (z2 - z1) * t), p)

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, block, hollow=False, half: str | None = None):
        """half='top' or 'bottom' for domes/bowls. hollow shell is 1 block thick."""
        p = self._picker(block)
        for x in range(-math.ceil(rx), math.ceil(rx) + 1):
            for y in range(-math.ceil(ry), math.ceil(ry) + 1):
                if half == "top" and y < 0 or half == "bottom" and y > 0:
                    continue
                for z in range(-math.ceil(rz), math.ceil(rz) + 1):
                    d = (x / (rx + .5)) ** 2 + (y / (ry + .5)) ** 2 + (z / (rz + .5)) ** 2
                    if d > 1:
                        continue
                    if hollow:
                        di = (x / max(rx - .5, .01)) ** 2 + (y / max(ry - .5, .01)) ** 2 + (z / max(rz - .5, .01)) ** 2
                        if di < 1:
                            continue
                    self._put(cx + x, cy + y, cz + z, p)

    def sphere(self, cx, cy, cz, r, block, hollow=False):
        self.ellipsoid(cx, cy, cz, r, r, r, block, hollow)

    def dome(self, cx, cy, cz, r, block, hollow=True):
        self.ellipsoid(cx, cy, cz, r, r, r, block, hollow, half="top")

    def cylinder(self, cx, y, cz, r, height, block, hollow=False, rz=None):
        """Vertical cylinder from y up `height` blocks. rz for elliptical."""
        p = self._picker(block)
        rz = r if rz is None else rz
        for x in range(-math.ceil(r), math.ceil(r) + 1):
            for z in range(-math.ceil(rz), math.ceil(rz) + 1):
                d = (x / (r + .5)) ** 2 + (z / (rz + .5)) ** 2
                if d > 1:
                    continue
                if hollow and (x / max(r - .5, .01)) ** 2 + (z / max(rz - .5, .01)) ** 2 < 1:
                    continue
                for yy in range(y, y + height):
                    self._put(cx + x, yy, cz + z, p)

    def pyramid(self, x1, z1, x2, z2, y, block, hollow=True):
        """Stepped pyramid shrinking 1 per layer, base at y."""
        xa, xb = sorted((x1, x2)); za, zb = sorted((z1, z2))
        i = 0
        while xa + i <= xb - i and za + i <= zb - i:
            self.box(xa + i, y + i, za + i, xb - i, y + i, zb - i, block, hollow=False) if not hollow else \
                self.walls(xa + i, y + i, za + i, xb - i, y + i, zb - i, block)
            i += 1
        if hollow and xa + i - 1 <= xb - i + 1:
            self.box(xa + i - 1, y + i - 1, za + i - 1, xb - i + 1, y + i - 1, zb - i + 1, block)

    def replace(self, old: str, new, x1=None, y1=None, z1=None, x2=None, y2=None, z2=None):
        """Swap planned blocks whose id matches `old` (prefix match, e.g. 'oak_planks'); optionally within a local box."""
        old_id = blocks.ns(old)
        p = self._picker(new)
        box = None
        if x1 is not None:
            a, b = self.pos(x1, y1, z1), self.pos(x2, y2, z2)
            box = [sorted((a[i], b[i])) for i in range(3)]
        for k, (s, nb) in list(self.c.voxels.items()):
            if s.split("[")[0] == old_id and (box is None or all(box[i][0] <= k[i] <= box[i][1] for i in range(3))):
                self.c.voxels[k] = (p(), None)

    def mirror_x(self, x_axis: int):
        """Duplicate everything planned so far, mirrored across the plane x = x_axis (canvas coords).
        Handy for symmetric facades: build the west half, then mirror it."""
        swap = {"east": "west", "west": "east", "left": "right", "right": "left",
                "inner_left": "inner_right", "inner_right": "inner_left",
                "outer_left": "outer_right", "outer_right": "outer_left"}
        for (x, y, z), (st, nb) in list(self.c.voxels.items()):
            name, props = blocks.parse(st)
            q = {}
            for k, v in props:
                if k == "facing" or k == "hinge" or k == "shape" or k == "type" and name.endswith("chest"):
                    v = swap.get(v, v)
                if k == "rotation" and v.isdigit():
                    v = str((16 - int(v)) % 16)
                q[{"east": "west", "west": "east"}.get(k, k)] = v
            self.c.voxels[(2 * x_axis - x, y, z)] = (blocks.fmt(name, q), nb)

    # -- architecture -------------------------------------------------------
    def door(self, x, y, z, facing: str, block="oak_door", hinge="left", open=False):
        """Two-block door. facing = direction you face walking IN through it."""
        b = block.split("[")[0]
        o = str(bool(open)).lower()
        self.set(x, y, z, f"{b}[facing={facing},half=lower,hinge={hinge},open={o}]")
        self.set(x, y + 1, z, f"{b}[facing={facing},half=upper,hinge={hinge},open={o}]")

    def double_door(self, x, y, z, facing: str, block="oak_door"):
        """Door at (x,y,z) and its partner one block to the right (as you walk in)."""
        dx, dz = DIRS[right_of(facing)]
        self.door(x, y, z, facing, block, hinge="left")
        self.door(x + dx, y, z + dz, facing, block, hinge="right")

    def window(self, x1, y1, z1, x2, y2, z2, glass="glass_pane"):
        self.box(x1, y1, z1, x2, y2, z2, glass)

    def stairs_run(self, x, y, z, direction: str, length: int, block="oak_stairs", width=1, support=None):
        """Staircase climbing toward `direction`, `width` wide to the right. support fills under each step."""
        dx, dz = DIRS[direction]
        rx, rz = DIRS[right_of(direction)]
        b = block.split("[")[0]
        for i in range(length):
            for w in range(width):
                px, pz = x + dx * i + rx * w, z + dz * i + rz * w
                self.set(px, y + i, pz, f"{b}[facing={direction},half=bottom]")
                if support:
                    for yy in range(y, y + i):
                        self.set(px, yy, pz, support)

    def ladder(self, x, y, z, height, facing: str):
        """Ladder column. facing = direction the ladder faces (away from the wall it hangs on)."""
        for i in range(height):
            self.set(x, y + i, z, f"ladder[facing={facing}]")

    def gable_roof(self, x1, z1, x2, z2, y, stairs="oak_stairs", ridge: str = "x", overhang=1,
                   gable=None, ridge_block=None):
        """Two-sloped roof over the footprint x1..x2, z1..z2 starting at height y.
        ridge='x' runs the ridge east-west (slopes face north/south); 'z' runs it north-south.
        gable: block for the triangular end walls (inside the footprint). ridge_block: cap for odd widths
        (defaults to a bottom slab of the same wood/stone when one exists)."""
        st = stairs.split("[")[0]
        cap = ridge_block or _slab_for(st)
        xa, xb = sorted((x1, x2)); za, zb = sorted((z1, z2))
        if ridge == "x":
            lo, hi, a0, a1 = za - overhang, zb + overhang, xa - overhang, xb + overhang
            near, far = "south", "north"  # low row (north side) climbs south
        else:
            lo, hi, a0, a1 = xa - overhang, xb + overhang, za - overhang, zb + overhang
            near, far = "east", "west"
        i = 0
        while lo + i <= hi - i:
            yy = y + i
            a, bb = lo + i, hi - i
            for t in range(a0, a1 + 1):
                if a == bb:
                    self._rset(ridge, t, yy, a, cap)
                else:
                    self._rset(ridge, t, yy, a, f"{st}[facing={near},half=bottom]")
                    self._rset(ridge, t, yy, bb, f"{st}[facing={far},half=bottom]")
            if gable:
                for t in ((xa, xb) if ridge == "x" else (za, zb)):
                    for k in range(a + 1, bb):
                        if (za <= k <= zb) if ridge == "x" else (xa <= k <= xb):
                            self._rset(ridge, t, yy, k, gable)
            i += 1
        return y + i - 1  # top y

    def _rset(self, ridge, t, y, k, block):
        if ridge == "x":
            self.set(t, y, k, block)
        else:
            self.set(k, y, t, block)

    def hip_roof(self, x1, z1, x2, z2, y, stairs="oak_stairs", overhang=1, top=None, fill=None):
        """Four-sloped roof; corners shape themselves. top caps the ridge (default: matching slab).
        fill puts a solid block under each ring so the roof is closed from inside."""
        st = stairs.split("[")[0]
        cap = top or _slab_for(st)
        xa, xb = sorted((x1, x2)); za, zb = sorted((z1, z2))
        xa -= overhang; xb += overhang; za -= overhang; zb += overhang
        i = 0
        while xa + i <= xb - i and za + i <= zb - i:
            a0, a1, b0, b1, yy = xa + i, xb - i, za + i, zb - i, y + i
            if a1 - a0 < 1 or b1 - b0 < 1:
                self.box(a0, yy, b0, a1, yy, b1, cap)
                break
            for x in range(a0, a1 + 1):
                self.set(x, yy, b0, f"{st}[facing=south]")
                self.set(x, yy, b1, f"{st}[facing=north]")
            for z in range(b0 + 1, b1):
                self.set(a0, yy, z, f"{st}[facing=east]")
                self.set(a1, yy, z, f"{st}[facing=west]")
            if fill and i > 0:
                self.box(a0 + 1, yy - 1, b0 + 1, a1 - 1, yy - 1, b1 - 1, fill)
            i += 1
        return y + i

    def flat_roof(self, x1, z1, x2, z2, y, block, rim=None, rim_height=1):
        self.floor(x1, z1, x2, z2, y, block)
        if rim:
            self.walls(x1, y + 1, z1, x2, y + rim_height, z2, rim)

    def foundation(self, x1, z1, x2, z2, y, block, depth=8):
        """Solid footing from y down `depth` blocks, so builds on slopes don't float."""
        self.box(x1, y - depth, z1, x2, y, z2, block)

    # -- furniture & details ------------------------------------------------
    def bed(self, x, y, z, facing: str, color="red"):
        """Foot at (x,y,z); head one block toward `facing` (put the headboard wall there)."""
        dx, dz = DIRS[facing]
        self.set(x, y, z, f"{color}_bed[facing={facing},part=foot]")
        self.set(x + dx, y, z + dz, f"{color}_bed[facing={facing},part=head]")

    def chair(self, x, y, z, facing: str, block="oak_stairs"):
        """Stair seat; facing = direction the sitter looks."""
        self.set(x, y, z, f"{block.split('[')[0]}[facing={OPPOSITE[facing]},half=bottom]")

    def table(self, x, y, z, leg="oak_fence", top="oak_pressure_plate"):
        """1x1 table: fence post + pressure plate (or carpet)."""
        self.set(x, y, z, leg)
        if top:
            self.set(x, y + 1, z, top)

    def long_table(self, x1, z1, x2, z2, y, slab="spruce_slab"):
        """Table surface of upside-down slabs at table height."""
        self.box(x1, y, z1, x2, y, z2, f"{slab.split('[')[0]}[type=top]")

    def sofa(self, x, y, z, facing: str, length=3, seat="oak_stairs", arm="oak_trapdoor"):
        """Row of stair seats extending to the sitter's right, with trapdoor arms."""
        rx, rz = DIRS[right_of(facing)]
        for i in range(length):
            self.chair(x + rx * i, y, z + rz * i, facing, seat)
        if arm:
            a = arm.split("[")[0]
            self.set(x - rx, y, z - rz, f"{a}[facing={left_of(facing)},open=true,half=bottom]")
            self.set(x + rx * length, y, z + rz * length, f"{a}[facing={right_of(facing)},open=true,half=bottom]")

    def bookshelves(self, x1, y1, z1, x2, y2, z2, mix=True):
        self.box(x1, y1, z1, x2, y2, z2, {"bookshelf": 5, "chiseled_bookshelf": 1} if mix else "bookshelf")

    def lamp(self, x, y, z, kind="lantern", hanging=False, post="oak_fence"):
        """hanging=True: lantern under the ceiling block above. Otherwise a floor lamp (post + lantern)."""
        if hanging:
            self.set(x, y, z, f"{kind}[hanging=true]")
        else:
            self.set(x, y, z, post)
            self.set(x, y + 1, z, f"{kind}[hanging=false]")

    def wall_torch(self, x, y, z, facing: str, kind="wall_torch"):
        """facing = direction the torch points (away from its wall)."""
        self.set(x, y, z, f"{kind}[facing={facing}]")

    def chest(self, x, y, z, facing: str, items: Iterable | None = None, double=False, block="chest"):
        """facing = direction the lid opens toward (where you stand). items: [('bread', 16), ('iron_ingot', 8)]
        or [(slot, 'item', count)]. double=True adds the partner chest to the viewer's right."""
        b = block.split("[")[0]
        nbt = _items_nbt(items) if items else None
        if not double:
            self.set(x, y, z, f"{b}[facing={facing},type=single]", nbt)
            return
        # Vanilla: a chest whose partner sits clockwise of its facing is the LEFT half.
        cw = right_of(facing)
        dx, dz = DIRS[OPPOSITE[cw]]  # viewer's right (viewer faces opposite of `facing`)
        self.set(x, y, z, f"{b}[facing={facing},type=right]", nbt)
        self.set(x + dx, y, z + dz, f"{b}[facing={facing},type=left]")

    def barrel(self, x, y, z, facing="up", items=None):
        self.set(x, y, z, f"barrel[facing={facing}]", _items_nbt(items) if items else None)

    def kitchen(self, x, y, z, facing: str, length=5, counter="smooth_stone_slab[type=top]",
                appliances=("smoker", "furnace", "water_cauldron[level=3]", "crafting_table", "barrel")):
        """Counter row to the viewer's right of (x,y,z); appliances face `facing` (toward the cook)."""
        dx, dz = DIRS[right_of(OPPOSITE[facing])]  # viewer looks at the counter, row runs to their right
        for i in range(length):
            px, pz = x + dx * i, z + dz * i
            ap = appliances[i] if i < len(appliances) else counter
            if ap.split("[")[0].replace("minecraft:", "") in ("smoker", "furnace", "blast_furnace"):
                ap = f"{ap.split('[')[0]}[facing={facing}]"
            elif ap.startswith("barrel") and "[" not in ap:
                ap = f"barrel[facing={facing}]"
            self.set(px, y, pz, ap)

    def carpet(self, x1, z1, x2, z2, y, color="red", border=None):
        self.box(x1, y, z1, x2, y, z2, f"{color}_carpet")
        if border:
            self.walls(x1, y, z1, x2, y, z2, f"{border}_carpet")

    def plant(self, x, y, z, kind="potted_fern"):
        self.set(x, y, z, kind)

    def sign(self, x, y, z, lines: list[str], facing="south", wall=True, wood="oak"):
        """Wall sign facing `facing` (readable from that side), or standing sign when wall=False."""
        msgs = Tag(LIST, [Tag(STRING, s) for s in (list(lines) + ["", "", "", ""])[:4]])
        nbt = Tag(COMPOUND, {"front_text": Tag(COMPOUND, {"messages": msgs}), "is_waxed": Tag(BYTE, 1)})
        if wall:
            self.set(x, y, z, f"{wood}_wall_sign[facing={facing}]", nbt)
        else:
            r = {"south": 0, "west": 4, "north": 8, "east": 12}[facing]
            self.set(x, y, z, f"{wood}_sign[rotation={r}]", nbt)

    def painting(self, x, y, z, facing: str, variant="minecraft:kebab"):
        """Painting entity hanging on the wall block behind (x,y,z); facing = direction it faces."""
        f = self.dir(facing)
        yaw = {"south": 0, "west": 90, "north": 180, "east": 270}[f]
        fid = {"south": 3, "west": 1, "north": 2, "east": 5}[f]
        self.summon("painting", x, y, z, f'{{facing:{fid}b,variant:"{variant}",Rotation:[{yaw}f,0f]}}')

    def summon(self, entity: str, x, y, z, nbt: str = ""):
        """Spawn an entity after the build is placed (mobs, armor stands, item frames...)."""
        ax, ay, az = self.pos(x, y, z)
        self.c.entities.append((blocks.ns(entity), ax + .5, ay, az + .5, nbt))

    def command(self, cmd: str, x=0, y=0, z=0):
        """Run a command after placement. '{x} {y} {z}' are replaced by the absolute coords of local (x,y,z)."""
        self.c.commands.append((cmd, self.pos(x, y, z)))

    # -- prefab -------------------------------------------------------------
    def house(self, x, y, z, width=9, depth=7, floors=1, wall="oak_planks", frame="spruce_log",
              floor_block="spruce_planks", roof="dark_oak_stairs", glass="glass_pane", door="spruce_door",
              furnished=True, foundation="cobblestone", floor_height=4, bed_color="red"):
        """Furnished timber-frame house. Footprint x..x+width-1, z..z+depth-1, front (door) on the south side
        (local +z), floor at y. Uses a gable roof running east-west. Returns the top y."""
        x2, z2 = x + width - 1, z + depth - 1
        if foundation:
            self.foundation(x, z, x2, z2, y - 1, foundation, depth=3)
        top_wall = y + floors * floor_height
        self.room(x, y, z, x2, top_wall, z2, wall)
        self.frame(x, y, z, x2, top_wall, z2, frame)
        for f in range(floors):
            fy = y + f * floor_height
            self.floor(x + 1, z + 1, x2 - 1, z2 - 1, fy, floor_block)
            if f:
                self.box(x, fy, z, x2, fy, z2, frame.replace("_log", "_planks") if "_log" in frame else frame)
                self.box(x + 1, fy, z + 1, x2 - 1, fy, z2 - 1, floor_block)
            # windows every other block along each wall, 2 high
            for wx in range(x + 2, x2 - 1, 3):
                self.window(wx, fy + 2, z, wx, fy + 3 if floor_height > 4 else fy + 2, z, glass)
                self.window(wx, fy + 2, z2, wx, fy + 3 if floor_height > 4 else fy + 2, z2, glass)
            for wz in range(z + 2, z2 - 1, 3):
                self.window(x, fy + 2, wz, x, fy + 2, wz, glass)
                self.window(x2, fy + 2, wz, x2, fy + 2, wz, glass)
        # front door, centred on the south wall, plus a step and lanterns
        dxp = x + width // 2
        self.clear(dxp, y + 1, z2, dxp, y + 2, z2)
        self.door(dxp, y + 1, z2, "north", door)
        self.set(dxp, y, z2 + 1, f"{_stairs_for(foundation) or 'cobblestone_stairs'}[facing=north]")
        self.wall_torch(dxp - 1, y + 3, z2 + 1, "south")
        self.wall_torch(dxp + 1, y + 3, z2 + 1, "south")
        # roof
        self.gable_roof(x, z, x2, z2, top_wall + 1, roof, ridge="x", overhang=1, gable=wall)
        if furnished:
            self._furnish(x, y, z, x2, z2, floors, floor_height, bed_color)
        return top_wall + (depth + 2) // 2 + 1

    def _furnish(self, x, y, z, x2, z2, floors, fh, bed_color):
        ix1, iz1, ix2, iz2 = x + 1, z + 1, x2 - 1, z2 - 1
        w, d = ix2 - ix1 + 1, iz2 - iz1 + 1
        for f in range(floors):
            fy = y + f * fh + 1
            ceil = y + (f + 1) * fh
            # hanging lights under each ceiling
            for lx in range(ix1 + 1, ix2, 4):
                self.lamp(lx, ceil - 1, iz1 + d // 2, hanging=True)
            if f == 0:
                # kitchen along the back (north) wall, facing south
                self.kitchen(ix1, fy, iz1, "south", length=min(5, w - 1))
                # dining table with chairs in the middle
                tx, tz = ix1 + w // 2, iz1 + d // 2
                if d >= 4:
                    self.long_table(tx - 1, tz, tx, tz, fy)
                    self.chair(tx - 1, fy, tz + 1, "north"); self.chair(tx, fy, tz + 1, "north")
                    self.chair(tx - 1, fy, tz - 1, "south"); self.chair(tx, fy, tz - 1, "south")
                # bookshelf + chest on the east wall, rug
                self.bookshelves(ix2, fy, iz1 + 1, ix2, fy + 1, min(iz2 - 1, iz1 + 2))
                self.chest(ix2, fy, iz2, "west", [("bread", 16), ("torch", 32), ("oak_planks", 64)])
                self.plant(ix1, fy, iz2, "potted_red_tulip")
            else:
                # bedroom: beds against the north wall
                self.bed(ix1, fy, iz1 + 1, "north", bed_color)
                if w >= 4:
                    self.bed(ix1 + 2, fy, iz1 + 1, "north", bed_color)
                # partner half goes to the viewer's right (east), so start one block in from the wall
                self.chest(ix2 - 1 if w >= 5 else ix2, fy, iz1, "south", [("white_wool", 8)], double=w >= 5)
                self.carpet(ix1 + 1, iz1 + 3, ix2 - 1, iz2 - 1, fy, "light_gray")
                self.lamp(ix2, fy, iz2, hanging=False)
            if f < floors - 1:
                # ladder in the south-west corner up through a hole in the next floor
                self.ladder(ix1, fy, iz2, fh, "north")
                self.set(ix1, ceil, iz2, "ladder[facing=north]")


def _slab_for(stairs: str) -> str:
    s = blocks.ns(stairs).replace("_stairs", "_slab")
    if s in blocks.catalog():
        return s + "[type=bottom]"
    alt = s.replace("_brick_slab", "_bricks").replace("_slab", "_planks")
    return alt if alt in blocks.catalog() else "minecraft:stone"


def _stairs_for(block: str) -> str | None:
    for cand in (blocks.ns(block) + "_stairs", blocks.ns(block).rstrip("s") + "_stairs"):
        if cand in blocks.catalog():
            return cand
    return None


def _items_nbt(items: Iterable) -> Tag:
    out = []
    for i, it in enumerate(items):
        if len(it) == 3:
            slot, item, count = it
        else:
            (item, count), slot = it, i
        out.append(Tag(COMPOUND, {"Slot": Tag(BYTE, int(slot)), "id": Tag(STRING, blocks.ns(item)), "count": Tag(INT, int(count))}))
    return Tag(COMPOUND, {"Items": Tag(LIST, out)})
