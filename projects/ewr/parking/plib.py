# Shared parking helpers (exec AFTER kit.py). Plan coords; fy = walking level, floor blocks at fy-1.
# Conventions used by every parking build:
#   space 3 wide x 7 deep, 1-block white_concrete lines inlaid in the floor (never raised),
#   wheel stop = smooth_stone_slab row across the 3 blocks, 1 block in from the nose end,
#   accessible = blue_concrete floor + white symbol block, EV = green_concrete floor + charger
#   (lightning_rod with a lantern on top) just beyond the nose end, rental = company colour floor.
import json as _json

LINE = "white_concrete"
STOP = "smooth_stone_slab[type=bottom]"
YAW = {"+s": 180, "-s": 0, "+t": -90, "-t": 90}
BAYS = []


def pline(s1, s2, t1, t2, fy, blk=LINE):
    rect(min(s1, s2), max(s1, s2), min(t1, t2), max(t1, t2), fy - 1, blk)


def bay(sa, sb, ta, tb, fy, nose, kind="std", col=None, stop=True, charger="beyond", tag="",
        charger_y=None):
    """3x7 bay on plan rect sa..sb, ta..tb (one side 3, the other 7). nose = '+s'|'-s'|'+t'|'-t' (the
    wheel-stop end). kind: std | acc | ev | rental (col = colour name). Records the bay in BAYS."""
    sa, sb = sorted((sa, sb)); ta, tb = sorted((ta, tb))
    cs, ct = (sa + sb) / 2.0, (ta + tb) / 2.0
    if kind == "acc":
        rect(sa, sb, ta, tb, fy - 1, "blue_concrete")
        put(round(cs), round(ct), fy - 1, "white_concrete")
    elif kind == "ev":
        rect(sa, sb, ta, tb, fy - 1, "green_concrete")
    elif kind == "rental":
        rect(sa, sb, ta, tb, fy - 1, f"{col}_concrete")
    # nose-end row and wheel stop
    if nose == "+s":
        end, stp, out = [(sb, t) for t in range(ta, tb + 1)], [(sb - 1, t) for t in range(ta, tb + 1)], (sb + 1, round(ct))
    elif nose == "-s":
        end, stp, out = [(sa, t) for t in range(ta, tb + 1)], [(sa + 1, t) for t in range(ta, tb + 1)], (sa - 1, round(ct))
    elif nose == "+t":
        end, stp, out = [(s, tb) for s in range(sa, sb + 1)], [(s, tb - 1) for s in range(sa, sb + 1)], (round(cs), tb + 1)
    else:
        end, stp, out = [(s, ta) for s in range(sa, sb + 1)], [(s, ta + 1) for s in range(sa, sb + 1)], (round(cs), ta - 1)
    if stop:
        for (s, t) in stp:
            put(s, t, fy, STOP)
    if kind == "ev" and charger:
        if charger == "beyond":
            cs_, ct_ = out
        else:
            cs_, ct_ = charger
        cy = fy if charger_y is None else charger_y
        put(cs_, ct_, cy, "lightning_rod")
        put(cs_, ct_, cy + 1, "lantern[hanging=false]")
    BAYS.append(dict(tag=tag, kind=kind if kind != "rental" else f"rental:{col}", s=cs, t=ct, fy=fy, nose=nose,
                     world=[60 + ct + 0.5, 64 + fy, 310 - cs + 0.5], yaw=YAW[nose]))
    return cs, ct


def report_bays():
    from collections import Counter
    c = Counter((b_["tag"], b_["kind"]) for b_ in BAYS)
    print("BAYS", _json.dumps({f"{k[0]}|{k[1]}": v for k, v in sorted(c.items())}))
    return c


def dump_bays(path):
    with open(path, "w") as fh:
        _json.dump(BAYS, fh, indent=0)
