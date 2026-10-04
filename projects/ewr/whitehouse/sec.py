# exec'd by gen_ss.py: ENFORCED SECURITY for the White House grounds (functions under ewr_whitehouse:sec/...)
# states (ewhs_st): 0 clear, 1 warned (5 s grace), 2 counter-sniper engagement, 3 agents moving to arrest, 4 in holding
def wbox(x1, x2, z1, z2, y1, y2):
    """site-local inclusive box -> selector args"""
    return f"x={x1 + OX},y={y1 + OY},z={z1 + OZ},dx={x2 - x1},dy={y2 - y1},dz={z2 - z1}"

ZONE = wbox(2, 176, 13, 151, -17, 63)               # inside the perimeter fence (cell is handled before this)
INSIDE = [  # buildings + gates  -> arrest instead of snipers
    wbox(46, 134, 34, 101, -2, 45), wbox(3, 31, 45, 98, -10, 20), wbox(30, 47, 61, 66, -1, 10),
    wbox(133, 146, 61, 66, -1, 10), wbox(147, 171, 47, 85, -10, 20),
    wbox(58, 78, 13, 21, 6, 14), wbox(102, 122, 13, 21, 6, 14), wbox(52, 70, 143, 151, -2, 6),
    wbox(110, 129, 143, 151, -2, 6), wbox(2, 9, 52, 68, -2, 6), wbox(170, 176, 52, 68, -2, 6),
    wbox(166, 176, 132, 151, -2, 8),
]
CELL_TP = f"{155.5 + OX} {-7 + OY} {71.5 + OZ}"
CELL_BOX = wbox(150, 160, 67, 74, -8, -2)
RELEASE_TP = f"{68.5 + OX} {8 + OY} {9.5 + OZ} 180 0"     # Pennsylvania Ave plaza, outside the NW gate
PASS = ('minecraft:paper[minecraft:custom_name={text:"White House Authorized Pass",color:"gold",italic:false},'
        'minecraft:lore=[{text:"USSS · All Access",color:"gray",italic:false}],'
        'minecraft:custom_data={ewhs_pass:1b},minecraft:enchantment_glint_override=true]')
HAS_PASS = "*[minecraft:custom_data~{ewhs_pass:1b}]"
U = '{text:"[USSS] ",color:"dark_red",bold:true}'
def say(msg, color="white"):
    return f'tellraw @s [{U},{{text:"{esc(msg)}",color:"{color}"}}]'
def secs(src):
    return [f"scoreboard players operation @s ewhs_gs = @s {src}", "scoreboard players add @s ewhs_gs 19",
            "scoreboard players operation @s ewhs_gs /= #20 ewhs_cfg"]

F["load"] += ["scoreboard objectives add ewhs_st dummy", "scoreboard objectives add ewhs_g dummy",
              "scoreboard objectives add ewhs_gs dummy", "scoreboard objectives add ewhs_sh dummy",
              "scoreboard objectives add ewhs_ct dummy", "scoreboard objectives add ewhs_jail dummy",
              "scoreboard objectives add ewhs_pid dummy", "scoreboard objectives add ewhs_tid dummy",
              "scoreboard objectives add ewhs_hp health", "scoreboard objectives add ewhs_cfg dummy",
              "scoreboard players set #20 ewhs_cfg 20", "scoreboard players set #10 ewhs_cfg 10",
              "execute unless score #on ewhs_cfg matches 0.. run scoreboard players set #on ewhs_cfg 1"]
F["tick"] += [f"execute if score #on ewhs_cfg matches 1 run function {NS}:sec/tick",
              f"execute if entity @e[type=mannequin,tag=ewhs_return,limit=1] run function {NS}:sec/return_tick"]
F["sec/tick"] = [
    f"execute as @a[gamemode=!spectator] at @s run function {NS}:sec/player",
    f"execute as @e[type=!player,tag=ewhs_testsubj] at @s run function {NS}:sec/player",
    f"execute if entity @e[type=mannequin,tag=ewhs_chaser,limit=1] run function {NS}:sec/chase_tick",
]
F["sec/player"] = [
    "execute if score @s ewhs_hp matches ..0 run return 0",
    f"execute if score @s ewhs_st matches 4 run return run function {NS}:sec/jailed",
    f"execute unless entity @s[{ZONE}] run return run function {NS}:sec/left",
    f"execute if items entity @s container.* {HAS_PASS} run return run function {NS}:sec/authorized",
    f"execute if items entity @s weapon.offhand {HAS_PASS} run return run function {NS}:sec/authorized",
    f"execute unless score @s ewhs_st matches 1.. run function {NS}:sec/warn",
    f"execute if score @s ewhs_st matches 1 run function {NS}:sec/grace",
    f"execute if score @s ewhs_st matches 2 run function {NS}:sec/snipe",
    f"execute if score @s ewhs_st matches 3 run function {NS}:sec/await",
]
F["sec/left"] = [f"execute if score @s ewhs_st matches 1..3 run {say('You are outside the restricted area. Stand down.', 'green')}",
                 f"execute if score @s ewhs_st matches 1..3 run function {NS}:sec/reset"]
F["sec/authorized"] = [f"execute if score @s ewhs_st matches 1..3 run {say('Authorized Pass verified. Welcome to the White House.', 'green')}",
                       f"execute if score @s ewhs_st matches 1..3 run function {NS}:sec/reset"]
F["sec/reset"] = ["scoreboard players set @s ewhs_st 0", 'title @s actionbar ""', f"function {NS}:sec/free_agents",
                  "tag @s remove ewhs_tracked"]
F["sec/is_inside"] = [f"execute if entity @s[{b}] run return 1" for b in INSIDE] + ["return 0"]
F["sec/warn"] = [
    "scoreboard players set @s ewhs_st 1", "scoreboard players set @s ewhs_g 100",
    "title @s times 5 50 10",
    'title @s subtitle {text:"Leave immediately or you will be detained",color:"gold"}',
    'title @s title {text:"RESTRICTED AREA",color:"red",bold:true}',
    "playsound minecraft:event.raid.horn master @s ~ ~ ~ 0.7 1.6",
    say("This is the U.S. Secret Service. You have entered the White House restricted area without an Authorized Pass. "
        "Leave within 5 seconds. If you stay, you will be detained (inside the buildings or at a gate) or engaged by "
        "counter-snipers (on the grounds).", "red"),
]
F["sec/grace"] = ["scoreboard players remove @s ewhs_g 1"] + secs("ewhs_g") + [
    'title @s actionbar [{text:"RESTRICTED AREA - leave within ",color:"red",bold:true},{score:{name:"@s",objective:"ewhs_gs"},color:"yellow",bold:true},{text:" s",color:"red",bold:true}]',
    "scoreboard players operation #m ewhs_tmp = @s ewhs_g", "scoreboard players operation #m ewhs_tmp %= #10 ewhs_cfg",
    "execute if score #m ewhs_tmp matches 0 run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2",
    "execute if score #m ewhs_tmp matches 5 run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.5",
    f"execute if score @s ewhs_g matches ..0 run function {NS}:sec/escalate",
]
F["sec/escalate"] = [f"execute if function {NS}:sec/is_inside run return run function {NS}:sec/start_arrest",
                     f"function {NS}:sec/start_snipe"]
F["sec/start_snipe"] = [
    "scoreboard players set @s ewhs_st 2", "scoreboard players set @s ewhs_sh 10",
    "gamemode survival @s",
    "title @s times 5 40 10",
    'title @s subtitle {text:"Counter-snipers are engaging - leave the grounds",color:"gold"}',
    'title @s title {text:"FINAL WARNING",color:"dark_red",bold:true}',
    say("You did not leave. USSS counter-sniper teams on the roofs are now engaging you. Leave the grounds to make it stop.", "red"),
]
F["sec/snipe"] = [
    f"execute if function {NS}:sec/is_inside run return run function {NS}:sec/start_arrest",
    "scoreboard players remove @s ewhs_sh 1",
    'title @s actionbar {text:"UNDER FIRE - LEAVE THE GROUNDS",color:"dark_red",bold:true}',
    f"execute if score @s ewhs_sh matches ..0 run function {NS}:sec/fire",
]
F["sec/fire"] = [
    "scoreboard players set @s ewhs_sh 20", "tag @s add ewhs_tgt",
    f"execute as @e[type=mannequin,tag=ewhs_r_sniper,sort=nearest,limit=1] at @s run function {NS}:sec/shoot",
    "tag @s remove ewhs_tgt",
]
F["sec/shoot"] = [
    "tp @s ~ ~ ~ facing entity @e[tag=ewhs_tgt,limit=1] eyes",
    "playsound minecraft:item.crossbow.shoot hostile @a ~ ~ ~ 4 0.6",
    "playsound minecraft:entity.firework_rocket.blast hostile @a ~ ~ ~ 4 0.5",
    "scoreboard players set #ray ewhs_tmp 0",
    f"execute anchored eyes positioned ^ ^ ^0.6 facing entity @e[tag=ewhs_tgt,limit=1] eyes run function {NS}:sec/ray",
    "damage @e[tag=ewhs_tgt,limit=1] 6 minecraft:arrow by @s",
    "execute at @e[tag=ewhs_tgt,limit=1] run playsound minecraft:entity.arrow.hit_player hostile @a ~ ~ ~ 1 1",
]
F["sec/ray"] = [
    "particle minecraft:crit ~ ~ ~ 0 0 0 0 1 force",
    "scoreboard players add #ray ewhs_tmp 1",
    "execute if score #ray ewhs_tmp matches 2 run particle minecraft:smoke ~ ~ ~ 0.1 0.1 0.1 0.01 6 force",
    f"execute if score #ray ewhs_tmp matches ..160 unless entity @e[tag=ewhs_tgt,distance=..1.2] positioned ^ ^ ^1 run function {NS}:sec/ray",
]
F["sec/newpid"] = ["scoreboard players add #next ewhs_pid 1", "scoreboard players operation @s ewhs_pid = #next ewhs_pid"]
F["sec/start_arrest"] = [
    "scoreboard players set @s ewhs_st 3", "scoreboard players set @s ewhs_ct 0",
    f"execute unless score @s ewhs_pid matches 1.. run function {NS}:sec/newpid",
    "tag @s add ewhs_tracked",
    "scoreboard players operation #t ewhs_tmp = @s ewhs_pid",
    f"execute as @e[type=mannequin,tag=ewhs_ss,tag=!ewhs_chaser,tag=!ewhs_patrol,tag=!ewhs_r_sniper,tag=!ewhs_r_roof,sort=nearest,limit=2] run function {NS}:sec/recruit",
    "title @s times 5 40 10",
    'title @s subtitle {text:"Stay where you are",color:"gold"}',
    'title @s title {text:"SECRET SERVICE - STOP!",color:"red",bold:true}',
    "playsound minecraft:block.bell.use master @s ~ ~ ~ 1 0.8",
    say("You did not leave. Secret Service agents are moving to detain you.", "red"),
]
F["sec/recruit"] = ["tag @s add ewhs_chaser", "tag @s remove ewhs_return",
                    "scoreboard players operation @s ewhs_tid = #t ewhs_tmp", "scoreboard players set @s ewhs_ct 0"]
F["sec/await"] = ["scoreboard players add @s ewhs_ct 1",
                  'title @s actionbar {text:"Secret Service agents are on their way - leave NOW",color:"red",bold:true}',
                  f"execute if score @s ewhs_ct matches 400.. run function {NS}:sec/arrest"]
F["sec/chase_tick"] = [f"execute as @e[type=mannequin,tag=ewhs_chaser] at @s run function {NS}:sec/chase_one"]
F["sec/chase_one"] = [
    "scoreboard players add @s ewhs_ct 1",
    "scoreboard players operation #t ewhs_tmp = @s ewhs_tid",
    "execute as @e[tag=ewhs_tracked] if score @s ewhs_pid = #t ewhs_tmp if score @s ewhs_st matches 3 run tag @s add ewhs_ctarget",
    f"execute unless entity @e[tag=ewhs_ctarget,limit=1] run return run function {NS}:sec/to_return",
    f"execute if score @s ewhs_ct matches 1200.. run tag @e[tag=ewhs_ctarget] remove ewhs_ctarget",
    f"execute unless entity @e[tag=ewhs_ctarget,limit=1] run return run function {NS}:sec/to_return",
    "tp @s ~ ~ ~ facing entity @e[tag=ewhs_ctarget,limit=1] feet",
    "execute at @s run tp @s ^ ^ ^0.4",
    "execute at @s run particle minecraft:cloud ~ ~0.1 ~ 0.1 0 0.1 0 1",
    f"execute at @s if entity @e[tag=ewhs_ctarget,distance=..1.8] as @e[tag=ewhs_ctarget,limit=1] at @s run function {NS}:sec/arrest",
    "tag @e[tag=ewhs_ctarget] remove ewhs_ctarget",
]
F["sec/arrest"] = [
    "scoreboard players set @s ewhs_st 4", "scoreboard players set @s ewhs_jail 1200",
    f"function {NS}:sec/free_agents", "tag @s remove ewhs_tracked",
    "title @s times 5 60 10",
    'title @s subtitle {text:"Detained by the U.S. Secret Service for 60 seconds",color:"gray"}',
    'title @s title {text:"ARRESTED",color:"dark_red",bold:true}',
    say("You have been detained for entering the White House restricted area without authorization. "
        "You will be released outside the North Gate in 60 seconds.", "red"),
    "gamemode survival @s",
    f"tp @s {CELL_TP} 0 0",
    "effect give @s minecraft:slowness 60 2 true",
    "playsound minecraft:block.iron_door.close master @s ~ ~ ~ 1 0.8",
]
F["sec/jailed"] = ["scoreboard players remove @s ewhs_jail 1",
                   f"execute unless entity @s[{CELL_BOX}] run tp @s {CELL_TP}"] + secs("ewhs_jail") + [
    'title @s actionbar [{text:"USSS HOLDING - release in ",color:"gray"},{score:{name:"@s",objective:"ewhs_gs"},color:"white"},{text:" s",color:"gray"}]',
    f"execute if score @s ewhs_jail matches ..0 run function {NS}:sec/release",
]
F["sec/release"] = ["scoreboard players set @s ewhs_st 0", "scoreboard players set @s ewhs_jail 0",
                    "effect clear @s minecraft:slowness", f"tp @s {RELEASE_TP}", 'title @s actionbar ""',
                    say("You have been released. Stay outside the fence unless you hold a White House Authorized Pass.", "green")]
F["sec/free_agents"] = ["scoreboard players set #t ewhs_tmp -1",
                        "scoreboard players operation #t ewhs_tmp = @s ewhs_pid",
                        f"execute as @e[type=mannequin,tag=ewhs_chaser] if score @s ewhs_tid = #t ewhs_tmp run function {NS}:sec/to_return"]
F["sec/to_return"] = ["tag @s remove ewhs_chaser", "tag @s add ewhs_return", "scoreboard players set @s ewhs_tid 0"]
RT = []
for a in AGENTS:
    if a["patrol"]:
        continue
    wx, wy, wz = world(a)
    RT.append(f"execute as @e[type=mannequin,tag=ewhs_m_{a['id']},tag=ewhs_return,limit=1] at @s run function {NS}:sec/walk/{a['id']}")
    F[f"sec/walk/{a['id']}"] = [f"execute positioned {wx} {wy} {wz} if entity @s[distance=..0.6] run return run function {NS}:sec/home/{a['id']}",
                                f"tp @s ~ ~ ~ facing {wx} {wy} {wz}", "execute at @s run tp @s ^ ^ ^0.3"]
    F[f"sec/home/{a['id']}"] = [f"tp @s {wx} {wy} {wz} {float(a['yaw'])} 0", "tag @s remove ewhs_return", "tag @s remove ewhs_turned"]
F["sec/return_tick"] = RT
F["release_all"] = [
    f"execute as @e[scores={{ewhs_st=4}}] run function {NS}:sec/release",
    f"execute as @e[scores={{ewhs_st=1..3}}] run function {NS}:sec/reset",
    f"execute as @e[type=mannequin,tag=ewhs_chaser] run function {NS}:sec/to_return",
    'tellraw @s {text:"[ewr_whitehouse] everyone released, agents returning to posts",color:"gray"}',
]
F["security_off"] = ["scoreboard players set #on ewhs_cfg 0", f"function {NS}:release_all",
                     'tellraw @s {text:"[ewr_whitehouse] White House security OFF",color:"yellow"}']
F["security_on"] = ["scoreboard players set #on ewhs_cfg 1",
                    'tellraw @s {text:"[ewr_whitehouse] White House security ON",color:"red"}']
F["give_pass"] = [f"$give $(player) {PASS} 1",
                  f'$tellraw $(player) [{U},{{text:"You have been issued a White House Authorized Pass. Keep it in your inventory.",color:"gold"}}]']
F["help"] += ['tellraw @s {text:"Security: function ewr_whitehouse:security_on | security_off | release_all | give_pass {player:\\"Name\\"}",color:"gray"}']
