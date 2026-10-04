"""Load building files from disk into relative cells {(x,y,z): (state, nbt Tag | None)}.

Supports Sponge .schem v2/v3 (WorldEdit / FAWE exports) and vanilla structure
.nbt files (structure blocks, other worlds' generated/ folders).
"""

from __future__ import annotations

from . import nbt
from .nbt import COMPOUND, Tag
from .world import AIR, state_string


def _varints(data: list[int]):
    out, i, n = [], 0, len(data)
    while i < n:
        val = shift = 0
        while True:
            b = data[i] & 0xFF
            i += 1
            val |= (b & 0x7F) << shift
            if not b & 0x80:
                break
            shift += 7
        out.append(val)
    return out


def load_schematic(path: str, include_air: bool = False) -> dict:
    with open(path, "rb") as f:
        raw = f.read()
    root = nbt.read(raw, typed=True)
    plain = nbt.untag(root)
    if "Schematic" in plain:  # Sponge v3 wraps everything
        root, plain = root["Schematic"].value, plain["Schematic"]
    if "Palette" in plain or "Blocks" in plain and isinstance(plain.get("Blocks"), dict):
        return _sponge(root, plain, include_air)
    if "palette" in plain or "palettes" in plain:
        return _structure(root, plain, include_air)
    raise ValueError("unrecognised file: expected a Sponge .schem or a structure .nbt")


def _sponge(root, plain, include_air):
    w, h, l = plain["Width"], plain["Height"], plain["Length"]
    if "Blocks" in plain and isinstance(plain["Blocks"], dict):  # v3
        blk, blk_t = plain["Blocks"], root["Blocks"].value
        palette, data, bents = blk["Palette"], blk["Data"], blk_t.get("BlockEntities")
    else:  # v2
        palette, data, bents = plain["Palette"], plain["BlockData"], root.get("BlockEntities")
    inv = {v: k for k, v in palette.items()}
    idx = _varints(data)
    be_map = {}
    for be in (bents.value if bents else []):
        d = be.value
        x, y, z = d["Pos"].value
        body = d["Data"].value if "Data" in d else {k: v for k, v in d.items() if k not in ("Pos", "Id")}
        be_map[(x, y, z)] = Tag(COMPOUND, dict(body))
    cells = {}
    for i, p in enumerate(idx):
        st = inv[p]
        name = st.split("[")[0]
        if not include_air and name in AIR:
            continue
        x = i % w
        z = (i // w) % l
        y = i // (w * l)
        cells[(x, y, z)] = (st, be_map.get((x, y, z)))
    return cells


def _structure(root, plain, include_air):
    pal = plain.get("palette") or plain["palettes"][0]
    states = [state_string(e) for e in pal]
    cells = {}
    for b, bt in zip(plain["blocks"], root["blocks"].value):
        st = states[b["state"]]
        if not include_air and st.split("[")[0] in AIR:
            continue
        x, y, z = b["pos"]
        cells[(x, y, z)] = (st, bt.value.get("nbt"))
    return cells
