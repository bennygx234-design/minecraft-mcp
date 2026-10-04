"""Isometric renderer using the real block models and textures from the client jar.

Resolves blockstates -> models -> elements exactly like the game (variants and
multipart, parent chains, #texture references, x/y variant rotation), then
draws every visible element face as an affine-warped texture sprite, back to
front. Element rotations (e.g. crossed plants) are drawn unrotated, block
entities without models (chests, beds, signs) fall back to simple boxes.
"""

from __future__ import annotations

import io
import json
import os
import zipfile
from functools import lru_cache

from PIL import Image, ImageDraw

from . import blocks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_JAR = os.environ.get("MCMCP_CLIENT_JAR", os.path.join(ROOT, "data", "client-26.3.jar"))

SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.62, "west": 0.62}
NORMALS = {"up": (0, 1, 0), "down": (0, -1, 0), "north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}
GRASS, FOLIAGE, WATER = (124, 189, 107), (89, 174, 48), (63, 118, 228)
TINTS = {"birch_leaves": (128, 167, 85), "spruce_leaves": (97, 153, 97), "lily_pad": (32, 128, 48),
         "water": WATER, "bubble_column": WATER, "water_cauldron": WATER, "redstone_wire": (200, 20, 0),
         "attached_melon_stem": (224, 199, 28), "melon_stem": (224, 199, 28), "pumpkin_stem": (224, 199, 28)}
FOLIAGE_BLOCKS = ("leaves", "vine")


class Assets:
    def __init__(self, jar: str = CLIENT_JAR):
        if not os.path.exists(jar):
            raise FileNotFoundError(f"client jar not found at {jar}")
        self.zip = zipfile.ZipFile(jar)
        self._json: dict[str, dict | None] = {}
        self._tex: dict[str, Image.Image | None] = {}

    def json(self, path: str) -> dict | None:
        if path not in self._json:
            try:
                self._json[path] = json.loads(self.zip.read(path))
            except KeyError:
                self._json[path] = None
        return self._json[path]

    def texture(self, ref: str) -> Image.Image | None:
        if ref not in self._tex:
            ns_, _, p = (ref if ":" in ref else "minecraft:" + ref).partition(":")
            try:
                im = Image.open(io.BytesIO(self.zip.read(f"assets/{ns_}/textures/{p}.png"))).convert("RGBA")
                if im.height > im.width:  # animated strip: first frame
                    im = im.crop((0, 0, im.width, im.width))
                self._tex[ref] = im
            except KeyError:
                self._tex[ref] = None
        return self._tex[ref]

    # -- blockstate -> list of (model json path, x rot, y rot) --------------
    def variants(self, state: str) -> list[tuple[str, int, int]]:
        name, props = blocks.full_props(state)
        ns_, _, bid = name.partition(":")
        bs = self.json(f"assets/{ns_}/blockstates/{bid}.json")
        if not bs:
            return []
        out = []
        if "variants" in bs:
            for key, v in bs["variants"].items():
                conds = dict(kv.split("=", 1) for kv in key.split(",") if kv)
                if all(props.get(k) == val for k, val in conds.items()):
                    v = v[0] if isinstance(v, list) else v
                    out.append((v["model"], v.get("x", 0), v.get("y", 0)))
                    break
        for part in bs.get("multipart", []):
            if _when(part.get("when"), props):
                ap = part["apply"]
                ap = ap[0] if isinstance(ap, list) else ap
                out.append((ap["model"], ap.get("x", 0), ap.get("y", 0)))
        return out

    @lru_cache(maxsize=8192)
    def model(self, ref: str) -> tuple[dict, list]:
        """Resolve parent chain -> (textures, elements)."""
        ns_, _, p = (ref if ":" in ref else "minecraft:" + ref).partition(":")
        m = self.json(f"assets/{ns_}/models/{p}.json") or {}
        textures, elements = {}, None
        if "parent" in m:
            pt, pe = self.model(m["parent"])
            textures.update(pt)
            elements = pe
        textures.update(m.get("textures", {}))
        if "elements" in m:
            elements = m["elements"]
        return textures, elements or []


def _when(cond, props) -> bool:
    if cond is None:
        return True
    if "OR" in cond:
        return any(_when(c, props) for c in cond["OR"])
    if "AND" in cond:
        return all(_when(c, props) for c in cond["AND"])
    for k, v in cond.items():
        if str(props.get(k)) not in str(v).split("|"):
            return False
    return True


def _resolve_tex(textures: dict, ref, depth=0) -> str | None:
    # 26.x models may give a texture as {"sprite": ..., "force_translucent": ...}
    if isinstance(ref, dict):
        ref = ref.get("sprite")
    while ref and ref.startswith("#") and depth < 10:
        ref = textures.get(ref[1:])
        if isinstance(ref, dict):
            ref = ref.get("sprite")
        depth += 1
    return ref


# -- geometry ----------------------------------------------------------------

def _rot_point(p, xr, yr):
    x, y, z = p[0] - 8, p[1] - 8, p[2] - 8
    for _ in range((xr // 90) % 4):
        y, z = -z, y
    for _ in range((yr // 90) % 4):
        x, z = -z, x
    return (x + 8, y + 8, z + 8)


def _rot_dir(d, xr, yr):
    n = NORMALS[d]
    r = _rot_point((n[0] + 8, n[1] + 8, n[2] + 8), xr, yr)
    v = (round(r[0] - 8), round(r[1] - 8), round(r[2] - 8))
    return next(k for k, nv in NORMALS.items() if nv == v)


def _face_quad(d, f, t):
    """Corners [uv1, u2v1, u2v2, u1v2] in 0..16 element space, and the default uv."""
    x1, y1, z1 = f
    x2, y2, z2 = t
    if d == "up":
        return [(x1, y2, z1), (x2, y2, z1), (x2, y2, z2), (x1, y2, z2)], (x1, z1, x2, z2)
    if d == "down":
        return [(x1, y1, z2), (x2, y1, z2), (x2, y1, z1), (x1, y1, z1)], (x1, 16 - z2, x2, 16 - z1)
    if d == "north":
        return [(x2, y2, z1), (x1, y2, z1), (x1, y1, z1), (x2, y1, z1)], (16 - x2, 16 - y2, 16 - x1, 16 - y1)
    if d == "south":
        return [(x1, y2, z2), (x2, y2, z2), (x2, y1, z2), (x1, y1, z2)], (x1, 16 - y2, x2, 16 - y1)
    if d == "west":
        return [(x1, y2, z1), (x1, y2, z2), (x1, y1, z2), (x1, y1, z1)], (z1, 16 - y2, z2, 16 - y1)
    return [(x2, y2, z2), (x2, y2, z1), (x2, y1, z1), (x2, y1, z2)], (16 - z2, 16 - y2, 16 - z1, 16 - y1)


FALLBACK_BOX = {"chest": ((1, 0, 1), (15, 14, 15)), "bed": ((0, 0, 0), (16, 9, 16)),
                "water": ((0, 0, 0), (16, 14, 16)), "lava": ((0, 0, 0), (16, 14, 16))}
FALLBACK_TEX = {"water": "block/water_still", "lava": "block/lava_still", "chest": "block/oak_planks",
                "trapped_chest": "block/oak_planks", "ender_chest": "block/obsidian"}
SKIP = ("air", "cave_air", "void_air", "barrier", "light", "structure_void")


class Renderer:
    def __init__(self):
        self.a = Assets()
        self._faces: dict[str, tuple[list, bool]] = {}

    def faces(self, state: str) -> tuple[list, bool]:
        """[(dir, corners16, uvcorners, tex, tint, cullface)], is_opaque_full_cube"""
        if state in self._faces:
            return self._faces[state]
        name, props = blocks.full_props(state)
        bid = name.split(":")[1]
        out = []
        full = False
        if bid in SKIP:
            self._faces[state] = ([], False)
            return [], False
        tint = TINTS.get(bid) or (FOLIAGE if any(k in bid for k in FOLIAGE_BLOCKS) else GRASS)
        variants = self.a.variants(state)
        elems_total = 0
        for model_ref, xr, yr in variants:
            textures, elements = self.a.model(model_ref)
            for el in elements:
                elems_total += 1
                f, t = el["from"], el["to"]
                for d, face in el.get("faces", {}).items():
                    tex = _resolve_tex(textures, face.get("texture", ""))
                    if not tex:
                        continue
                    corners, duv = _face_quad(d, f, t)
                    uv = face.get("uv", duv)
                    uvc = [(uv[0], uv[1]), (uv[2], uv[1]), (uv[2], uv[3]), (uv[0], uv[3])]
                    r = (face.get("rotation", 0) // 90) % 4
                    uvc = uvc[r:] + uvc[:r]
                    rc = [_rot_point(c, xr, yr) for c in corners]
                    cull = face.get("cullface")
                    out.append((_rot_dir(d, xr, yr), rc, uvc, tex, tint if "tintindex" in face else None,
                                _rot_dir(cull, xr, yr) if cull in NORMALS else None))
            if len(elements) == 1 and elements[0]["from"] == [0, 0, 0] and elements[0]["to"] == [16, 16, 16]:
                texs = {_resolve_tex(textures, fc.get("texture", "")) for fc in elements[0]["faces"].values()}
                full = all(self.a.texture(tx) is not None and self.a.texture(tx).getextrema()[3][0] == 255 for tx in texs if tx)
        if elems_total == 0:
            textures = self.a.model(variants[0][0])[0] if variants else {}
            tex = FALLBACK_TEX.get(bid) or _resolve_tex(textures, textures.get("particle")) or None
            if tex and not any(s in bid for s in ("sign", "banner", "head", "skull")):
                key = next((k for k in FALLBACK_BOX if bid.endswith(k)), None)
                f, t = FALLBACK_BOX.get(key, ((0, 0, 0), (16, 16, 16)))
                for d in NORMALS:
                    corners, duv = _face_quad(d, f, t)
                    uvc = [(duv[0], duv[1]), (duv[2], duv[1]), (duv[2], duv[3]), (duv[0], duv[3])]
                    t_ = WATER if bid == "water" else None
                    if bid.endswith("_bed"):
                        tex = f"block/{bid.replace('_bed', '')}_wool"
                    out.append((d, corners, uvc, tex, t_, d if (f, t) == ((0, 0, 0), (16, 16, 16)) else None))
        self._faces[state] = (out, full)
        return out, full


_RENDERER: Renderer | None = None


def render_cells(cells: dict, view: str = "south_east", scale: int = 0, background=(152, 186, 230, 255)) -> bytes:
    """cells: {(x,y,z): (state, nbt)} absolute coords. Returns PNG bytes."""
    global _RENDERER
    if _RENDERER is None:
        _RENDERER = Renderer()
    R = _RENDERER
    if not cells:
        im = Image.new("RGBA", (64, 64), background)
        b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()
    states = {p: v[0] for p, v in cells.items()}
    xs, ys, zs = zip(*states)
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2
    turns = {"south_east": 0, "north_east": 1, "north_west": 2, "south_west": 3, "top": 0}.get(view, 0)
    top = view == "top"
    span = max(max(xs) - min(xs), max(zs) - min(zs)) + 1
    height = max(ys) - min(ys) + 1
    if not scale:
        scale = max(4, min(32, int(1400 / (span * 1.75 + height * 0.6 + 1))))
    s = scale
    import math
    c30, s30 = math.cos(math.radians(30)) * s, 0.5 * s

    def rot(x, z):
        x, z = x - cx, z - cz
        for _ in range(turns):
            x, z = z, -x
        return x, z

    def proj(x, y, z):
        if top:
            return x * s, z * s
        return (x - z) * c30, (x + z) * s30 - y * s

    full_cache = {}

    def opaque(p):
        st = states.get(p)
        if st is None:
            return False
        if st not in full_cache:
            full_cache[st] = R.faces(st)[1]
        return full_cache[st]

    visible_dirs = {"up"} if top else {"up", "south", "east"}
    dir_after = {}

    def rdir(d):
        if d not in dir_after:
            n = NORMALS[d]
            x, z = n[0], n[2]
            for _ in range(turns):
                x, z = z, -x
            dir_after[d] = next(k for k, v in NORMALS.items() if v == (x, n[1], z))
        return dir_after[d]

    draws = []
    for (x, y, z), st in states.items():
        faces, _ = R.faces(st)
        for d, corners, uvc, tex, tint, cull in faces:
            if rdir(d) not in visible_dirs:
                continue
            if cull:
                n = NORMALS[cull]
                if opaque((x + n[0], y + n[1], z + n[2])):
                    continue
            pts = []
            for (u, v, w) in corners:
                rx, rz = rot(x + u / 16, z + w / 16)
                pts.append((rx, y + v / 16, rz))
            ctr = [sum(p[i] for p in pts) / 4 for i in range(3)]
            depth = ctr[1] if top else ctr[0] + ctr[2] + ctr[1] * 0.999
            draws.append((depth, pts, uvc, tex, tint, rdir(d)))
    draws.sort(key=lambda t: t[0])

    # canvas bounds
    allp = [proj(*p) for _, pts, *_ in draws for p in pts] or [(0, 0)]
    minx, miny = min(p[0] for p in allp), min(p[1] for p in allp)
    maxx, maxy = max(p[0] for p in allp), max(p[1] for p in allp)
    pad = 8
    W, H = int(maxx - minx) + 2 * pad, int(maxy - miny) + 2 * pad
    if W * H > 6000 * 6000:
        raise ValueError("render too large; lower scale or region")
    img = Image.new("RGBA", (W, H), background)
    sprite_cache: dict = {}
    for _, pts, uvc, tex, tint, d in draws:
        sp = [proj(*p) for p in pts]
        sp = [(px - minx + pad, py - miny + pad) for px, py in sp]
        _draw_face(img, R.a, sp, uvc, tex, tint, SHADE[d], sprite_cache)
    out = io.BytesIO()
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out.getvalue()


def _draw_face(img, assets, sp, uvc, tex, tint, shade, cache):
    texture = assets.texture(tex)
    if texture is None:
        return
    ox, oy = min(p[0] for p in sp), min(p[1] for p in sp)
    bx, by = int(ox), int(oy)
    local = [(px - bx, py - by) for px, py in sp]
    key = (tex, tuple(uvc), tuple((round(a, 2), round(b, 2)) for a, b in local), tint, shade)
    spr = cache.get(key)
    if spr is None:
        spr = _make_sprite(texture, local, uvc, tint, shade)
        cache[key] = spr
    if spr is not None:
        img.alpha_composite(spr, (bx, by))


def _make_sprite(texture, local, uvc, tint, shade):
    (x0, y0), (x1, y1), _, (x3, y3) = local
    e1 = (x1 - x0, y1 - y0)
    e2 = (x3 - x0, y3 - y0)
    det = e1[0] * e2[1] - e1[1] * e2[0]
    if abs(det) < 0.05:
        return None
    tw = texture.width / 16.0
    (u0, v0), (u1, v1), _, (u3, v3) = [(u * tw, v * tw) for u, v in uvc]
    # tex = T0 + A * (screen - P0); A maps e1 -> (u1-u0, v1-v0), e2 -> (u3-u0, v3-v0)
    inv = (e2[1] / det, -e2[0] / det, -e1[1] / det, e1[0] / det)
    du1, dv1, du2, dv2 = u1 - u0, v1 - v0, u3 - u0, v3 - v0
    a = du1 * inv[0] + du2 * inv[2]
    b = du1 * inv[1] + du2 * inv[3]
    d = dv1 * inv[0] + dv2 * inv[2]
    e = dv1 * inv[1] + dv2 * inv[3]
    c = u0 - a * x0 - b * y0
    f = v0 - d * x0 - e * y0
    w = int(max(p[0] for p in local)) + 2
    h = int(max(p[1] for p in local)) + 2
    tex = texture
    if tint or shade != 1.0:
        r, g, bb, al = tex.split()
        k = [shade * (tint[i] / 255 if tint else 1) for i in range(3)]
        r = r.point(lambda v, k=k[0]: int(v * k))
        g = g.point(lambda v, k=k[1]: int(v * k))
        bb = bb.point(lambda v, k=k[2]: int(v * k))
        tex = Image.merge("RGBA", (r, g, bb, al))
    spr = tex.transform((w, h), Image.Transform.AFFINE, (a, b, c, d, e, f), resample=Image.Resampling.NEAREST)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(round(px), round(py)) for px, py in local], fill=255)
    # +0.5px outline avoids hairline seams between neighbouring faces
    ImageDraw.Draw(mask).line([(round(px), round(py)) for px, py in local + [local[0]]], fill=255, width=1)
    al = spr.getchannel("A")
    from PIL import ImageChops
    spr.putalpha(ImageChops.multiply(al, mask))
    return spr
