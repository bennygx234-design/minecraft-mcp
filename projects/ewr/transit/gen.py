"""EWR transit: generates the ewr_transit datapack + the station panel build scripts from one data model.

    python gen.py            -> writes datapack to the server's world/datapacks/ewr_transit and
                                panel build scripts + panels.json next to this file
Coordinates are WORLD coordinates (TRANSIT.md is authoritative).
Fares (ewr_econ): $2 + $1 per 25 track blocks; buttons -> ewr:buy/<a>_<b> -> ewr_econ:try_buy -> ewr:start/<a>_<b> (start = free admin).
panels/signs_<stop>.py = sign-only rebuild; run with PYTHONUTF8=1 (cars/build.py reads the script with the default codec).
"""
import json
import math
import os
import shutil
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
DP = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_transit"
NS = "ewr"

# ---------------------------------------------------------------- network (TRANSIT.md)
NODES = {
    "A": (-43.5, 73, 238), "B": (-43.5, 73, 159), "C": (-43.5, 73, 126),
    "MJ": (-43.5, 73, 197), "S": (-43.5, 73, 270), "N": (-43.5, 73, 84),
    "MAR": (-66, 64, 197), "HAN": (4, 64, 5), "CAR": (-10, 64, 278),
    "MAN": (83, 75, -97), "BUR": (145, 69, -122), "TOP": (170, 221, -132),
}
J1 = (83, 86, -88)  # light-rail junction (Manor / Burj)
LINES = [
    ["S", "A", "MJ", "B", "C", "N"],
    ["MJ", (-55, 73, 197), (-66, 66, 197), "MAR"],
    ["N", (-43.5, 80, 40), (4, 74, 10), "HAN"],
    ["S", (-43.5, 82, 285), (-10, 82, 280), (-10, 70, 278), "CAR"],   # revised: clears FedEx roof
    ["N", (-43.5, 86, 60), (-43.5, 86, -30), (20, 86, -78), J1, (83, 78, -95), "MAN"],
    [J1, (130, 86, -92), (145, 78, -108), "BUR"],
    ["BUR", (150, 90, -112), (150, 230, -112)],   # then a snap into the deck (TOP)
]
STOPS = ["A", "B", "C", "MAR", "HAN", "CAR", "MAN", "BUR"]
DESTS = STOPS + ["TOP"]
NAME = {"A": "Terminal A", "B": "Terminal B", "C": "Terminal C", "MAR": "Marriott", "HAN": "Hangars",
        "CAR": "Cargo", "MAN": "Manor", "BUR": "Burj Khalifa", "TOP": "Burj Top"}
SIGN = {  # button label signs (4 lines max, ~15 chars)
    "A": ["", "\u2192 Terminal A", "AirTrain", ""], "B": ["", "\u2192 Terminal B", "AirTrain", ""],
    "C": ["", "\u2192 Terminal C", "AirTrain", ""], "MAR": ["", "\u2192 Marriott", "& garages", ""],
    "HAN": ["", "\u2192 Hangars", "north apron", ""], "CAR": ["", "\u2192 Cargo", "FedEx apron", ""],
    "MAN": ["", "\u2192 Manor", "south gate", ""], "BUR": ["", "\u2192 Burj Khalifa", "lobby", ""],
    "TOP": ["\u2192 Burj Khalifa", "Observation", "Deck", "(top)"],
}

# ---------------------------------------------------------------- fares (ewr_econ)
FARE_BASE, FARE_PER = 2, 25      # $2 + $1 per 25 blocks of track (rounded)


def route_len(a, b):
    pts = [pos(n) for n in path(a, b)] + ([NODES["TOP"]] if b == "TOP" else [])
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


def fare(a, b):
    return FARE_BASE + int(route_len(a, b) / FARE_PER + 0.5)


_W = {**{c: 2 for c in "i!.,':;|"}, "l": 3, "`": 3, **{c: 4 for c in "It[] "}, **{c: 5 for c in "fk<>(){}*"},
      "@": 7, "~": 7, "→": 8}


def px(t):
    """approximate rendered width of a sign line in the default font (sign lines fit ~90 px)"""
    return sum(_W.get(c, 6) for c in t)


def sign_lines(stop, d):
    lines = list(SIGN[d])
    p = f"${fare(stop, d)}"
    for i, l in enumerate(lines):          # the destination line: price on the same line if it fits
        if l.startswith("→"):
            for sep in ("  ", " "):
                if px(l + sep + p) <= 80:      # conservative (a sign line is ~90 px)
                    lines[i] = l + sep + p
                    return lines
            break
    for i in (3, 0):                       # otherwise on an empty line / appended to the last line
        if not lines[i]:
            lines[i] = "fare " + p
            return lines
    lines[3] = lines[3] + "  " + p
    assert px(lines[3]) <= 88, lines
    return lines


# ---------------------------------------------------------------- station panels
# segment: leftmost wall cell (x, z), facing (direction buttons face, toward the rider), n columns,
# header columns (indices that get the header row + cap), header sign columns.
# base = y of the lowest wall block (= walking level / feet y).
DV = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
PANELS = {
    # AirTrain stations have a slab canopy at y=76, so the board is 3 high (y 73..75) with the header
    # signs on an extra column at its left end
    "A": dict(base=73, segs=[dict(left=(-46, 241), facing="east", n=8, roof=True)]),
    "B": dict(base=73, segs=[dict(left=(-46, 162), facing="east", n=8, roof=True)]),
    "C": dict(base=73, segs=[dict(left=(-46, 129), facing="east", n=8, roof=True)]),
    "MAR": dict(base=64, segs=[dict(left=(-61, 201), facing="north", n=8)]),
    "HAN": dict(base=64, segs=[dict(left=(8, 1), facing="west", n=8)]),
    # Cargo: the light-rail lift frame (posts x -13/-8, z 276/282) surrounds the stand (with
    # cargo dollies inside it on x=-12): 4 buttons on a board just north of the lift + 4 on the lift's inner
    # east side (3 high, under the glass ring at y=67)
    "CAR": dict(base=64, segs=[dict(left=(-11, 274), facing="south", n=4),
                               dict(left=(-8, 277), facing="west", n=4, roof=True, hcol=False)]),
    # Manor: two 4-wide boards either side of the south gate, standing against (not touching) the gate wall;
    # header row skips the cells holding the manor's red wall banners (x 79 / 87, y 78, z -100)
    "MAN": dict(base=75, segs=[dict(left=(77, -100), facing="south", n=4, head=[0, 1], hsign=[0, 1]),
                               dict(left=(86, -100), facing="south", n=4, head=[2, 3], hsign=[2, 3])]),
    # Burj: on the plaza just north of the light-rail platform (platform x 141..147, z -126..-121)
    "BUR": dict(base=68, segs=[dict(left=(140, -128), facing="south", n=8)]),
}
EXTRA = {}  # (the light-rail builder provides the MAN landing strip, floor y=74)


def right_vec(facing):
    fx, fz = DV[facing]
    vx, vz = -fx, -fz          # the viewer looks opposite to the facing
    return (-vz, vx)           # viewer's right-hand side


def panel_cells(stop):
    """-> (blocks: list[((x,y,z), state, sign_lines|None)], buttons: list[(dest, (x,y,z), facing)])"""
    p = PANELS[stop]
    base = p["base"]
    dests = [d for d in DESTS if d != stop]
    blocks, buttons = [], []
    i = 0
    for seg in p["segs"]:
        rx, rz = right_vec(seg["facing"])
        fx, fz = DV[seg["facing"]]
        n = seg["n"]
        head = seg.get("head", list(range(n)))
        hsign = seg.get("hsign", [n // 2 - 1, n // 2])
        roof = seg.get("roof", False)
        if roof and seg.get("hcol", True):
            head = []
            wx, wz = seg["left"][0] - rx, seg["left"][1] - rz      # header column left of the buttons
            for y in range(base, base + 3):
                blocks.append(((wx, y, wz), "light_blue_concrete", None))
            blocks.append(((wx + fx, base + 2, wz + fz), f"birch_wall_sign[facing={seg['facing']}]",
                           ["AIRTRAIN", "press a button", "to ride", "→"]))
            blocks.append(((wx + fx, base + 1, wz + fz), f"birch_wall_sign[facing={seg['facing']}]",
                           ["you are at", NAME[stop], "", ""]))
        for c in range(n):
            wx, wz = seg["left"][0] + rx * c, seg["left"][1] + rz * c
            for y in range(base, base + 3):
                blocks.append(((wx, y, wz), "white_concrete", None))
            if roof:
                head = []
            elif c in head:
                blocks.append(((wx, base + 3, wz), "light_blue_concrete", None))
                blocks.append(((wx, base + 4, wz), "smooth_quartz_slab[type=bottom]", "OPT"))
            else:
                blocks.append(((wx, base + 3, wz), "smooth_quartz_slab[type=bottom]", "OPT"))
            d = dests[i]
            i += 1
            bpos = (wx + fx, base + 1, wz + fz)
            buttons.append((d, bpos, seg["facing"]))
            blocks.append((bpos, f"stone_button[face=wall,facing={seg['facing']}]", None))
            blocks.append(((wx + fx, base + 2, wz + fz), f"birch_wall_sign[facing={seg['facing']}]", sign_lines(stop, d)))
        for k, c in enumerate([] if roof else hsign):
            wx, wz = seg["left"][0] + rx * c, seg["left"][1] + rz * c
            lines = ["AIRTRAIN", "press a button", "to ride", ""] if k == 0 else \
                ["you are at", NAME[stop], "", ""]
            blocks.append(((wx + fx, base + 3, wz + fz), f"birch_wall_sign[facing={seg['facing']}]", lines))
    assert i == len(dests), (stop, i)
    for pos, st in EXTRA.get(stop, []):
        blocks.append((pos, st, None))
    return blocks, buttons


def panel_script(stop, origin, signs_only=False):
    ox, oy, oz = origin
    blocks, _ = panel_cells(stop)
    if signs_only:
        blocks = [bl for bl in blocks if isinstance(bl[2], list)]
    out = [f"# station panel for {stop} ({NAME[stop]}) -- generated by gen.py; builder origin {origin}"]
    for (x, y, z), st, lines in blocks:
        lx, ly, lz = x - ox, y - oy, z - oz
        if lines is None:
            out.append(f"b.set({lx},{ly},{lz},{st!r})")
        elif lines == "OPT":   # decorative cap: only where nothing is built yet
            out.append(f"if (world_block({lx},{ly},{lz}) or 'minecraft:air').split('[')[0] in ('minecraft:air', 'minecraft:cave_air'): b.set({lx},{ly},{lz},{st!r})")
        else:
            facing = st.split("facing=")[1].rstrip("]")
            out.append(f"b.sign({lx},{ly},{lz},{lines!r},facing={facing!r},wall=True,wood='birch')")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- routing
def build_graph():
    adj = {}

    def key(p):
        return p if isinstance(p, str) else tuple(p)

    for line in LINES:
        for a, b in zip(line, line[1:]):
            a, b = key(a), key(b)
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
    return adj


ADJ = build_graph()


def pos(n):
    return NODES[n] if isinstance(n, str) else n


def path(a, b):
    """BFS (the network is a tree) from stop a to dest b; TOP is reached via the shaft top + snap."""
    target = (150, 230, -112) if b == "TOP" else b
    prev = {a: None}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == target:
            break
        for v in ADJ[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    out, u = [], target
    while u is not None:
        out.append(u)
        u = prev[u]
    return out[::-1]


def yaw_of(p0, p1, last):
    dx, dz = p1[0] - p0[0], p1[2] - p0[2]
    if math.hypot(dx, dz) < 0.5:
        return last
    return round(math.degrees(math.atan2(-dx, dz)), 1)


def f(v):
    """number with at least one decimal, so integer x/z are NOT centred (+0.5) by the command parser"""
    s = ("%.4f" % v).rstrip("0")
    return s + "0" if s.endswith(".") else s


def P(p):
    return f"{f(p[0])} {f(p[1])} {f(p[2])}"


def text(t, color="aqua", bold=False):
    d = {"text": t, "color": color}
    if bold:
        d["bold"] = True
    return json.dumps(d, ensure_ascii=False)


# car model: parts in the car's local frame (local +z = direction of travel), block, translation, scale
CAR = [
    ("white_concrete", (-1.0, -0.1, -1.8), (2.0, 1.0, 3.6)),             # main (the vehicle itself)
    ("light_blue_stained_glass", (-1.0, 0.9, -1.8), (2.0, 0.8, 3.6)),     # window band
    ("white_concrete", (-1.0, 1.7, -1.8), (2.0, 0.35, 3.6)),              # roof
    ("light_blue_concrete", (-1.03, 0.3, -1.83), (2.06, 0.22, 3.66)),     # livery stripe
    ("gray_concrete", (-0.9, -0.32, -1.6), (1.8, 0.24, 3.2)),             # underframe / bogies
    ("light_gray_concrete", (-0.8, 2.05, -1.0), (1.6, 0.18, 2.0)),        # roof pod
]


def display_nbt(block, tr, sc, tags, yaw):
    tags = ",".join(f'"{t}"' for t in tags)
    return (f'{{Tags:[{tags}],Rotation:[{yaw}f,0f],teleport_duration:2,view_range:2.0f,'
            f'block_state:"minecraft:{block}",'
            f'transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
            f'translation:[{tr[0]}f,{tr[1]}f,{tr[2]}f],scale:[{sc[0]}f,{sc[1]}f,{sc[2]}f]}}}}')


def gen_datapack():
    if os.path.isdir(DP):
        shutil.rmtree(DP)
    fdir = os.path.join(DP, "data", NS, "function")
    files = {}

    def W(name, lines):
        files[name] = "\n".join(lines) + "\n"

    routes = []
    for a in STOPS:
        for b in DESTS:
            if a != b:
                routes.append((a, b))
    rid = {r: i + 1 for i, r in enumerate(routes)}

    # --- per route: start + movement
    for (a, b), R in rid.items():
        nodes = path(a, b)
        wps = [pos(n) for n in nodes]
        name = f"{a}_{b}"
        n = len(wps)
        yaws, last = [], 0.0
        for k in range(1, n):
            last = yaw_of(wps[k - 1], wps[k], last)
            yaws.append(last)
        # start
        s0 = wps[0]
        lines = [f"# start ride {NAME[a]} -> {NAME[b]} (as the rider)",
                 "execute if entity @s[tag=ewrt_ride] run return fail",
                 "tag @s add ewrt_ride",
                 "execute unless score @s ewrt_id matches 1.. store result score @s ewrt_id run scoreboard players add #next ewrt_id 1",
                 "scoreboard players operation #cur ewrt_id = @s ewrt_id",
                 f"tp @s {P(s0)}"]
        for j, (blk, tr, sc) in enumerate(CAR):
            tags = ["ewrt_car", "ewrt_new", "ewrt_main" if j == 0 else "ewrt_part"]
            lines.append(f"summon block_display {P(s0)} {display_nbt(blk, tr, sc, tags, yaws[0])}")
        lines += [
            "scoreboard players operation @e[tag=ewrt_new] ewrt_id = #cur ewrt_id",
            f"scoreboard players set @e[tag=ewrt_new,tag=ewrt_main] ewrt_route {R}",
            "scoreboard players set @e[tag=ewrt_new,tag=ewrt_main] ewrt_step 1",
            "scoreboard players set @e[tag=ewrt_new,tag=ewrt_main] ewrt_t -30",
            "ride @s mount @e[tag=ewrt_new,tag=ewrt_main,limit=1]",
            "tag @e[tag=ewrt_new] remove ewrt_new",
            "effect give @s minecraft:resistance 600 4 true",
            "effect give @s minecraft:slow_falling 600 0 true",
            "playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 1.4",
            f"tellraw @s {text('[AirTrain] ' + NAME[a] + ' -> ' + NAME[b] + ' - doors closing', 'aqua')}",
        ]
        W(f"start/{name.lower()}", lines)
        # paid entry (station buttons): ticket via the shared economy, then the (free, admin) start function
        W(f"buy/{name.lower()}", [
            f"# ticket {NAME[a]} -> {NAME[b]}: {route_len(a, b):.0f} blocks -> ${fare(a, b)} (as the rider)",
            "execute if entity @s[tag=ewrt_ride] run return fail",
            f'return run function ewr_econ:try_buy {{price:{fare(a, b)},item:"AirTrain ticket to {NAME[b]}",then:"ewr:start/{name.lower()}"}}'])

        # movement (as the car, descending step order so an advance never moves twice in one tick)
        named = [nd if isinstance(nd, str) and nd in NAME else None for nd in nodes]
        lines = [f"# move car along {NAME[a]} -> {NAME[b]}: {len(wps)} waypoints",
                 f"execute if score @s ewrt_step matches {n}.. run return run function ewr:arrive/{b.lower()}"]
        for k in range(n - 1, 0, -1):
            w, yaw = wps[k], yaws[k - 1]
            final = k == n - 1
            g = f"execute if score @s ewrt_step matches {k} positioned {P(w)}"
            snap = 0.35 if final else 1.2
            lines.append(f"{g} if entity @s[distance=..{snap}] run tp @s {P(w)} {yaw} 0")
            lines.append(f"{g} if entity @s[distance=..0.001] run scoreboard players set @s ewrt_step {k + 1}")
            mv = f"at @s facing {P(w)} run tp @s ^ ^ ^"
            if final:
                lines.append(f"{g} if entity @s[distance={snap}..4] {mv}0.35 {yaw} 0")
                lines.append(f"{g} if entity @s[distance=4..12] {mv}0.7 {yaw} 0")
                lines.append(f"{g} unless entity @s[distance=..12] {mv}1.2 {yaw} 0")
            else:
                lines.append(f"{g} unless entity @s[distance=..1.2] {mv}1.2 {yaw} 0")
        # actionbar (every 30 ticks): next stop on the way
        groups = []
        for k in range(1, n):
            nxt = next((named[j] for j in range(k, n) if named[j]), b)
            if b == "TOP" and nxt is None:
                nxt = "TOP"
            if groups and groups[-1][2] == nxt:
                groups[-1][1] = k
            else:
                groups.append([k, k, nxt])
        for k1, k2, nxt in groups:
            msg = (f"Final stop: {NAME[b]}" if nxt == b else f"Next stop: {NAME[nxt]}   (to {NAME[b]})")
            rng = f"{k1}" if k1 == k2 else f"{k1}..{k2}"
            lines.append(f"execute if score @s ewrt_t matches 0 if score @s ewrt_step matches {rng} run "
                         f"title @a[tag=ewrt_rcur] actionbar {text(msg, 'yellow')}")
        W(f"r/{name.lower()}", lines)

    # --- arrival (as car) and landing (as rider)
    for b in DESTS:
        W(f"arrive/{b.lower()}", [
            f"# car reached {NAME[b]}",
            f"execute as @e[tag=ewrt_rcur] run function ewr:land/{b.lower()}",
            "execute as @e[type=block_display,tag=ewrt_part] if score @s ewrt_id = #cur ewrt_id run kill @s",
            "tag @s add ewrt_done"])
        W(f"land/{b.lower()}", [
            "ride @s dismount",
            f"tp @s {P(NODES[b])}",
            "effect clear @s minecraft:slow_falling",
            "effect clear @s minecraft:resistance",
            "tag @s remove ewrt_ride", "tag @s remove ewrt_orphan", "tag @s remove ewrt_onv",
            "title @s times 5 50 15",
            f"title @s subtitle {text('EWR AirTrain', 'gray')}",
            f"title @s title {text('Arrived: ' + NAME[b], 'aqua', True)}",
            "playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 1.2"])

    # --- core
    dispatch = [f"execute if score @s ewrt_route matches {R} run return run function ewr:r/{a.lower()}_{b.lower()}"
                for (a, b), R in rid.items()]
    W("car_tick", [
        "# as + at a car's main body",
        "scoreboard players operation #cur ewrt_id = @s ewrt_id",
        "execute as @e[tag=ewrt_ride] if score @s ewrt_id = #cur ewrt_id run tag @s add ewrt_rcur",
        "execute unless entity @e[tag=ewrt_rcur] run return run function ewr:abort",
        "tag @e[tag=ewrt_rcur] remove ewrt_orphan",
        "function ewr:dispatch",
        "execute unless entity @s[tag=ewrt_done] at @s as @e[type=block_display,tag=ewrt_part] if score @s ewrt_id = #cur ewrt_id run tp @s ~ ~ ~ ~ ~",
        "tag @s add ewrt_cur",
        "execute unless entity @s[tag=ewrt_done] as @e[tag=ewrt_rcur] run function ewr:rider_tick",
        "tag @s remove ewrt_cur",
        "tag @e[tag=ewrt_rcur] remove ewrt_rcur",
        "scoreboard players add @s ewrt_t 1",
        "execute if score @s ewrt_t matches 30.. run scoreboard players set @s ewrt_t 0",
        "kill @s[tag=ewrt_done]"])
    W("dispatch", dispatch)
    W("rider_tick", [
        "# keep the rider seated in its car (re-seat after sneaking out)",
        "tag @s remove ewrt_onv",
        "execute on vehicle if entity @s[tag=ewrt_cur] on passengers run tag @s add ewrt_onv",
        "execute unless entity @s[tag=ewrt_onv] run ride @s dismount",
        "execute unless entity @s[tag=ewrt_onv] at @e[tag=ewrt_cur,limit=1] run tp @s ~ ~ ~",
        "execute unless entity @s[tag=ewrt_onv] run ride @s mount @e[tag=ewrt_cur,limit=1]"])
    W("abort", [
        "# car lost its rider (logged out / died): remove the car",
        "execute as @e[type=block_display,tag=ewrt_part] if score @s ewrt_id = #cur ewrt_id run kill @s",
        "kill @s"])
    W("cleanup", [
        "# rider without a car",
        "ride @s dismount",
        "tag @s remove ewrt_ride", "tag @s remove ewrt_orphan", "tag @s remove ewrt_onv",
        "effect clear @s minecraft:slow_falling", "effect clear @s minecraft:resistance"])
    W("reset", [
        "# emergency: remove all cars, free all riders",
        "kill @e[type=block_display,tag=ewrt_car]",
        "execute as @e[tag=ewrt_ride] run function ewr:cleanup",
        "scoreboard players reset * ewrt_btn"])
    W("load", [
        "scoreboard objectives add ewrt_id dummy",
        "scoreboard objectives add ewrt_route dummy",
        "scoreboard objectives add ewrt_step dummy",
        "scoreboard objectives add ewrt_t dummy",
        "scoreboard objectives add ewrt_btn dummy",
        "scoreboard players add #next ewrt_id 0",
        "function ewr:trains/load"])
    W("tick", [
        "tag @e[tag=ewrt_ride] add ewrt_orphan",
        "execute as @e[type=block_display,tag=ewrt_main] at @s run function ewr:car_tick",
        "execute as @e[tag=ewrt_orphan] run function ewr:cleanup",
        "function ewr:buttons",
        "function ewr:trains/tick"])

    # --- buttons (rising-edge detection so a held button never re-triggers / grabs a second player)
    lines = ["# station panel buttons"]
    panels = {}
    for a in STOPS:
        _, buttons = panel_cells(a)
        panels[a] = [(d, bp, fc) for d, bp, fc in buttons]
        for d, (x, y, z), _fc in buttons:
            fake = f"#{a}_{d}"
            cond = f"if block {x} {y} {z} minecraft:stone_button[powered=true]"
            lines.append(f"execute {cond} unless score {fake} ewrt_btn matches 1 positioned {x}.5 {y}.5 {z}.5 "
                         f"as @p[distance=..4,tag=!ewrt_ride,gamemode=!spectator] at @s run function ewr:buy/{a.lower()}_{d.lower()}")
            lines.append(f"execute store success score {fake} ewrt_btn {cond}")
    W("buttons", lines)

    for name, body in files.items():
        p = os.path.join(fdir, name + ".mcfunction")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(body)
    tdir = os.path.join(DP, "data", "minecraft", "tags", "function")
    os.makedirs(tdir, exist_ok=True)
    json.dump({"values": [f"{NS}:tick"]}, open(os.path.join(tdir, "tick.json"), "w"))
    json.dump({"values": [f"{NS}:load"]}, open(os.path.join(tdir, "load.json"), "w"))
    json.dump({"pack": {"description": "EWR AirTrain / city transit push-button rides",
                        "min_format": 121, "max_format": 121}},
              open(os.path.join(DP, "pack.mcmeta"), "w"), indent=1)
    nt = gen_trains(fdir)
    return rid, panels, len(files) + nt


# ---------------------------------------------------------------- always-running decorative trains
# Every car's position is precomputed for every tick of its train's cycle; the datapack replays it as
# runs of constant per-tick deltas (relative tp) plus an absolute snap at every run start and every
# SNAP ticks (so trains re-sync after their chunks were unloaded). Lines are bucketed by tick range.
AIR_W, AIR_E = -44.2, -42.8          # two lanes on the AirTrain deck (northbound west, southbound east)
TRAINS = [
    # AirTrain shuttles: loop  west lane z 266 -> 88, cross, east lane 88 -> 266, cross back.
    dict(name="air", loop=True, y=73.0, width=1.4, cars=(2.0, -2.0), speed=0.5, wait=60,
         path=[(AIR_W, 266), (AIR_W, 88), (AIR_E, 88), (AIR_E, 266)],
         stops_z=[("W", 238), ("W", 159), ("W", 126), ("W", 90), ("E", 126), ("E", 159), ("E", 238), ("E", 262)],
         count=3),
    # City light rail: out and back on the single elevated track (deck 1 below ride level y=86)
    dict(name="city", loop=False, y=85.5, width=1.8, cars=(4.0, 0.0, -4.0), speed=0.6, wait=60,
         path=[(-43.5, 60), (-43.5, -30), (20, -78), (83, -88), (130, -92)],
         stops_xz=[(-43.5, 60, 6), (83, -88, 0), (130, -92, -6)], count=1),
]
SNAP = 40
BUCKET = 100


def seglens(path):
    return [math.dist(a, b) for a, b in zip(path, path[1:])]


def at_s(path, s):
    """point + tangent yaw at arc length s along an open polyline (clamped)"""
    L = seglens(path)
    for (a, b), l in zip(zip(path, path[1:]), L):
        if s <= l or (a, b) == (path[-2], path[-1]):
            t = max(0.0, min(1.0, s / l))
            x, z = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            yaw = math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))
            return x, z, round(yaw, 1)
        s -= l


def train_schedule(tr):
    """-> list of train-centre arc positions, one per tick of the cycle"""
    path = tr["path"]
    if tr["loop"]:
        path = path + [path[0]]
    L = sum(seglens(path))
    if tr["loop"]:
        # arc position of each stop: west lane s = 266 - z ; east lane s = 178 + 1.4 + (z - 88)
        cross = abs(AIR_E - AIR_W)
        stops = [(266 - z) if lane == "W" else (178 + cross + z - 88) for lane, z in tr["stops_z"]]
        stops = stops + [stops[0] + L]
    else:
        def arc_of(x, z):
            acc = 0.0
            for a, b in zip(path, path[1:]):
                if math.dist(a, (x, z)) < 1e-6:
                    return acc
                acc += math.dist(a, b)
            return acc
        out = [arc_of(x, z) + off for x, z, off in tr["stops_xz"]]
        stops = out + out[-2::-1]           # there and back
    seq = []
    for i in range(len(stops) - 1):
        s0, s1 = stops[i], stops[i + 1]
        seq += [s0] * tr["wait"]
        n = max(1, round(abs(s1 - s0) / tr["speed"]))
        seq += [s0 + (s1 - s0) * k / n for k in range(1, n)]
    return path, L, seq


def car_states(tr, path, L, seq, off):
    st = []
    for s in seq:
        cs = (s + off) % L if tr["loop"] else s + off
        x, z, yaw = at_s(path, cs)
        st.append((x, tr["y"], z, yaw))
    return st


def car_lines(states, tag):
    """-> list of (t1, t2, command) for one car (all its display parts share the tag)"""
    T = len(states)
    out = []
    prev_d = None
    run = None
    for t in range(T):
        x, y, z, yaw = states[t]
        px, py, pz, pyaw = states[t - 1]
        d = (round(x - px, 5), 0.0, round(z - pz, 5), yaw)
        moving = d[0] != 0 or d[2] != 0
        if t == 0 or t % SNAP == 0 or d != prev_d or yaw != pyaw:
            if run:
                out.append(run); run = None
            out.append((t, t, f"tp @s {f(x)} {f(y)} {f(z)} {yaw} 0"))
        elif moving:
            if run and run[1] == t - 1 and run[3] == d:
                run = (run[0], t, run[2], d)
            else:
                if run:
                    out.append(run)
                run = (t, t, f"tp @s ~{f(d[0])} ~ ~{f(d[2])} {yaw} 0", d)
        prev_d = d
    if run:
        out.append(run)
    return [(a, b, c) for a, b, c, *_ in out]


def train_parts(tr):
    w = tr["width"]
    return [
        ("white_concrete", (-w / 2, 0.1, -1.8), (w, 2.0, 3.6), None),
        ("blue_stained_glass", (-w / 2 - 0.03, 0.95, -1.7), (w + 0.06, 0.7, 3.4), None),
        ("sea_lantern", (-0.3, 0.35, -1.84), (0.6, 0.3, 3.68), {"sky": 15, "block": 15}),   # head/tail lights
        ("light_gray_concrete", (-w / 2 + 0.1, 2.1, -1.5), (w - 0.2, 0.15, 3.0), None),      # roof pod
    ]


def gen_trains(fdir):
    files = {}
    spawn = ["# (re)spawn all decorative trains: kills loaded ones first",
             "kill @e[type=block_display,tag=ewrt_train]"]
    tick = ["# always-running trains (decoration)"]
    load = []
    for tr in TRAINS:
        path, L, seq = train_schedule(tr)
        T = len(seq)
        for n in range(tr["count"]):
            tid = f"{tr['name']}{n + 1}"
            fake = f"#{tid}"
            phase = (T * n) // tr["count"]
            load.append(f"execute unless score {fake} ewrt_tt matches 0.. run scoreboard players set {fake} ewrt_tt {phase}")
            tick.append(f"scoreboard players add {fake} ewrt_tt 1")
            tick.append(f"execute if score {fake} ewrt_tt matches {T}.. run scoreboard players set {fake} ewrt_tt 0")
            buckets = {}
            for k, off in enumerate(tr["cars"]):
                tag = f"ewrt_{tid}_c{k}"
                st = car_states(tr, path, L, seq, off)
                x, y, z, yaw = st[phase]
                for blk, trn, sc, br in train_parts(tr):
                    nbt = display_nbt(blk, tuple(round(v, 3) for v in trn), tuple(round(v, 3) for v in sc),
                                      ["ewrt_train", f"ewrt_{tid}", tag], yaw)
                    if br:
                        nbt = nbt[:-1] + f',brightness:{{sky:{br["sky"]},block:{br["block"]}}}}}'
                    spawn.append(f"summon block_display {f(x)} {f(y)} {f(z)} {nbt}")
                for a, b, cmd in car_lines(st, tag):
                    t = a
                    while t <= b:          # split across buckets
                        bk = t // BUCKET
                        e2 = min(b, bk * BUCKET + BUCKET - 1)
                        rng = f"{t}" if t == e2 else f"{t}..{e2}"
                        buckets.setdefault(bk, []).append(
                            f"execute if score {fake} ewrt_tt matches {rng} as @e[type=block_display,tag={tag}] at @s run {cmd}")
                        t = e2 + 1
            for bk, lines in buckets.items():
                files[f"trains/{tid}_{bk}"] = lines
                lo, hi = bk * BUCKET, bk * BUCKET + BUCKET - 1
                tick.append(f"execute if score {fake} ewrt_tt matches {lo}..{hi} run function ewr:trains/{tid}_{bk}")
            print(f"train {tid}: cycle {T} ticks ({T / 20:.0f} s), {tr['cars'].__len__()} cars, "
                  f"{sum(len(v) for v in buckets.values())} lines")
    files["trains/spawn"] = spawn
    files["trains/despawn"] = ["kill @e[type=block_display,tag=ewrt_train]"]
    files["trains/tick"] = tick
    files["trains/load"] = ["scoreboard objectives add ewrt_tt dummy"] + load
    for name, lines in files.items():
        p = os.path.join(fdir, name + ".mcfunction")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    return len(files)


def main():
    rid, panels, nf = gen_datapack()
    # build scripts
    os.makedirs(os.path.join(HERE, "panels"), exist_ok=True)
    for a in STOPS:
        if a in ("A", "B", "C"):
            origin = (60, 64, 310)  # harness plan origin
            body = 'exec(open(r"C:\\Users\\benny\\.claude\\jobs\\ef42125c\\tmp\\ewr\\kit.py").read())\n' + \
                panel_script(a, origin)
        else:
            sx, sy, sz = NODES[a]
            origin = (math.floor(sx), int(sy), math.floor(sz))
            body = panel_script(a, origin)
        open(os.path.join(HERE, "panels", f"panel_{a}.py"), "w", encoding="utf-8").write(body)
        sbody = (body.split(chr(10), 1)[0] + chr(10) if a in ("A", "B", "C") else "") + panel_script(a, origin, signs_only=True)
        open(os.path.join(HERE, "panels", f"signs_{a}.py"), "w", encoding="utf-8").write(sbody)
    allcells = {a: [(list(p), st) for p, st, ln in panel_cells(a)[0] if ln != "OPT"] for a in STOPS}
    json.dump({"routes": {f"{a}_{b}": R for (a, b), R in rid.items()},
               "buttons": {a: [[d, list(bp), fc] for d, bp, fc in v] for a, v in panels.items()},
               "cells": allcells,
               "fares": {f"{a}_{b}": fare(a, b) for (a, b) in rid},
               "paths": {f"{a}_{b}": [list(pos(n)) for n in path(a, b)] for (a, b) in rid}},
              open(os.path.join(HERE, "panels.json"), "w"), indent=0)
    print(f"datapack: {nf} functions, {len(rid)} routes -> {DP}")


if __name__ == "__main__":
    main()
