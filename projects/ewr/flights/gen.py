"""Generate the ewr_flights datapack: automated "Burj Khalifa Scenic Flight" (Emirates EK 2026).

    python gen.py            writes server/world/datapacks/ewr_flights (then /reload)

Vanilla Java 26.3, data pack format 121. Everything is precomputed here (route.py / flight.py):
the plane is a set of block_display parts (ewr_planes geometry, Emirates livery) that all sit at the
plane centre; each tick they are teleported (teleport_duration 1) with yaw + pitch, while bank is baked
into their transformations as keyframes every 4 ticks (client-interpolated). Passengers ride invisible
item_display seats that are teleported to their seat points each tick.

Entity tags: ewr_flt_*   Scoreboards: ewrf_*   Storage: ewr_flights:*
"""
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flight as FL  # noqa: E402
import model as MD  # noqa: E402
import route as RT  # noqa: E402

PACK = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_flights"
NS = "ewr_flights"

PERIOD = 4800                 # a departure every 4 minutes
BOARD_T = 400                 # plane boards at the stand for 20 s; leaves at flight tick 400
GATE = (-14.5, 73.0, 212.5)   # boarding point: Terminal A north airside lounge, window to the stand
GATE_YAW = -115.0             # looking out at the plane
GATE_NAME = "A10"
GATE_RADIUS = 32
FLIGHT_NAME = "Burj Scenic Flight"
FLIGHT_NO = "EK 2026"
PRICE = 350
BOARD_POS = (-13.7, 74.9, 210.2)   # departures board (text display) just inside the east glass wall
SEATS_Z = [6.0 - 1.6 * k for k in range(8)]
SEAT_DROP = 0.77              # seat point below the fuselage axis (player eyes ~0.25 above the axis)
BUCKET = 50


def f3(v):
    s = f"{v:.3f}"
    return "0.0" if s in ("-0.000", "0.000") else s


def f2(v):
    s = f"{v:.2f}"
    return "0.0" if s in ("-0.00", "0.00") else s


def W(rel, text):
    path = os.path.join(PACK, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.strip("\n") + "\n")


def F(name, lines):
    W(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) if isinstance(lines, list) else lines)


def tj(obj):
    return json.dumps(obj, ensure_ascii=False)


def say(msg, color="white"):
    return 'tellraw @s [{"text":"[Burj Scenic] ","color":"gold"},%s]' % tj({"text": msg, "color": color})


def main():
    TL, info, paths = FL.build()
    n = len(TL)
    A = BOARD_T + n                     # arrival tick (plane stopped at the stand)
    assert A + 20 < PERIOD, (A, PERIOD)
    sx, sz, syaw = RT.STAND
    sy = MD.CENTRE_GROUND
    if os.path.isdir(PACK):
        shutil.rmtree(PACK)
    W("pack.mcmeta", json.dumps({"pack": {
        "description": f"EWR automated scenic flights: {FLIGHT_NAME} ({FLIGHT_NO}) around the Burj Khalifa",
        "min_format": [121, 0], "max_format": [121, 0]}}, indent=2))
    W("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
    W("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))

    # ------------------------------------------------------------------ plane: summon at the stand
    parts = MD.PARTS
    lines = [f"# new plane at stand {GATE_NAME}: brain marker + {len(parts)} parts + {len(SEATS_Z)} seats",
             "scoreboard players add #next ewrf_id 1",
             f"summon marker {f3(sx)} {f3(sy)} {f3(sz)} {{Tags:[\"ewr_flt\",\"ewr_flt_brain\",\"ewr_flt_new\"],Rotation:[{syaw}f,0f]}}"]
    for i, p in enumerate(parts):
        nbt = ("{Tags:[\"ewr_flt\",\"ewr_flt_part\",\"ewr_flt_p%d\",\"ewr_flt_new\"],block_state:\"minecraft:%s\","
               "teleport_duration:1,interpolation_duration:%d,view_range:3f,Rotation:[%sf,0f],transformation:%s}"
               % (i, p.block, FL.RK, syaw, MD.part_nbt(p, 0.0, i)))
        lines.append(f"summon block_display {f3(sx)} {f3(sy)} {f3(sz)} {nbt}")
    M = MD.rot_matrix(syaw, 0, 0)
    for k, zk in enumerate(SEATS_Z):
        o = (0.0, -SEAT_DROP, zk)
        w = [sx + sum(M[0][j] * o[j] for j in range(3)), sy + sum(M[1][j] * o[j] for j in range(3)),
             sz + sum(M[2][j] * o[j] for j in range(3))]
        lines.append(f"summon item_display {f3(w[0])} {f3(w[1])} {f3(w[2])} "
                     f"{{Tags:[\"ewr_flt\",\"ewr_flt_seat\",\"ewr_flt_s{k}\",\"ewr_flt_new\"],teleport_duration:1}}")
    lines += [
        "scoreboard players operation @e[tag=ewr_flt_new] ewrf_id = #next ewrf_id",
    ] + [f"scoreboard players set @e[tag=ewr_flt_new,tag=ewr_flt_s{k}] ewrf_seat {k}" for k in range(len(SEATS_Z))] + [
        "scoreboard players set @e[tag=ewr_flt_new,tag=ewr_flt_brain] ewrf_ft 0",
        "scoreboard players operation @e[tag=ewr_flt_new,tag=ewr_flt_brain] ewrf_ep = #epoch ewrf_t",
        "tag @e[tag=ewr_flt_new] remove ewr_flt_new",
    ]
    F("internal/spawn", lines)

    # ------------------------------------------------------------------ roll levels (keyframes)
    levels = sorted({st["roll_kf"] for st in TL if st["roll_kf"] is not None} | {0.0})
    lvname = lambda v: ("p%d" % round(v)) if v >= 0 else ("m%d" % round(-v))
    for lv in levels:
        lines = [f"# bank {lv:+.0f} deg: every part's transformation (as + at the brain, parts at the brain)"]
        for i, p in enumerate(parts):
            lines.append(f"data merge entity @e[type=block_display,tag=ewr_flt_p{i},distance=..0.6,limit=1] "
                         f"{{start_interpolation:0,transformation:{MD.part_nbt(p, lv, i)}}}")
        F(f"roll/{lvname(lv)}", lines)

    # ------------------------------------------------------------------ motion: per-tick lines
    seat_lines = [f"$execute positioned $(x) $(y) $(z) rotated $(w) $(p) as @e[type=item_display,tag=ewr_flt_s{k},"
                  f"distance=..16] if score @s ewrf_id = #cur ewrf_id run tp @s ^$(a) ^$(b) ^{zk:.2f}"
                  for k, zk in enumerate(SEATS_Z)]
    F("fx/mv", [
        "# one motion step (as + at the brain): parts (at the brain) -> new pose, seats -> seat points, brain",
        "$execute as @e[type=block_display,tag=ewr_flt_part,distance=..0.6] if score @s ewrf_id = #cur ewrf_id run tp @s $(x) $(y) $(z) $(w) $(p)",
    ] + seat_lines + ["$tp @s $(x) $(y) $(z) $(w) $(p)"])
    buckets = {}
    for i, st in enumerate(TL):
        ft = BOARD_T + i
        r = math.radians(st["roll"])
        a, b = SEAT_DROP * math.sin(r), -SEAT_DROP * math.cos(r)
        yaw = (st["yaw"] + 180.0) % 360.0 - 180.0
        ls = buckets.setdefault(i // BUCKET, [])
        if st["roll_kf"] is not None:
            ls.append(f"execute if score @s ewrf_ft matches {ft} run function {NS}:roll/{lvname(st['roll_kf'])}")
        prev = TL[i - 1] if i else None
        if prev and all(abs(prev[k] - st[k]) < 1e-6 for k in ("x", "y", "z", "yaw", "pitch", "roll")):
            continue                                    # standing still: nothing to send
        ls.append(f"execute if score @s ewrf_ft matches {ft} run return run function {NS}:fx/mv "
                  f"{{x:\"{f3(st['x'])}\",y:\"{f3(st['y'])}\",z:\"{f3(st['z'])}\",w:\"{f2(yaw)}\",p:\"{f2(st['pitch'])}\","
                  f"a:\"{f3(a)}\",b:\"{f3(b)}\"}}")
    groups = {}
    for k, ls in buckets.items():
        F(f"path/b{k}", [f"# flight ticks {BOARD_T + k * BUCKET}..{BOARD_T + k * BUCKET + BUCKET - 1}"] + ls)
        groups.setdefault(k // 10, []).append(k)
    disp = ["# as + at a brain in motion: run this tick's step"]
    for g, ks in sorted(groups.items()):
        lo, hi = BOARD_T + ks[0] * BUCKET, BOARD_T + ks[-1] * BUCKET + BUCKET - 1
        disp.append(f"execute if score @s ewrf_ft matches {lo}..{hi} run return run function {NS}:path/g{g}")
        F(f"path/g{g}", [f"execute if score @s ewrf_ft matches {BOARD_T + k * BUCKET}..{BOARD_T + k * BUCKET + BUCKET - 1} "
                         f"run return run function {NS}:path/b{k}" for k in ks])
    F("path/dispatch", disp)

    # ------------------------------------------------------------------ load / tick
    gx, gy, gz = GATE
    F("load", [
        "scoreboard objectives add ewrf_t dummy",
        "scoreboard objectives add ewrf_id dummy",
        "scoreboard objectives add ewrf_ft dummy",
        "scoreboard objectives add ewrf_seat dummy",
        "scoreboard objectives add ewrf_ep dummy",
        "execute unless score #next ewrf_id matches 0.. run scoreboard players set #next ewrf_id 0",
        "execute unless score #epoch ewrf_t matches 0.. run scoreboard players set #epoch ewrf_t 0",
        f"execute unless score #clock ewrf_t matches 0.. run scoreboard players set #clock ewrf_t {PERIOD - 1}",
        "scoreboard players set #t20 ewrf_t 0",
        f"function {NS}:internal/forceload",
        f"schedule function {NS}:internal/ensure_board 40t replace",
    ])
    F("tick", [
        "scoreboard players add #clock ewrf_t 1",
        f"execute if score #clock ewrf_t matches {PERIOD}.. run scoreboard players set #clock ewrf_t 0",
        f"execute if score #clock ewrf_t matches 0 run function {NS}:internal/cycle",
        f"execute as @e[type=marker,tag=ewr_flt_brain] at @s run function {NS}:internal/brain_tick",
        "scoreboard players add #t20 ewrf_t 1",
        f"execute if score #t20 ewrf_t matches 20.. run function {NS}:internal/second",
    ])
    F("internal/brain_tick", [
        "scoreboard players add @s ewrf_ft 1",
        "scoreboard players operation #cur ewrf_id = @s ewrf_id",
        f"execute if score @s ewrf_ft matches {BOARD_T} run function {NS}:internal/depart",
        f"execute if score @s ewrf_ft matches {BOARD_T}..{A - 1} run function {NS}:path/dispatch",
        f"execute if score @s ewrf_ft matches {BOARD_T}..{A - 1} run function {NS}:internal/pax_all",
        f"execute if score @s ewrf_ft matches {A} run function {NS}:internal/arrive",
        f"execute if score @s ewrf_ft matches 100000.. run scoreboard players set @s ewrf_ft {A + 1}",
    ])

    # ------------------------------------------------------------------ schedule
    F("internal/cycle", [
        "# every 4 minutes: next departure starts boarding (re-use the plane parked at the stand)",
        "scoreboard players add #epoch ewrf_t 1",
        f"function {NS}:internal/forceload",
        # stale flights (stuck, e.g. their chunks were unloaded for a whole cycle): remove
        f"execute as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=..{A - 1}}}] run function {NS}:internal/stale_check",
        "scoreboard players set #ok ewrf_t 0",
        f"execute if entity @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=..{BOARD_T - 1}}}] run scoreboard players set #ok ewrf_t 1",
        f"execute if score #ok ewrf_t matches 0 as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={A}..}},limit=1] store success score #ok ewrf_t run scoreboard players set @s ewrf_ft 0",
        f"execute as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=0}}] run scoreboard players operation @s ewrf_ep = #epoch ewrf_t",
        f"execute if score #ok ewrf_t matches 0 run function {NS}:internal/spawn",
    ])
    F("internal/stale_check", [
        "scoreboard players operation #age ewrf_t = #epoch ewrf_t",
        "scoreboard players operation #age ewrf_t -= @s ewrf_ep",
        f"execute if score #age ewrf_t matches 2.. at @s run function {NS}:internal/despawn",
    ])
    F("depart_now", [
        "# (ops) depart immediately; the 4-minute schedule restarts from now",
        f"execute store result score #air ewrf_t if entity @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={BOARD_T}..{A - 1}}}]",
        f"execute if score #air ewrf_t matches 2.. run return run {say('Two flights are already in the air (maximum). Try again later.', 'red')}",
        "scoreboard players set #ok ewrf_t 0",
        f"execute as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=..{BOARD_T - 1}}},limit=1] store success score #ok ewrf_t run scoreboard players set @s ewrf_ft {BOARD_T - 1}",
        f"execute if score #ok ewrf_t matches 0 as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={A}..}},limit=1] store success score #ok ewrf_t run scoreboard players set @s ewrf_ft {BOARD_T - 1}",
        f"execute if score #ok ewrf_t matches 0 run function {NS}:internal/spawn",
        f"execute if score #ok ewrf_t matches 0 as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=0}}] run scoreboard players set @s ewrf_ft {BOARD_T - 1}",
        f"execute as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={BOARD_T - 1}}}] run scoreboard players operation @s ewrf_ep = #epoch ewrf_t",
        f"scoreboard players set #clock ewrf_t {BOARD_T - 1}",
        say(f"{FLIGHT_NAME} departing now from gate {GATE_NAME}. Next scheduled departure in 4:00.", "green"),
    ])

    # ------------------------------------------------------------------ boarding / passengers
    F("book", [
        f"# Book the caller on the next {FLIGHT_NAME} (run as the player). Ticket desks call it through",
        f"# function ewr_econ:try_buy {{price:{PRICE}, item:\"{FLIGHT_NAME}\", then:\"{NS}:book\"}}",
        f"execute if entity @s[tag=ewr_flt_pax] run return run {say('You are already on board this flight.', 'yellow')}",
        "tag @s add ewr_flt_booked",
        f"tp @s {gx} {gy} {gz} {GATE_YAW} 0",
        f"function {NS}:internal/countdown",
        "title @s times 10 70 20",
        f"title @s title {tj({'text': f'Boarding: {FLIGHT_NAME}, gate {GATE_NAME}', 'color': 'gold'})}",
        f"function {NS}:internal/sub_title with storage {NS}:b",
        say(f"Booked on {FLIGHT_NO} {FLIGHT_NAME}. Wait here at gate {GATE_NAME} (Terminal A) - you are seated "
            f"automatically when the flight leaves. Your plane is the Emirates jet outside the window.", "white"),
        "playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 1.2",
        "return 1",
    ])
    F("internal/sub_title", [
        "$title @s subtitle {\"text\":\"Departs in $(m):$(s10)$(s1)  -  Emirates EK 2026\",\"color\":\"yellow\"}",
    ])
    F("internal/depart", [
        "# flight leaves the stand: seat booked passengers waiting at the gate (as + at the brain)",
        "scoreboard players set #seat ewrf_t 0",
        f"execute positioned {gx} {gy} {gz} as @e[tag=ewr_flt_booked,distance=..{GATE_RADIUS},sort=nearest] run function {NS}:internal/board_one",
        f"execute as @a[tag=ewr_flt_booked] run {say('You missed this departure (not at the gate). You stay booked for the next one.', 'yellow')}",
        "playsound minecraft:block.note_block.bell master @a[tag=ewr_flt_pax] ~ ~ ~ 0.6 0.8",
    ])
    F("internal/board_one", [
        f"execute if score #seat ewrf_t matches {len(SEATS_Z)}.. run return run {say('This flight is full - you are booked on the next one.', 'yellow')}",
        "scoreboard players operation @s ewrf_id = #cur ewrf_id",
        "scoreboard players operation @s ewrf_seat = #seat ewrf_t",
        "scoreboard players add #seat ewrf_t 1",
        "tag @s remove ewr_flt_booked",
        "tag @s add ewr_flt_pax",
        f"function {NS}:internal/protect",
        "title @s[type=player] times 10 60 20",
        f"title @s[type=player] subtitle {tj({'text': 'Pushback - taxi - takeoff from 04L - orbit the Burj Khalifa', 'color': 'yellow'})}",
        f"title @s[type=player] title {tj({'text': f'Welcome aboard {FLIGHT_NO}', 'color': 'gold'})}",
    ])
    F("internal/protect", [
        "effect give @s[type=player] minecraft:resistance 40 4 true",
        "effect give @s[type=player] minecraft:slow_falling 40 0 true",
        "effect give @s[type=player] minecraft:fire_resistance 40 0 true",
    ])
    F("internal/pax_all", [
        f"execute as @e[tag=ewr_flt_pax] if score @s ewrf_id = #cur ewrf_id run function {NS}:internal/pax_tick",
    ])
    F("internal/pax_tick", [
        "# keep the passenger in their seat (re-seat after sneaking out / any dismount)",
        "scoreboard players set #onv ewrf_t 0",
        "execute on vehicle if entity @s[type=item_display,tag=ewr_flt_seat] if score @s ewrf_id = #cur ewrf_id run scoreboard players set #onv ewrf_t 1",
        "execute if score #onv ewrf_t matches 1 run return 0",
        "scoreboard players operation #ps ewrf_seat = @s ewrf_seat",
        "execute as @e[type=item_display,tag=ewr_flt_seat,distance=..64] if score @s ewrf_id = #cur ewrf_id if score @s ewrf_seat = #ps ewrf_seat run tag @s add ewr_flt_tgt",
        "execute unless entity @e[type=item_display,tag=ewr_flt_tgt] as @e[type=item_display,tag=ewr_flt_seat] if score @s ewrf_id = #cur ewrf_id if score @s ewrf_seat = #ps ewrf_seat run tag @s add ewr_flt_tgt",
        "ride @s dismount",
        "execute at @e[type=item_display,tag=ewr_flt_tgt,limit=1] run tp @s ~ ~ ~",
        "ride @s mount @e[type=item_display,tag=ewr_flt_tgt,limit=1]",
        "tag @e[type=item_display,tag=ewr_flt_tgt] remove ewr_flt_tgt",
    ])
    F("internal/arrive", [
        "# parked at the stand: release the passengers at the gate; tow away any older parked plane",
        f"execute as @e[tag=ewr_flt_pax] if score @s ewrf_id = #cur ewrf_id run function {NS}:internal/release_one",
        "tag @s add ewr_flt_self",
        f"execute as @e[type=marker,tag=ewr_flt_brain,tag=!ewr_flt_self,scores={{ewrf_ft={A}..}}] at @s run function {NS}:internal/despawn",
        "tag @s remove ewr_flt_self",
        "scoreboard players operation #cur ewrf_id = @s ewrf_id",
    ])
    F("internal/release_one", [
        "ride @s dismount",
        f"tp @s {gx} {gy} {gz} {GATE_YAW} 0",
        "effect clear @s[type=player] minecraft:slow_falling",
        "effect clear @s[type=player] minecraft:resistance",
        "effect clear @s[type=player] minecraft:fire_resistance",
        "tag @s remove ewr_flt_pax",
        "scoreboard players reset @s ewrf_id",
        "scoreboard players reset @s ewrf_seat",
        "title @s[type=player] times 10 60 20",
        f"title @s[type=player] subtitle {tj({'text': 'Thank you for flying the Burj Scenic Flight', 'color': 'yellow'})}",
        f"title @s[type=player] title {tj({'text': f'Welcome back to Newark - gate {GATE_NAME}', 'color': 'gold'})}",
        "playsound minecraft:block.note_block.bell master @s[type=player] ~ ~ ~ 1 1.2",
    ])
    F("internal/despawn", [
        "# remove this plane (as + at its brain); passengers go back to the gate",
        "scoreboard players operation #dead ewrf_id = @s ewrf_id",
        "scoreboard players operation #keep ewrf_id = #cur ewrf_id",
        "scoreboard players operation #cur ewrf_id = #dead ewrf_id",
        f"execute as @e[tag=ewr_flt_pax] if score @s ewrf_id = #dead ewrf_id run function {NS}:internal/release_one",
        "execute as @e[type=block_display,tag=ewr_flt_part] if score @s ewrf_id = #dead ewrf_id run kill @s",
        "execute as @e[type=item_display,tag=ewr_flt_seat] if score @s ewrf_id = #dead ewrf_id run kill @s",
        "scoreboard players operation #cur ewrf_id = #keep ewrf_id",
        "kill @s",
    ])

    # ------------------------------------------------------------------ once a second
    F("internal/second", [
        "scoreboard players set #t20 ewrf_t 0",
        f"function {NS}:internal/countdown",
        f"execute if entity @a[tag=ewr_flt_booked] run function {NS}:internal/actionbar with storage {NS}:b",
        f"function {NS}:internal/board_text with storage {NS}:b",
        f"execute as @a[tag=ewr_flt_pax] run function {NS}:internal/orphan_check",
        "scoreboard players add #t5 ewrf_t 1",
        f"execute if score #t5 ewrf_t matches 10.. run function {NS}:internal/every10",
    ])
    F("internal/every10", [
        "scoreboard players set #t5 ewrf_t 0",
        f"execute as @a[tag=ewr_flt_pax] run function {NS}:internal/protect",
        f"execute as @e[type=block_display,tag=ewr_flt_part] run function {NS}:internal/orphan_part",
        f"execute as @e[type=item_display,tag=ewr_flt_seat] run function {NS}:internal/orphan_part",
        f"function {NS}:internal/ensure_board",
    ])
    F("internal/orphan_part", [
        "scoreboard players operation #p ewrf_id = @s ewrf_id",
        "scoreboard players set #found ewrf_t 0",
        "execute as @e[type=marker,tag=ewr_flt_brain] if score @s ewrf_id = #p ewrf_id run scoreboard players set #found ewrf_t 1",
        "execute if score #found ewrf_t matches 0 run kill @s",
    ])
    F("internal/orphan_check", [
        "# passenger whose flight is gone or already parked (e.g. logged out mid-flight): back to the gate",
        "scoreboard players operation #p ewrf_id = @s ewrf_id",
        "scoreboard players set #found ewrf_t 0",
        f"execute as @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={BOARD_T}..{A - 1}}}] if score @s ewrf_id = #p ewrf_id run scoreboard players set #found ewrf_t 1",
        f"execute if score #found ewrf_t matches 0 run function {NS}:internal/release_one",
    ])
    F("internal/countdown", [
        "# seconds until the next departure -> storage ewr_flights:b {m, s10, s1, st}",
        f"scoreboard players set #rem ewrf_t {BOARD_T}",
        "scoreboard players operation #rem ewrf_t -= #clock ewrf_t",
        f"execute if score #rem ewrf_t matches ..0 run scoreboard players add #rem ewrf_t {PERIOD}",
        "scoreboard players add #rem ewrf_t 19",
        "scoreboard players set #c20 ewrf_t 20",
        "scoreboard players operation #rem ewrf_t /= #c20 ewrf_t",
        "scoreboard players set #c60 ewrf_t 60",
        "scoreboard players set #c10 ewrf_t 10",
        "scoreboard players operation #m ewrf_t = #rem ewrf_t",
        "scoreboard players operation #m ewrf_t /= #c60 ewrf_t",
        "scoreboard players operation #s ewrf_t = #rem ewrf_t",
        "scoreboard players operation #s ewrf_t %= #c60 ewrf_t",
        "scoreboard players operation #s10 ewrf_t = #s ewrf_t",
        "scoreboard players operation #s10 ewrf_t /= #c10 ewrf_t",
        "scoreboard players operation #s1 ewrf_t = #s ewrf_t",
        "scoreboard players operation #s1 ewrf_t %= #c10 ewrf_t",
        f"execute store result storage {NS}:b m int 1 run scoreboard players get #m ewrf_t",
        f"execute store result storage {NS}:b s10 int 1 run scoreboard players get #s10 ewrf_t",
        f"execute store result storage {NS}:b s1 int 1 run scoreboard players get #s1 ewrf_t",
        f"data modify storage {NS}:b st set value \"ON TIME\"",
        f"execute if entity @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft=..{BOARD_T - 1}}}] run data modify storage {NS}:b st set value \"BOARDING\"",
        f"execute store result score #air ewrf_t if entity @e[type=marker,tag=ewr_flt_brain,scores={{ewrf_ft={BOARD_T}..{A - 1}}}]",
        f"data modify storage {NS}:b air set value \"\"",
        f"execute if score #air ewrf_t matches 1.. run data modify storage {NS}:b air set value \"Previous flight: airborne / taxiing\"",
    ])
    F("internal/actionbar", [
        "$title @a[tag=ewr_flt_booked] actionbar {\"text\":\"Burj Scenic Flight - gate A10 - departs in $(m):$(s10)$(s1)  ($(st))\",\"color\":\"gold\"}",
    ])
    bx, by, bz = BOARD_POS
    F("internal/board_text", [
        "$data merge entity @e[type=text_display,tag=ewr_flt_board,limit=1] {text:{text:\"\",extra:["
        "{text:\"EMIRATES  EK 2026\\n\",color:\"gold\",bold:true},"
        "{text:\"BURJ KHALIFA SCENIC FLIGHT\\n\",color:\"white\",bold:true},"
        "{text:\"Gate A10  -  Terminal A\\n\",color:\"aqua\"},"
        "{text:\"Next departure in $(m):$(s10)$(s1)\\n\",color:\"yellow\"},"
        "{text:\"Status: $(st)\\n\",color:\"green\"},"
        "{text:\"Every 4 min  -  about 3 min  -  $350\\n\",color:\"gray\"},"
        "{text:\"$(air)\",color:\"dark_gray\"}]}}",
    ])
    F("internal/ensure_board", [
        f"execute unless loaded {math.floor(bx)} {math.floor(by)} {math.floor(bz)} run return 0",
        f"execute positioned {bx} {by} {bz} run tag @e[type=text_display,tag=ewr_flt_board,sort=nearest,limit=1] add ewr_flt_keep",
        "kill @e[type=text_display,tag=ewr_flt_board,tag=!ewr_flt_keep]",
        "tag @e[type=text_display,tag=ewr_flt_board] remove ewr_flt_keep",
        f"execute unless entity @e[type=text_display,tag=ewr_flt_board] run summon text_display {bx} {by} {bz} "
        "{Tags:[\"ewr_flt\",\"ewr_flt_board\"],billboard:\"vertical\",alignment:\"center\",line_width:220,"
        "background:-1442840576,view_range:0.6f,transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],"
        "translation:[0f,0f,0f],scale:[0.55f,0.55f,0.55f]},text:{text:\"EMIRATES  EK 2026\",color:\"gold\"}}",
        f"function {NS}:internal/countdown",
        f"function {NS}:internal/board_text with storage {NS}:b",
    ])

    # ------------------------------------------------------------------ chunk loading for the route
    chunks = set()
    for st in TL:
        for dx in (-16, 0, 16):
            for dz in (-16, 0, 16):
                chunks.add((math.floor((st["x"] + dx * 0.44) / 16), math.floor((st["z"] + dz * 0.44) / 16)))
    chunks.add((math.floor(GATE[0] / 16), math.floor(GATE[2] / 16)))
    rows = {}
    for cx, cz in chunks:
        rows.setdefault(cz, []).append(cx)
    fl = ["# keep the flight route loaded (planes fly where no player may be); re-asserted every departure"]
    nrect = 0
    for cz in sorted(rows):
        xs = sorted(rows[cz])
        run = [xs[0], xs[0]]
        for cx in xs[1:] + [None]:
            if cx is not None and cx == run[1] + 1:
                run[1] = cx
                continue
            fl.append(f"forceload add {run[0] * 16} {cz * 16} {run[1] * 16 + 15} {cz * 16 + 15}")
            nrect += 1
            if cx is not None:
                run = [cx, cx]
    F("internal/forceload", fl)
    F("internal/unforceload", [l.replace("forceload add", "forceload remove") for l in fl])

    # ------------------------------------------------------------------ admin
    F("reset", [
        "# (ops) remove all scenic-flight planes, return passengers to the gate, restart the schedule",
        f"execute as @e[type=marker,tag=ewr_flt_brain] at @s run function {NS}:internal/despawn",
        "kill @e[type=block_display,tag=ewr_flt_part]",
        "kill @e[type=item_display,tag=ewr_flt_seat]",
        f"execute as @e[tag=ewr_flt_pax] run function {NS}:internal/release_one",
        f"scoreboard players set #clock ewrf_t {PERIOD - 1}",
        say("Scenic flights reset; a new plane appears at the stand next tick.", "green"),
    ])
    F("cancel", [
        "# (as a player) cancel your booking",
        "tag @s remove ewr_flt_booked",
        say("Booking cancelled.", "yellow"),
    ])
    F("status", [
        f"function {NS}:internal/countdown",
        f"function {NS}:internal/status_msg with storage {NS}:b",
    ])
    F("internal/status_msg", [
        f"$tellraw @s [{{\"text\":\"[Burj Scenic] \",\"color\":\"gold\"}},{{\"text\":\"Next departure from gate {GATE_NAME} in $(m):$(s10)$(s1) ($(st)). $(air)\",\"color\":\"white\"}}]",
    ])
    F("help", [
        'tellraw @s {"text":"--- Burj Khalifa Scenic Flight (Emirates EK 2026) ---","color":"gold","bold":true}',
        f'tellraw @s {{"text":"Book: /function {NS}:book  (ticket desks sell it for ${PRICE}). You are sent to gate {GATE_NAME} (Terminal A north lounge) and seated when the flight leaves.","color":"white"}}',
        'tellraw @s {"text":"Departures every 4 minutes, about 3 minutes gate to gate: pushback, taxi, takeoff 04L, climb, one orbit of the Burj at y 222, landing 22R.","color":"white"}',
        f'tellraw @s {{"text":"Status: /function {NS}:status   Cancel booking: /function {NS}:cancel   Ops: /function {NS}:depart_now | {NS}:reset","color":"gray"}}',
    ])

    nfun = sum(len(fs) for _, _, fs in os.walk(os.path.join(PACK, "data", NS, "function")))
    print(f"pack: {nfun} functions; flight {n} ticks ({n / 20:.0f} s), arrive at ft {A}, period {PERIOD};"
          f" {len(parts)} parts, roll levels {len(levels)}, keyframes {info['keyframes']}; forceload {len(chunks)} chunks in {nrect} rects")
    meta = dict(PERIOD=PERIOD, BOARD_T=BOARD_T, A=A, n=n, GATE=GATE, STAND=RT.STAND, parts=len(parts),
                chunks=sorted(chunks), info={k: v for k, v in info.items() if isinstance(v, (int, float))})
    json.dump(meta, open(os.path.join(HERE, "meta.json"), "w"), indent=1)
    with open(os.path.join(HERE, "timeline.json"), "w") as fh:
        json.dump([{k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items()} for st in TL], fh)


if __name__ == "__main__":
    main()
