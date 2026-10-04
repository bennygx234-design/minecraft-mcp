"""White House Secret Service: generates the ewr_whitehouse datapack (agents = mannequin + interaction entity).

    python gen_ss.py          # write the datapack (+ checks every post is free in the live world)
Then (RCON):  reload ; function ewr_whitehouse:spawn_all
Tags / scoreboards all start with ewhs_.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DP = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_whitehouse"
NS = "ewr_whitehouse"
OX, OY, OZ = -270, 72, -236           # White House site origin (local -> world)

# ------------------------------------------------------------------ posts (site-local x, y, z, yaw, role)
# yaw: 0 = facing south, 90 = west, 180 = north, -90 = east
POSTS = [
    ("Carter", 68, 8, 14, 180, "gate"), ("Reyes", 112, 8, 14, 180, "gate"),
    ("Brooks", 73, 9, 17, 180, "booth"), ("Nguyen", 106, 9, 17, 180, "booth"),
    ("Hayes", 84, 8, 39, 180, "portico"), ("Okafor", 96, 8, 39, 180, "portico"),
    ("Sullivan", 84, 8, 96, 0, "portico_s"), ("Dawson", 96, 8, 96, 0, "portico_s"),
    ("Ramirez", 59, 0, 150, 0, "gate"), ("Price", 120, 0, 150, 0, "gate"),
    ("Kowalski", 64, 1, 148, 0, "booth"), ("Mendez", 115, 1, 148, 0, "booth"),
    ("Grant", 1, 0, 56, 90, "gate"), ("Lee", 175, 0, 59, -90, "gate"),
    ("Banks", 175, 0, 136, -90, "vehicle_gate"), ("Ortiz", 172, 1, 147, -90, "vehicle_gate"),
    ("Walsh", 14, 0, 77, -30, "oval"), ("Fischer", 11, 0, 81, -60, "oval"),
    ("Coleman", 6, 0, 70, 0, "corridor"), ("Patel", 6, 0, 88, 180, "corridor"),
    ("Morgan", 32, 0, 87, -90, "garden"),
    ("Hunt", 50, 27, 50, 180, "roof"), ("Shaw", 130, 27, 80, 0, "roof"),
    ("Kane", 53, 33, 66, 90, "sniper"), ("Wolfe", 10, 17, 56, 90, "sniper"), ("Bishop", 24, 17, 79, 180, "sniper"),
    ("Steele", 52, 27, 84, 45, "sniper"), ("Knox", 128, 27, 52, -135, "sniper"), ("Vance", 127, 33, 66, -90, "sniper"), ("Archer", 90, 33, 50, 180, "sniper"),
    ("Holt", 80, 0, 109, 135, "helipad"), ("Pierce", 100, 0, 109, -135, "helipad"),
    ("Rhodes", 80, 0, 123, 45, "helipad"), ("Tanaka", 100, 0, 123, -45, "helipad"),
]
# patrols: (name, axis, fixed coords, lo, hi) along x or z at local y
PATROLS = [
    ("Miller", 'x', 8, 16, 10, 62),          # north fence line (inside the fence)
    ("Ward", 'x', 0, 149, 70, 112),          # south fence line
    ("Fox", 'z', 0, 174, 70, 130),           # east fence line
]
LINES = {
    "gate": ["Sir, this is a restricted area.", "Please stay behind the rope line.",
             "Public tours enter through the East Wing visitors' entrance.", "Keep moving, please. Thank you."],
    "booth": ["Name and ID, please.", "You're not on today's list.", "Wait here, I need to call this in."],
    "vehicle_gate": ["Authorised vehicles only. Stop at the line.", "Pop the trunk, please.",
                     "Turn off your engine and wait for clearance.", "Welcome to the White House. Drive slowly."],
    "portico": ["The President is not receiving visitors at this time.", "Please step back from the door.",
                "North Portico is closed to the public."],
    "portico_s": ["Please stay behind the rope line.", "The South Portico is off limits.", "Marine One departs from the lawn. Stand clear."],
    "oval": ["Nobody goes in without an appointment.", "POTUS is in a meeting. Please wait here.",
             "Hands where I can see them, please.", "This is the Oval Office hallway. Badge, please."],
    "corridor": ["Badge, please.", "West Wing staff only beyond this point.", "Keep to the corridor, please."],
    "garden": ["The Rose Garden is closed today.", "Please don't touch the roses."],
    "roof": ["You shouldn't be up here.", "Eyes on the perimeter.", "Roof is secure."],
    "sniper": ["Overwatch. All clear.", "Counter-sniper team. Move along.", "I've got eyes on the whole lawn."],
    "helipad": ["Marine One is inbound. Clear the lawn.", "Stay off the pad, sir.", "Rotor wash is no joke. Step back."],
    "patrol": ["Perimeter check.", "Move along, nothing to see here.", "Stay on the public side of the fence."],
}
SKINS = ["steve", "alex", "ari", "efe", "kai", "makena", "noor", "sunny", "zuri"]


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def snbt(o):
    if isinstance(o, dict):
        return "{" + ",".join(((f'"{k}"' if ":" in k else k) + ":" + snbt(v)) for k, v in o.items()) + "}"
    if isinstance(o, list):
        return "[" + ",".join(snbt(v) for v in o) + "]"
    if isinstance(o, bool):
        return "1b" if o else "0b"
    if isinstance(o, float):
        return f"{o}f"
    if isinstance(o, int):
        return str(o)
    return '"' + esc(str(o)) + '"'


def leather(item, color):
    return {"id": f"minecraft:leather_{item}", "count": 1, "components": {"minecraft:dyed_color": color}}


AGENTS = []
for i, (nm, x, y, z, yaw, role) in enumerate(POSTS):
    AGENTS.append(dict(id=f"a{i:02d}_{nm.lower()}", name=nm, x=x, y=y, z=z, yaw=yaw, role=role, patrol=None))
for j, (nm, axis, y, fixed, lo, hi) in enumerate(PATROLS):
    if axis == 'x':
        x, z, yaw = lo, fixed, -90
    else:
        x, z, yaw = fixed, lo, 0
    AGENTS.append(dict(id=f"p{j}_{nm.lower()}", name=nm, x=x, y=y, z=z, yaw=yaw, role="patrol",
                       patrol=(j, axis, y, fixed, lo, hi)))


def world(a):
    return a["x"] + OX + 0.5, a["y"] + OY, a["z"] + OZ + 0.5


# ------------------------------------------------------------------ check the posts in the live world
if "--nocheck" not in sys.argv:
    os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
    sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
    from mcmcp.server import engine
    engine.load_area("minecraft:overworld", OX, OZ, OX + 180, OZ + 156, timeout=200)
    engine.flush()
    W = engine.world
    for a in AGENTS:
        wx, wy, wz = world(a)
        feet = W.block(int(wx // 1), wy, int(wz // 1), "minecraft:overworld")
        head = W.block(int(wx // 1), wy + 1, int(wz // 1), "minecraft:overworld")
        below = W.block(int(wx // 1), wy - 1, int(wz // 1), "minecraft:overworld")
        ok = lambda s: s is None or s.endswith(":air") or "carpet" in s or "lantern" in s
        if not (ok(feet) and ok(head)) or below is None or below.endswith(":air"):
            print("CHECK", a["id"], (wx, wy, wz), "below", below, "feet", feet, "head", head)

# ------------------------------------------------------------------ functions
F = {}


def outfit(a):
    suit = 0x15161A
    eq = {"head": {"id": "minecraft:black_stained_glass_pane", "count": 1,
                   "components": {"minecraft:custom_name": {"text": "Sunglasses & earpiece", "italic": False}}},
          "chest": leather("chestplate", suit), "legs": leather("leggings", suit), "feet": leather("boots", 0x0B0B0B)}
    if a["role"] == "sniper":
        eq["mainhand"] = {"id": "minecraft:spyglass", "count": 1}
        eq["offhand"] = {"id": "minecraft:crossbow", "count": 1}
    elif a["role"] in ("helipad", "vehicle_gate", "booth"):
        eq["mainhand"] = {"id": "minecraft:paper", "count": 1}
    elif a["role"] in ("roof",):
        eq["mainhand"] = {"id": "minecraft:spyglass", "count": 1}
    return eq


spawn = ["# summon every Secret Service agent (kills ours first)", f"function {NS}:remove_all"]
for k, a in enumerate(AGENTS):
    wx, wy, wz = world(a)
    tags = ["ewhs", "ewhs_ss", f"ewhs_r_{a['role']}", f"ewhs_m_{a['id']}"]
    if a["patrol"]:
        tags += ["ewhs_patrol", f"ewhs_p{a['patrol'][0]}"]
    eq = outfit(a)
    skin = SKINS[k % len(SKINS)]
    model = "slim" if skin in ("alex", "makena", "sunny", "zuri") and k % 2 else "wide"
    m = {"Tags": tags, "CustomName": {"text": f"Agent {a['name']} \u00b7 USSS", "color": "white"}, "CustomNameVisible": True,
         "description": {"text": "U.S. Secret Service", "color": "dark_gray"},
         "profile": {"texture": f"entity/player/{model}/{skin}", "model": model},
         "Rotation": [float(a["yaw"]), 0.0], "NoGravity": True, "immovable": True, "Invulnerable": True,
         "PersistenceRequired": True, "Silent": True, "equipment": eq, "drop_chances": {s: 0.0 for s in eq}}
    spawn.append(f"summon minecraft:mannequin {wx} {wy} {wz} {snbt(m)}")
    itags = ["ewhs", "ewhs_hit"] + ([f"ewhs_p{a['patrol'][0]}hit"] if a["patrol"] else [])
    spawn.append(f'summon minecraft:interaction {wx} {wy} {wz} {{Tags:{snbt(itags)},CustomName:"{a["id"]}",'
                 f'width:0.8f,height:1.95f,response:1b}}')
    spawn.append(f"scoreboard players set @e[type=mannequin,tag=ewhs_m_{a['id']},limit=1] ewhs_yaw {int(a['yaw'])}")
spawn.append(f'tellraw @a[tag=ewhs_dev] {{text:"[ewr_whitehouse] {len(AGENTS)} Secret Service agents on post",color:"gray"}}')
F["spawn_all"] = spawn
F["remove_all"] = ["kill @e[tag=ewhs_ss]", "kill @e[type=interaction,tag=ewhs_hit]"]

F["load"] = ["scoreboard objectives add ewhs_t dummy", "scoreboard objectives add ewhs_tmp dummy",
             "scoreboard objectives add ewhs_yaw dummy", "scoreboard objectives add ewhs_cd dummy"]
F["tick"] = [
    "# clicks: only interaction boxes within 6 blocks of a player are checked",
    f"execute as @a[gamemode=!spectator] at @s as @e[type=interaction,tag=ewhs_hit,distance=..6] if data entity @s interaction run function {NS}:hit",
    "scoreboard players remove @a[scores={ewhs_cd=1..}] ewhs_cd 1",
    f"function {NS}:patrol",
    "scoreboard players add #t ewhs_t 1",
    f"execute if score #t ewhs_t matches 20.. run function {NS}:look_tick",
]
# patrols: slow walk (0.08 block/tick) along a fixed line, turning at the ends; interaction box follows
P = []
for a in AGENTS:
    if not a["patrol"]:
        continue
    j, axis, y, fixed, lo, hi = a["patrol"]
    sel = f"@e[type=mannequin,tag=ewhs_p{j},limit=1]"
    wy = y + OY
    if axis == 'x':
        wz = fixed + OZ
        x1, x2 = lo + OX, hi + OX
        P.append(f"execute as {sel} at @s if entity @s[x={x2},y={wy - 2},z={wz - 2},dx=6,dy=5,dz=5] run rotate @s 90 0")
        P.append(f"execute as {sel} at @s if entity @s[x={x1 - 6},y={wy - 2},z={wz - 2},dx=6,dy=5,dz=5] run rotate @s -90 0")
    else:
        wx = fixed + OX
        z1, z2 = lo + OZ, hi + OZ
        P.append(f"execute as {sel} at @s if entity @s[x={wx - 2},y={wy - 2},z={z2},dx=5,dy=5,dz=6] run rotate @s 180 0")
        P.append(f"execute as {sel} at @s if entity @s[x={wx - 2},y={wy - 2},z={z1 - 6},dx=5,dy=5,dz=6] run rotate @s 0 0")
    P.append(f"execute as {sel} at @s run tp @s ^ ^ ^0.08")
    P.append(f"execute as @e[type=interaction,tag=ewhs_p{j}hit,limit=1] at {sel} run tp @s ~ ~ ~")
F["patrol"] = P
F["look_tick"] = [
    "scoreboard players set #t ewhs_t 0",
    "execute as @a[gamemode=!spectator] at @s as @e[type=mannequin,tag=ewhs_ss,tag=!ewhs_patrol,distance=..7] run tag @s add ewhs_near",
    f"execute as @e[type=mannequin,tag=ewhs_near] at @s run function {NS}:look",
    f"execute as @e[type=mannequin,tag=ewhs_turned,tag=!ewhs_near] at @s unless entity @a[gamemode=!spectator,distance=..8] run function {NS}:unlook",
    "tag @e[type=mannequin,tag=ewhs_near] remove ewhs_near",
]
F["look"] = ["tp @s ~ ~ ~ facing entity @p[gamemode=!spectator] eyes", "tag @s add ewhs_turned"]
F["unlook"] = ["tag @s remove ewhs_turned",
               "execute store result storage ewr_whitehouse:t yaw float 1 run scoreboard players get @s ewhs_yaw",
               f"function {NS}:unlook_m with storage ewr_whitehouse:t"]
F["unlook_m"] = ["$rotate @s $(yaw) 0"]
F["hit"] = [
    "# as the clicked interaction entity: run its agent's line as the clicking player, then clear",
    "execute at @s as @e[type=mannequin,tag=ewhs_ss,distance=..0.6,limit=1,sort=nearest] at @s run tp @s ~ ~ ~ facing entity @p[gamemode=!spectator] eyes",
    "execute at @s as @e[type=mannequin,tag=ewhs_ss,distance=..0.6,limit=1,sort=nearest] run tag @s add ewhs_turned",
    f"function {NS}:route with entity @s",
    "data remove entity @s interaction",
    "data remove entity @s attack",
]
F["route"] = [f"$execute on target if entity @s[type=player] unless score @s ewhs_cd matches 1.. at @s run function {NS}:npc/$(CustomName)"]
for a in AGENTS:
    lines = LINES[a["role"]]
    L = ["scoreboard players set @s ewhs_cd 10",
         f"execute store result score #r ewhs_tmp run random value 1..{len(lines)}"]
    for k, line in enumerate(lines, 1):
        L.append(f'execute if score #r ewhs_tmp matches {k} run tellraw @s [{{text:"[Agent {a["name"]} \u00b7 USSS] ",color:"dark_gray"}},{{text:"{esc(line)}",color:"white"}}]')
    F[f"npc/{a['id']}"] = L
F["help"] = ['tellraw @s {text:"--- White House Secret Service ---",color:"white",bold:true}',
             f'tellraw @s {{text:"{len(AGENTS)} agents. Right-click one to talk. Admin: function {NS}:spawn_all | {NS}:remove_all",color:"gray"}}']

exec(open(os.path.join(HERE, "sec.py"), encoding="utf-8").read())

# ------------------------------------------------------------------ write
if os.path.isdir(DP):
    shutil.rmtree(DP)
fd = os.path.join(DP, "data", NS, "function")
for name, lines in F.items():
    path = os.path.join(fd, *name.split("/")) + ".mcfunction"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
tg = os.path.join(DP, "data", "minecraft", "tags", "function")
os.makedirs(tg, exist_ok=True)
json.dump({"values": [f"{NS}:load"]}, open(os.path.join(tg, "load.json"), "w"))
json.dump({"values": [f"{NS}:tick"]}, open(os.path.join(tg, "tick.json"), "w"))
json.dump({"pack": {"description": "White House: Secret Service agents (mannequins + interactions)",
                    "min_format": [121, 0], "max_format": [200, 0]}}, open(os.path.join(DP, "pack.mcmeta"), "w"), indent=1)
json.dump([{k: a[k] for k in ("id", "name", "role", "x", "y", "z", "yaw")} | {"world": world(a)} for a in AGENTS],
          open(os.path.join(HERE, "roster.json"), "w"), indent=0)
print(f"{len(AGENTS)} agents, {len(F)} functions -> {DP}")
