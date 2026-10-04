"""Block-state strings: parse, validate against the 26.3 block catalog, rotate.

A state string looks like 'oak_stairs[facing=east,half=top]'. The namespace is
optional. data/blocks.json was generated from the server jar's data reports.
"""

from __future__ import annotations

import difflib
import json
import os
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

HORIZONTAL = ["north", "east", "south", "west"]  # clockwise order seen from above
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}


@lru_cache(maxsize=1)
def catalog() -> dict[str, dict]:
    with open(os.path.join(DATA_DIR, "blocks.json"), encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def registries() -> dict[str, list[str]]:
    with open(os.path.join(DATA_DIR, "registries.json"), encoding="utf-8") as f:
        return json.load(f)


def ns(name: str) -> str:
    name = name.strip().lower()
    return name if ":" in name else "minecraft:" + name


@lru_cache(maxsize=65536)
def parse(state: str) -> tuple[str, tuple[tuple[str, str], ...]]:
    """'oak_stairs[facing=east]' -> ('minecraft:oak_stairs', (('facing','east'),))."""
    state = state.strip()
    if "[" in state:
        name, rest = state.split("[", 1)
        rest = rest.rstrip("]")
        props = []
        for kv in filter(None, (p.strip() for p in rest.split(","))):
            k, _, v = kv.partition("=")
            props.append((k.strip(), v.strip()))
        return ns(name), tuple(sorted(props))
    return ns(state), ()


def fmt(name: str, props: dict | tuple) -> str:
    items = sorted(props.items()) if isinstance(props, dict) else props
    if not items:
        return name
    return name + "[" + ",".join(f"{k}={v}" for k, v in items) + "]"


class BlockError(ValueError):
    pass


@lru_cache(maxsize=65536)
def normalize(state: str) -> str:
    """Validate a state string and return it in canonical form. Raises BlockError with suggestions."""
    name, props = parse(state)
    cat = catalog()
    info = cat.get(name)
    if info is None:
        guess = difflib.get_close_matches(name, cat.keys(), n=4, cutoff=0.6)
        raise BlockError(f"unknown block '{name}'" + (f"; did you mean {', '.join(guess)}?" if guess else ""))
    allowed = info["p"]
    for k, v in props:
        if k not in allowed:
            raise BlockError(f"{name} has no property '{k}' (valid: {', '.join(allowed) or 'none'})")
        if v not in allowed[k]:
            raise BlockError(f"{name}[{k}={v}] invalid; {k} must be one of {', '.join(allowed[k])}")
    return fmt(name, props)


def full_props(state: str) -> tuple[str, dict[str, str]]:
    """Canonical name plus every property, with defaults filled in."""
    name, items = canonical(state)
    return name, dict(items)


@lru_cache(maxsize=65536)
def canonical(state: str) -> tuple[str, tuple[tuple[str, str], ...]]:
    """Hashable full form, so 'oak_stairs' and 'oak_stairs[facing=north,half=bottom,...]' compare equal."""
    name, props = parse(state)
    d = dict(catalog().get(name, {}).get("d", {}))
    d.update(props)
    return name, tuple(sorted(d.items()))


def describe(name: str) -> dict:
    info = catalog().get(ns(name))
    if info is None:
        raise BlockError(f"unknown block '{name}'")
    return {"id": ns(name), "properties": info["p"], "defaults": info["d"]}


def search(query: str, limit: int = 40) -> list[str]:
    q = query.lower().replace(" ", "_")
    hits = [k for k in catalog() if q in k]
    if not hits:
        hits = difflib.get_close_matches(ns(q), catalog().keys(), n=limit, cutoff=0.5)
    return sorted(hits, key=len)[:limit]


# -- rotation ---------------------------------------------------------------

def rot_dir(d: str, steps: int) -> str:
    if d in HORIZONTAL:
        return HORIZONTAL[(HORIZONTAL.index(d) + steps) % 4]
    return d


_RAIL = {
    "north_south": "east_west", "east_west": "north_south",
    "ascending_north": "ascending_east", "ascending_east": "ascending_south",
    "ascending_south": "ascending_west", "ascending_west": "ascending_north",
    "south_east": "south_west", "south_west": "north_west",
    "north_west": "north_east", "north_east": "south_east",
}


@lru_cache(maxsize=65536)
def rotate(state: str, steps: int) -> str:
    """Rotate a block state clockwise (seen from above) by steps * 90 degrees."""
    steps %= 4
    if steps == 0 or "[" not in state:
        return state
    name, props = parse(state)
    p = dict(props)
    for _ in range(steps):
        q = dict(p)
        if p.get("facing") in HORIZONTAL:
            q["facing"] = rot_dir(p["facing"], 1)
        if "axis" in p and p["axis"] in ("x", "z"):
            q["axis"] = "z" if p["axis"] == "x" else "x"
        if "rotation" in p and p["rotation"].isdigit():
            q["rotation"] = str((int(p["rotation"]) + 4) % 16)
        if "shape" in p and p["shape"] in _RAIL:
            q["shape"] = _RAIL[p["shape"]]
        if any(d in p for d in HORIZONTAL):
            for d in HORIZONTAL:
                q.pop(d, None)
            for d in HORIZONTAL:
                if d in p:
                    q[rot_dir(d, 1)] = p[d]
        p = q
    return fmt(name, p)
