"""Generator for the ewr_cars datapack (drivable Ferraris / Lamborghinis, vanilla 26.3).

Car = tamed, saddled, invisible, scaled-down horse (the thing you ride) + ~40 block_display parts that share
the horse's position and are rotated to its yaw every tick (all parts sit at the horse origin; their shape
comes from the display transformation, so rotating the entity rotates the whole car rigidly) + one
interaction entity (a big click target that mounts you).

Run:  python gen.py            -> writes the pack into the server's world/datapacks/ewr_cars and parts.json
"""
import json, math, os, shutil

PACK = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_cars"
HERE = os.path.dirname(os.path.abspath(__file__))
NS = "ewr_cars"

SPEED = 0.55          # movement_speed while driven (vanilla horse max 0.3375)
JUMP = 0.25           # jump_strength (low: cars don't jump much)
STEP = 1.1            # step_height (climbs slabs/blocks; vanilla gives >=1 when ridden by a player)
SCALE = 0.35          # horse scale -> rider sits low in the cockpit
PREDICT = 2           # ticks of position extrapolation for the body while driving (hides network lag)

# --------------------------------------------------------------------------------------------------
# geometry helpers: car-local coords, +z = forward (nose), +y up, x lateral; origin = horse feet
# --------------------------------------------------------------------------------------------------

def qx(a):  # quaternion [x,y,z,w] for rotation a (radians) about X
    return [math.sin(a / 2), 0.0, 0.0, math.cos(a / 2)]

def qy(a):
    return [0.0, math.sin(a / 2), 0.0, math.cos(a / 2)]

def qz(a):
    return [0.0, 0.0, math.sin(a / 2), math.cos(a / 2)]

def qrot(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    # v' = q v q*
    tx = 2 * (y * vz - z * vy); ty = 2 * (z * vx - x * vz); tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx))


class Car:
    def __init__(self):
        self.parts = []

    def box(self, x1, y1, z1, x2, y2, z2, block, glow=False):
        x1, x2 = sorted((x1, x2)); y1, y2 = sorted((y1, y2)); z1, z2 = sorted((z1, z2))
        self.parts.append(dict(block=block, t=[x1, y1, z1], s=[x2 - x1, y2 - y1, z2 - z1],
                               q=[0.0, 0.0, 0.0, 1.0], glow=glow))

    def sym(self, x1, y1, z1, x2, y2, z2, block, glow=False):
        """box and its mirror across x=0"""
        self.box(x1, y1, z1, x2, y2, z2, block, glow)
        self.box(-x1, y1, z1, -x2, y2, z2, block, glow)

    def rbox(self, center, size, q, block, glow=False):
        """box of `size` centred on `center`, rotated by quaternion q about its centre"""
        h = qrot(q, (size[0] / 2, size[1] / 2, size[2] / 2))
        t = [center[0] - h[0], center[1] - h[1], center[2] - h[2]]
        self.parts.append(dict(block=block, t=t, s=list(size), q=q, glow=glow))

    def slope(self, x1, x2, za, ya, zb, yb, thick, block, glow=False):
        """panel whose TOP surface runs from (za,ya) to (zb,yb) (za<zb), spanning x1..x2, `thick` deep below it"""
        dz, dy = zb - za, yb - ya
        L = math.hypot(dz, dy)
        a = math.atan2(-dy, dz)        # R_x(a) maps +z onto the slope direction
        q = qx(a)
        n = qrot(q, (0, 1, 0))         # panel "up" normal
        cx = (x1 + x2) / 2
        cy = (ya + yb) / 2 - n[1] * thick / 2
        cz = (za + zb) / 2 - n[2] * thick / 2
        self.rbox((cx, cy, cz), (abs(x2 - x1), thick, L), q, block, glow)

    def wheel(self, x, z, side, rim, r=0.4, w=0.36):
        """side=+1/-1 (outer face direction). Octagonal tyre (two boxes, one turned 45 deg) + rim + hub"""
        cy = r
        cx = x
        for a in (0.0, math.pi / 6, math.pi / 3):
            self.rbox((cx, cy, z), (w, 2 * r * 0.88, 2 * r * 0.88), qx(a), "black_concrete")
        # rim disc on the outer face (two squares -> 8 spokes look)
        ox = cx + side * (w / 2 + 0.005)
        for a in (0.0, math.pi / 4):
            self.rbox((ox, cy, z), (0.02, 0.48, 0.48), qx(a), rim)
        self.rbox((ox + side * 0.012, cy, z), (0.02, 0.16, 0.16), qx(math.pi / 8), "black_concrete")
        # brake caliper (yellow/red) peeking
        self.rbox((ox - side * 0.01, cy + 0.12, z - 0.12), (0.02, 0.12, 0.08), qx(0.6), "red_concrete" if rim != "gold_block" else "yellow_concrete")


def build_car(kind, body, accent, rim, wing_block):
    """kind: 'ferrari' | 'lambo'"""
    c = Car()
    L, W = 2.8, 1.12          # half length, half width
    # ---------------- wheels ----------------
    for z in (1.75, -1.7):
        c.wheel(0.93, z, +1, rim)
        c.wheel(-0.93, z, -1, rim)
    # ---------------- chassis / lower body ----------------
    c.box(-W + 0.08, 0.14, -L + 0.1, W - 0.08, 0.26, L - 0.05, "black_concrete")     # floor pan / splitter line
    c.box(-W, 0.26, -L + 0.05, W, 0.55, L - 0.15, body)                             # main tub
    # side skirts (black, slightly proud)
    c.sym(W, 0.2, -1.2, W + 0.03, 0.34, 1.25, "black_concrete")
    # wheel-arch fenders, bulging over the wheels
    for z in (1.75, -1.7):
        c.sym(0.7, 0.55, z - 0.5, W + 0.04, 0.82, z + 0.5, body)
        c.sym(0.75, 0.82, z - 0.32, W + 0.0, 0.88, z + 0.32, body)
    # ---------------- nose ----------------
    nose_y = 0.48 if kind == "ferrari" else 0.42
    c.slope(-W + 0.05, W - 0.05, 0.85, 0.86, L, nose_y, 0.32, body)                  # bonnet wedge
    c.box(-W + 0.2, 0.08, L - 0.25, W - 0.2, 0.18, L + 0.08, "black_concrete")        # front splitter
    c.box(-0.75, 0.2, L - 0.12, 0.75, 0.36, L - 0.04, "black_concrete")              # front grille
    if kind == "lambo":
        # big hexagon-ish side intakes in the bumper
        c.sym(0.55, 0.18, L - 0.14, 1.05, 0.4, L - 0.06, "black_concrete")
        # Y-shaped headlight: bar + down-stroke
        c.sym(0.45, 0.41, L - 0.22, 1.02, 0.47, L - 0.08, "white_concrete", glow=True)
        c.sym(0.85, 0.3, L - 0.2, 0.93, 0.44, L - 0.08, "white_concrete", glow=True)
        # bonnet creases (accent)
        c.slope(-0.36, -0.3, 0.9, 0.875, L - 0.1, nose_y + 0.025, 0.02, accent)
        c.slope(0.3, 0.36, 0.9, 0.875, L - 0.1, nose_y + 0.025, 0.02, accent)
    else:
        # oval headlights swept back over the fenders
        c.sym(0.5, 0.47, L - 0.35, 1.04, 0.53, L - 0.1, "white_concrete", glow=True)
        c.box(-0.55, 0.22, L - 0.1, 0.55, 0.38, L - 0.02, "black_concrete")
    # badge on the nose (yellow scudetto / gold bull)
    c.box(-0.09, nose_y - 0.12, L - 0.05, 0.09, nose_y + 0.04, L + 0.01, "yellow_concrete" if kind == "ferrari" else "gold_block")
    c.box(-0.035, nose_y - 0.08, L + 0.005, 0.035, nose_y, L + 0.02, "black_concrete")
    # ---------------- cockpit ----------------
    c.box(-0.6, 0.55, -0.6, 0.6, 0.62, 0.85, "black_concrete")                        # cockpit floor / hides saddle
    c.sym(0.62, 0.55, -0.55, W, 0.86, 0.85, body)                                     # door tops / sills
    c.slope(-0.95, 0.95, 0.15, 1.28, 0.95, 0.86, 0.04, "black_stained_glass")         # windscreen
    c.sym(0.92, 1.24, 0.08, 0.98, 1.3, 0.22, "black_concrete")                         # A-pillar tops
    c.slope(-0.98, -0.92, 0.12, 1.29, 0.95, 0.86, 0.06, "black_concrete")              # A-pillars
    c.slope(0.92, 0.98, 0.12, 1.29, 0.95, 0.86, 0.06, "black_concrete")
    c.box(-0.55, 0.62, 0.55, 0.55, 0.86, 0.85, "black_concrete")                      # dashboard
    c.box(-0.12, 0.8, 0.5, 0.12, 0.9, 0.56, "light_gray_concrete")                    # steering wheel
    seat = "red_concrete" if body != "red_concrete" else "black_concrete"
    c.box(-0.42, 0.55, -0.7, 0.42, 1.2, -0.48, "black_concrete")                      # seat back
    c.box(-0.42, 0.55, -0.62, -0.3, 1.1, 0.0, seat)                                   # seat bolsters
    c.box(0.3, 0.55, -0.62, 0.42, 1.1, 0.0, seat)
    c.sym(0.95, 0.94, 0.45, 1.25, 1.06, 0.62, body)                                    # mirrors
    c.sym(1.2, 0.95, 0.47, 1.26, 1.05, 0.6, "black_stained_glass")
    # side windows (low door glass)
    c.sym(1.0, 0.86, -0.45, 1.06, 1.08, 0.12, "black_stained_glass")
    # ---------------- side intakes ----------------
    if kind == "lambo":
        c.sym(W - 0.03, 0.33, -1.15, W + 0.02, 0.78, -0.62, "black_concrete")
        c.sym(W - 0.02, 0.78, -1.15, W + 0.03, 0.86, -0.55, accent)
    else:
        c.sym(W - 0.03, 0.38, -1.05, W + 0.02, 0.7, -0.62, "black_concrete")
        c.sym(W - 0.02, 0.3, -0.62, W + 0.03, 0.42, 0.6, accent)                      # side line
        c.sym(W + 0.01, 0.62, 1.2, W + 0.04, 0.78, 1.36, "yellow_concrete")           # scudetto on fender
    # ---------------- engine cover / rear ----------------
    c.box(-0.98, 0.55, -2.55, 0.98, 0.92, -0.55, body)                                # rear haunches
    c.slope(-0.7, 0.7, -2.4, 0.95, -0.7, 1.2, 0.3, body if kind == "ferrari" else "black_stained_glass")  # engine-cover slope
    c.box(-0.72, 0.92, -1.2, 0.72, 1.18, -0.68, body)                                  # roll hoop / buttress
    c.box(-0.5, 1.18, -1.15, 0.5, 1.22, -0.75, "black_concrete")                       # roof scoop lip
    if kind == "lambo":
        for i in range(3):                                                             # louvres
            zz = -1.45 - i * 0.28
            c.box(-0.6, 0.93, zz - 0.06, 0.6, 1.0 + 0.0 * i, zz, "black_concrete")
    # rear wing
    big = wing_block is not None
    wb = wing_block or body
    if big:
        c.sym(0.5, 0.9, -2.5, 0.56, 1.32, -2.38, "black_concrete")                     # struts
        c.box(-1.08, 1.3, -2.75, 1.08, 1.37, -2.3, wb)                                 # wing plane
        c.sym(1.06, 1.18, -2.78, 1.1, 1.42, -2.28, wb)                                 # end plates
    else:
        c.slope(-0.95, 0.95, -2.78, 1.02, -2.5, 0.93, 0.07, wb)                         # ducktail spoiler
    c.box(-W + 0.02, 0.3, -L - 0.02, W - 0.02, 0.86, -L + 0.12, body)                  # tail
    c.box(-0.9, 0.1, -L - 0.08, 0.9, 0.3, -L + 0.15, "black_concrete")                 # diffuser
    for x in (-0.6, -0.3, 0.0, 0.3, 0.6):
        c.box(x - 0.02, 0.1, -L - 0.12, x + 0.02, 0.32, -L - 0.08, "gray_concrete")    # diffuser fins
    # tail lights
    if kind == "ferrari":
        for x in (0.45, 0.8):
            c.sym(x - 0.12, 0.6, -L - 0.05, x + 0.12, 0.76, -L - 0.01, "red_concrete", glow=True)
        c.sym(0.12, 0.33, -L - 0.12, 0.26, 0.45, -L - 0.02, "light_gray_concrete")     # quad exhausts
        c.sym(0.32, 0.33, -L - 0.12, 0.46, 0.45, -L - 0.02, "light_gray_concrete")
    else:
        c.box(-1.02, 0.7, -L - 0.05, 1.02, 0.76, -L - 0.01, "red_concrete", glow=True)  # full-width bar
        c.sym(0.75, 0.52, -L - 0.05, 0.82, 0.76, -L - 0.01, "red_concrete", glow=True)  # Y down-strokes
        c.box(-0.2, 0.4, -L - 0.14, 0.2, 0.58, -L - 0.02, "light_gray_concrete")       # centre hex exhaust
        c.box(-0.12, 0.44, -L - 0.15, 0.12, 0.54, -L - 0.13, "black_concrete")
    return c.parts


VARIANTS = {
    # name: (kind, body, accent, rim, wing)
    "ferrari":      ("ferrari", "red_concrete",    "black_concrete",  "light_gray_concrete", None),
    "lambo_yellow": ("lambo",   "yellow_concrete", "black_concrete",  "gray_concrete",       "black_concrete"),
    "lambo_orange": ("lambo",   "orange_concrete", "black_concrete",  "gray_concrete",       "black_concrete"),
    "lambo_green":  ("lambo",   "lime_concrete",   "black_concrete",  "gray_concrete",       "black_concrete"),
    "lambo_black":  ("lambo",   "black_concrete",  "gray_concrete",   "gold_block",          "black_concrete"),
}


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".") + "f" if v != 0 else "0f"


def display_nbt(p):
    tr = ("{left_rotation:[%s],right_rotation:[0f,0f,0f,1f],translation:[%s],scale:[%s]}" %
          (",".join(f(v) for v in p["q"]), ",".join(f(v) for v in p["t"]), ",".join(f(v) for v in p["s"])))
    extra = ",brightness:{sky:15,block:15}" if p["glow"] else ""
    return ('{Tags:["ewrcar_part","ewrcar_new"],teleport_duration:2,view_range:1.5f,block_state:"minecraft:%s",'
            'transformation:%s%s}' % (p["block"], tr, extra))


HORSE = ('{Tags:["ewrcar","ewrcar_new","ewrcar_%s"],Tame:1b,Silent:1b,PersistenceRequired:1b,Invulnerable:1b,'
         'NoAI:0b,DeathLootTable:"minecraft:empty",Variant:0,'
         'equipment:{saddle:{id:"minecraft:saddle",count:1}},drop_chances:{saddle:0f},'
         'active_effects:[{id:"minecraft:invisibility",duration:-1,amplifier:0b,show_particles:0b,show_icon:0b}],'
         'attributes:[{id:"minecraft:movement_speed",base:0d},{id:"minecraft:jump_strength",base:%sd},'
         '{id:"minecraft:step_height",base:%sd},{id:"minecraft:scale",base:%sd},'
         '{id:"minecraft:knockback_resistance",base:1d}]}')


def write(path, text):
    full = os.path.join(PACK, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.strip() + "\n")


def main():
    if os.path.isdir(PACK):
        shutil.rmtree(PACK)
    write("pack.mcmeta", json.dumps({"pack": {"description": "EWR drivable supercars (Ferrari / Lamborghini)",
                                                "min_format": [121, 0], "max_format": [200, 0]}}, indent=1))
    write("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}))
    write("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}))

    write(f"data/{NS}/function/load.mcfunction", f"""
scoreboard objectives add ewr_car.id dummy
scoreboard objectives add ewr_car.v dummy
scoreboard objectives add ewr_car.x dummy
scoreboard objectives add ewr_car.y dummy
scoreboard objectives add ewr_car.z dummy
scoreboard objectives add ewr_car.px dummy
scoreboard objectives add ewr_car.py dummy
scoreboard objectives add ewr_car.pz dummy
execute unless score #next ewr_car.id matches 1.. run scoreboard players set #next ewr_car.id 0
scoreboard players set #t ewr_car.v 0
scoreboard players set #cd ewr_car.v 0
""")

    write(f"data/{NS}/function/tick.mcfunction", f"""
scoreboard players add #t ewr_car.v 1
execute as @e[type=horse,tag=ewrcar] at @s run function {NS}:internal/car_tick
function {NS}:dealer/tick
execute if score #t ewr_car.v matches 40.. run function {NS}:internal/cleanup
""")

    # per car, as+at the horse
    write(f"data/{NS}/function/internal/car_tick.mcfunction", f"""
scoreboard players set #ridden ewr_car.v 0
execute on passengers if entity @s[type=player] run scoreboard players set #ridden ewr_car.v 1
execute if score #ridden ewr_car.v matches 1 unless entity @s[tag=ewrcar_driving] run function {NS}:internal/start_drive
execute if score #ridden ewr_car.v matches 0 if entity @s[tag=ewrcar_driving] run function {NS}:internal/stop_drive
execute if score #ridden ewr_car.v matches 0 unless entity @s[tag=ewrcar_parked] if entity @s[nbt={{OnGround:1b}}] run function {NS}:internal/park
execute unless items entity @s saddle minecraft:saddle run item replace entity @s saddle with minecraft:saddle
# parked cars only refresh their body every 2 s; moving cars every tick
execute if entity @s[tag=ewrcar_parked] unless score #t ewr_car.v matches 40.. run return 0
function {NS}:internal/follow
""")
    write(f"data/{NS}/function/internal/start_drive.mcfunction", f"""
tag @s add ewrcar_driving
tag @s remove ewrcar_parked
data merge entity @s {{NoAI:0b}}
attribute @s minecraft:movement_speed base set {SPEED}
""")
    write(f"data/{NS}/function/internal/stop_drive.mcfunction", """
tag @s remove ewrcar_driving
attribute @s minecraft:movement_speed base set 0
""")
    write(f"data/{NS}/function/internal/park.mcfunction", f"""
data merge entity @s {{NoAI:1b,Motion:[0d,0d,0d]}}
tag @s add ewrcar_parked
function {NS}:internal/follow
""")
    # body follow with lag-hiding extrapolation
    write(f"data/{NS}/function/internal/follow.mcfunction", f"""
execute store result score @s ewr_car.x run data get entity @s Pos[0] 1000
execute store result score @s ewr_car.y run data get entity @s Pos[1] 1000
execute store result score @s ewr_car.z run data get entity @s Pos[2] 1000
scoreboard players operation #dx ewr_car.v = @s ewr_car.x
scoreboard players operation #dx ewr_car.v -= @s ewr_car.px
scoreboard players operation #dy ewr_car.v = @s ewr_car.y
scoreboard players operation #dy ewr_car.v -= @s ewr_car.py
scoreboard players operation #dz ewr_car.v = @s ewr_car.z
scoreboard players operation #dz ewr_car.v -= @s ewr_car.pz
scoreboard players operation @s ewr_car.px = @s ewr_car.x
scoreboard players operation @s ewr_car.py = @s ewr_car.y
scoreboard players operation @s ewr_car.pz = @s ewr_car.z
scoreboard players set #k ewr_car.v {PREDICT}
execute unless entity @s[tag=ewrcar_driving] run scoreboard players set #k ewr_car.v 0
execute unless score #dx ewr_car.v matches -2500..2500 run scoreboard players set #k ewr_car.v 0
execute unless score #dz ewr_car.v matches -2500..2500 run scoreboard players set #k ewr_car.v 0
execute unless score #dy ewr_car.v matches -1500..1500 run scoreboard players set #k ewr_car.v 0
scoreboard players operation #dx ewr_car.v *= #k ewr_car.v
scoreboard players operation #dz ewr_car.v *= #k ewr_car.v
execute if score #k ewr_car.v matches 0 run scoreboard players set #dy ewr_car.v 0
execute if score #dy ewr_car.v matches ..0 run scoreboard players set #dy ewr_car.v 0
scoreboard players operation #dx ewr_car.v += @s ewr_car.x
scoreboard players operation #dy ewr_car.v += @s ewr_car.y
scoreboard players operation #dz ewr_car.v += @s ewr_car.z
execute store result storage {NS}:tmp p.x double 0.001 run scoreboard players get #dx ewr_car.v
execute store result storage {NS}:tmp p.y double 0.001 run scoreboard players get #dy ewr_car.v
execute store result storage {NS}:tmp p.z double 0.001 run scoreboard players get #dz ewr_car.v
data modify storage {NS}:tmp p.yaw set from entity @s Rotation[0]
scoreboard players operation #cur ewr_car.v = @s ewr_car.id
function {NS}:internal/move with storage {NS}:tmp p
""")
    write(f"data/{NS}/function/internal/move.mcfunction", """
$execute as @e[tag=ewrcar_part,distance=..24] if score @s ewr_car.id = #cur ewr_car.v run tp @s $(x) $(y) $(z) $(yaw) 0
""")

    # orphan cleanup: parts whose horse is gone (only near players, so unloaded horses never lose bodies)
    write(f"data/{NS}/function/internal/cleanup.mcfunction", f"""
scoreboard players set #t ewr_car.v 0
tag @e[tag=ewrcar_part] add ewrcar_orphan
execute as @e[type=horse,tag=ewrcar] at @s run function {NS}:internal/claim
execute as @e[tag=ewrcar_orphan] at @s if entity @a[distance=..48] run kill @s
tag @e[tag=ewrcar_orphan] remove ewrcar_orphan
""")
    write(f"data/{NS}/function/internal/claim.mcfunction", """
scoreboard players operation #cur ewr_car.v = @s ewr_car.id
execute as @e[tag=ewrcar_orphan,distance=..24] if score @s ewr_car.id = #cur ewr_car.v run tag @s remove ewrcar_orphan
""")

    # click-to-enter via the interaction hitbox
    write(f"data/{NS}/advancement/click.json", json.dumps({
        "criteria": {"click": {"trigger": "minecraft:player_interacted_with_entity",
                               "conditions": {"entity": {"type": "minecraft:entity_properties", "entity": "this",
                                                                     "predicate": {"minecraft:entity_type": "minecraft:interaction"}}}}},
        "rewards": {"function": f"{NS}:internal/on_click"}}, indent=1))
    write(f"data/{NS}/function/internal/on_click.mcfunction", f"""
advancement revoke @s only {NS}:click
tag @s add ewrcar_clicker
execute on vehicle run tag @a[tag=ewrcar_clicker] remove ewrcar_clicker
execute if entity @s[tag=ewrcar_clicker] as @e[type=interaction,tag=ewrcar_click,distance=..8] if data entity @s interaction run function {NS}:internal/click_hit
execute as @e[type=interaction,tag=ewrcar_click,distance=..8] if data entity @s interaction run data remove entity @s interaction
tag @s remove ewrcar_clicker
""")
    write(f"data/{NS}/function/internal/click_hit.mcfunction", f"""
data remove entity @s interaction
scoreboard players operation #cur ewr_car.v = @s ewr_car.id
execute at @s as @e[type=horse,tag=ewrcar,distance=..8] if score @s ewr_car.id = #cur ewr_car.v run function {NS}:internal/mount
""")
    write(f"data/{NS}/function/internal/mount.mcfunction", """
execute on passengers run return 0
ride @p[tag=ewrcar_clicker] mount @s
tag @a remove ewrcar_clicker
""")

    # spawning
    parts_out = {}
    for name, (kind, body, accent, rim, wing) in VARIANTS.items():
        parts = build_car(kind, body, accent, rim, wing)
        parts_out[name] = parts
        lines = [f"# {name}: {len(parts)} display parts. Spawns at the execution position, facing the execution yaw.",
                 f"summon horse ~ ~ ~ {HORSE % (name, JUMP, STEP, SCALE)}",
                 "tp @e[type=horse,tag=ewrcar_new] ~ ~ ~ facing ^ ^ ^1",
                 "scoreboard players add #next ewr_car.id 1",
                 "scoreboard players operation @e[type=horse,tag=ewrcar_new] ewr_car.id = #next ewr_car.id"]
        for p in parts:
            lines.append("summon block_display ~ ~ ~ " + display_nbt(p))
        lines.append('summon interaction ~ ~ ~ {Tags:["ewrcar_part","ewrcar_click","ewrcar_new"],width:2.6f,height:1.35f,response:1b}')
        lines.append("scoreboard players operation @e[tag=ewrcar_part,tag=ewrcar_new] ewr_car.id = #next ewr_car.id")
        lines.append(f"execute as @e[type=horse,tag=ewrcar_new] at @s run function {NS}:internal/follow")
        lines.append("tag @e[tag=ewrcar_new] remove ewrcar_new")
        write(f"data/{NS}/function/place/{name}.mcfunction", "\n".join(lines))
        # public: in front of the executing player, facing their look direction (or at the execution pos)
        write(f"data/{NS}/function/spawn_{name}.mcfunction", f"""
execute if entity @s[type=player] at @s rotated ~ 0 positioned ^ ^ ^4 run function {NS}:place/{name}
execute unless entity @s[type=player] run function {NS}:place/{name}
""")
    # aliases
    write(f"data/{NS}/function/spawn_lambo.mcfunction", f"function {NS}:spawn_lambo_yellow")
    write(f"data/{NS}/function/spawn_lambo_lime.mcfunction", f"function {NS}:spawn_lambo_green")

    write(f"data/{NS}/function/remove_nearest.mcfunction", f"""
execute as @e[type=horse,tag=ewrcar,distance=..16,sort=nearest,limit=1] at @s run function {NS}:internal/remove_car
""")
    write(f"data/{NS}/function/remove_all.mcfunction", f"""
execute as @e[type=horse,tag=ewrcar] at @s run function {NS}:internal/remove_car
""")
    write(f"data/{NS}/function/internal/remove_car.mcfunction", """
scoreboard players operation #cur ewr_car.v = @s ewr_car.id
execute as @e[tag=ewrcar_part,distance=..24] if score @s ewr_car.id = #cur ewr_car.v run kill @s
kill @s
""")
    write(f"data/{NS}/function/help.mcfunction", """
tellraw @s [{"text":"[EWR Cars] ","color":"gold"},{"text":"Right-click a car to get in, look to steer, W to drive, sneak to get out. Spawn: /function ewr_cars:spawn_ferrari | spawn_lambo_yellow | spawn_lambo_orange | spawn_lambo_green | spawn_lambo_black   Remove: /function ewr_cars:remove_nearest","color":"white"}]
""")


    # ---------------- dealership: button panel -> delivery bay ----------------
    # buttons (stone, on the showroom's north wall inside the entrance) and the bay, in world coords
    # prices go through the shared economy: ewr_econ:try_buy (spawn_* functions stay free admin tools)
    BUTTONS = [(91, "ferrari", "Ferrari Rosso", 250000), (92, "lambo_yellow", "Lamborghini Yellow", 220000),
               (93, "lambo_orange", "Lamborghini Orange", 220000), (94, "lambo_green", "Lamborghini Green", 220000),
               (95, "lambo_black", "Lamborghini Black", 300000)]
    BY, BZ = 73, -84
    lines = ["execute if score #cd ewr_car.v matches 1.. run scoreboard players remove #cd ewr_car.v 1"]
    for i, (x, model, label, price) in enumerate(BUTTONS):
        # rising-edge detection: fire only on the tick the button becomes powered (+ global 2 s cooldown)
        lines.append(f'execute store success score #b{i} ewr_car.v if block {x} {BY} {BZ} minecraft:stone_button[powered=true]')
        lines.append(f'execute if score #b{i} ewr_car.v matches 1 unless score #p{i} ewr_car.v matches 1 if score #cd ewr_car.v matches ..0 '
                     f'positioned {x}.5 {BY} {BZ + 0.5} as @p[distance=..6,gamemode=!spectator] at @s '
                     f'run function {NS}:dealer/press {{model:"{model}",label:"{label}",price:{price}}}')
        lines.append(f'scoreboard players operation #p{i} ewr_car.v = #b{i} ewr_car.v')
    write(f"data/{NS}/function/dealer/tick.mcfunction", "\n".join(lines))
    # bay: x 90..96, z -71..-63 (floor y 71). Slots (cars face west = the highway)
    BAY = "x=90,y=70,z=-71,dx=6.99,dy=5,dz=8.99"
    SLOTS = [(1, -69.5), (2, -66.5), (3, -63.5)]
    slot_lines = "\n".join(
        f"execute if score #slot ewr_car.v matches 0 positioned 93.0 72 {z} unless entity @e[type=horse,tag=ewrcar,distance=..2.2] "
        f"run scoreboard players set #slot ewr_car.v {k}" for k, z in SLOTS)
    write(f"data/{NS}/function/dealer/press.mcfunction", f"""
# macro args: model, label, price. Context: AS + at the player who pressed. One press per 2 s (cooldown > 1 s button)
scoreboard players set #cd ewr_car.v 40
# refuse before charging if the bay is jammed (all slots taken and nothing recyclable)
scoreboard players set #slot ewr_car.v 0
{slot_lines}
execute if score #slot ewr_car.v matches 0 unless entity @e[type=horse,tag=ewrcar,tag=!ewrcar_driving,{BAY}] run return run title @s actionbar {{"text":"Delivery bay full - drive a car out first","color":"red"}}
$data modify storage {NS}:dealer model set value "$(model)"
$data modify storage {NS}:dealer label set value "$(label)"
$scoreboard players set #price ewr_car.v $(price)
$function ewr_econ:try_buy {{price:$(price),item:"$(label)",then:"{NS}:dealer/deliver"}}
""")
    write(f"data/{NS}/function/dealer/deliver.mcfunction", f"""
# paid (run by ewr_econ:try_buy as the buyer): recycle if the bay is full, then place the car
execute store result score #n ewr_car.v if entity @e[type=horse,tag=ewrcar,{BAY}]
execute if score #n ewr_car.v matches 3.. run function {NS}:dealer/remove_oldest
scoreboard players set #slot ewr_car.v 0
{slot_lines}
execute if score #slot ewr_car.v matches 0 run function {NS}:dealer/remove_oldest
{slot_lines}
execute if score #slot ewr_car.v matches 0 run return run function {NS}:dealer/refund
function {NS}:dealer/place with storage {NS}:dealer
""")
    write(f"data/{NS}/function/dealer/place.mcfunction", "\n".join(
        [f"$execute if score #slot ewr_car.v matches {k} positioned 93.0 72 {z} rotated 90 0 run function {NS}:place/$(model)"
         for k, z in SLOTS] +
        ['$tellraw @s [{"text":"[EWR Cars] ","color":"gold"},{"text":"Your $(label) is ready in the delivery bay","color":"gold"},{"text":" (outside, south-west)","color":"gray"}]']))
    write(f"data/{NS}/function/dealer/refund.mcfunction", """
execute unless entity @s[tag=ewr_infinite] run scoreboard players operation @s money += #price ewr_car.v
title @s actionbar {"text":"Delivery bay full - refunded, drive a car out first","color":"red"}
""")
    write(f"data/{NS}/function/dealer/remove_oldest.mcfunction", f"""
scoreboard players set #min ewr_car.v 2147483647
execute as @e[type=horse,tag=ewrcar,tag=!ewrcar_driving,x=90,y=70,z=-71,dx=6.99,dy=5,dz=8.99] run scoreboard players operation #min ewr_car.v < @s ewr_car.id
execute as @e[type=horse,tag=ewrcar,tag=!ewrcar_driving,x=90,y=70,z=-71,dx=6.99,dy=5,dz=8.99] if score @s ewr_car.id = #min ewr_car.v at @s run function {NS}:internal/remove_car
""")

    with open(os.path.join(HERE, "parts.json"), "w") as fh:
        json.dump(parts_out, fh)
    print({k: len(v) for k, v in parts_out.items()})


if __name__ == "__main__":
    main()
