"""EWR economy: generates the ewr_econ datapack.   python gen.py
Public interface (other packs depend on it -- keep stable):
  function ewr_econ:try_buy {price:<int>, item:"<text>", then:"<namespace:function>"}   (as + at the buyer)
  function ewr_econ:give {player:"<name>", amount:<int>}     (amount may be negative)
  function ewr_econ:balance                                    (as the player)
"""
import json, os, shutil

DP = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_econ"
NS = "ewr_econ"
INFINITE = ["buggati354", "AniYiga", "pitaishere"]
START = 1000
INF_SCORE = 999999999

F = {}
F["load"] = [
    'scoreboard objectives add money dummy {text:"Money",color:"gold",bold:true}',
    'scoreboard objectives setdisplay sidebar money',
    'scoreboard objectives add ewre_tmp dummy',
    f"function {NS}:infinite_list",
]
F["tick"] = [
    "# only new (never seen) players: one cheap selector per tick; infinite list every 20 ticks",
    f"execute as @a[tag=!ewre_seen] run function {NS}:join",
    "scoreboard players add #t ewre_tmp 1",
    f"execute if score #t ewre_tmp matches 20.. run function {NS}:infinite_list",
]
# NAME-BASED infinite list: generator names (INFINITE) + names added live with add_infinite (kept in
# storage ewr_econ:cfg infinite, which lives in the world save and so survives regeneration)
F["infinite_list"] = ["scoreboard players set #t ewre_tmp 0"] + [
    f"execute as @a[name={n},tag=!ewr_infinite] run function {NS}:make_infinite" for n in INFINITE] + [
    f"data modify storage {NS}:tmp inf set from storage {NS}:cfg infinite",
    f"execute if data storage {NS}:tmp inf[0] run function {NS}:inf_iter",
]
F["inf_iter"] = [
    f"function {NS}:inf_one with storage {NS}:tmp inf[0]",
    f"data remove storage {NS}:tmp inf[0]",
    f"execute if data storage {NS}:tmp inf[0] run function {NS}:inf_iter",
]
F["inf_one"] = [f"$execute as @a[name=$(n),tag=!ewr_infinite] run function {NS}:make_infinite"]
F["add_infinite"] = [
    "# MACRO (admin): {player:\"<name>\"} -> remembered in storage (survives reloads/regeneration) + tagged now if online.",
    "# To make it part of the pack itself, also add the name to INFINITE in econ/gen.py.",
    f"$data remove storage {NS}:cfg infinite[{{n:\"$(player)\"}}]",
    f"$data modify storage {NS}:cfg infinite append value {{n:\"$(player)\"}}",
    f"$execute as @a[name=$(player)] run function {NS}:make_infinite",
    '$tellraw @a[tag=ewr_infinite] [{text:"[EWR Bank] ",color:"gold"},{text:"$(player) now has infinite money",color:"green"}]',
]
F["remove_infinite"] = [
    "# MACRO (admin): {player:\"<name>\"} (only for names added with add_infinite; generator names come back)",
    f"$data remove storage {NS}:cfg infinite[{{n:\"$(player)\"}}]",
    "$tag @a[name=$(player)] remove ewr_infinite",
    "$scoreboard players display numberformat @a[name=$(player)] money",
    "$scoreboard players set @a[name=$(player)] money 0",
]
F["join"] = [
    "# first time this player is seen: starting cash (once)",
    "tag @s add ewre_seen",
    f"function {NS}:infinite_list",
] + [
    "execute if entity @s[tag=ewr_infinite] run return 0",
    f"scoreboard players add @s money {START}",
    f'tellraw @s [{{text:"[EWR Bank] ",color:"gold"}},{{text:"Welcome! You got ${START:,} to spend.",color:"green"}}]',
]
F["make_infinite"] = [
    "tag @s add ewr_infinite",
    f"scoreboard players set @s money {INF_SCORE}",
    'scoreboard players display numberformat @s money fixed {text:"\u221e",color:"gold",bold:true}',
]
F["try_buy"] = [
    "# MACRO, as + at the buyer: {price:<int>, item:\"<text>\", then:\"<namespace:function>\"}",
    "# success -> deduct (unless ewr_infinite), receipt, run $(then) as the buyer, return 1; else red message, return fail",
    "scoreboard players add @s money 0",
    "$scoreboard players set #price ewre_tmp $(price)",
    "scoreboard players set #ok ewre_tmp 0",
    "execute if entity @s[tag=ewr_infinite] run scoreboard players set #ok ewre_tmp 1",
    "execute if score #ok ewre_tmp matches 0 if score @s money >= #price ewre_tmp run scoreboard players set #ok ewre_tmp 2",
    '$execute if score #ok ewre_tmp matches 0 run title @s actionbar [{text:"Not enough money: $(item) costs $$(price), you have $",color:"red"},{score:{name:"@s",objective:"money"},color:"red"}]',
    "execute if score #ok ewre_tmp matches 0 run playsound minecraft:block.note_block.bass master @s ~ ~ ~ 1 0.6",
    "execute if score #ok ewre_tmp matches 0 run return fail",
    "execute if score #ok ewre_tmp matches 2 run scoreboard players operation @s money -= #price ewre_tmp",
    '$title @s actionbar {text:"Bought $(item) for $$(price)",color:"green"}',
    "playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 0.6 1.4",
    "$function $(then)",
    "return 1",
]
F["give"] = [
    "# MACRO: {player:\"<name>\", amount:<int>}  (negative amount takes money; infinite players unchanged)",
    "$execute if entity @a[name=$(player),tag=ewr_infinite] run return 0",
    "$scoreboard players set #amt ewre_tmp $(amount)",
    "$scoreboard players operation $(player) money += #amt ewre_tmp",
    '$tellraw @a[name=$(player)] [{text:"[EWR Bank] ",color:"gold"},{text:"$(amount) -> balance $",color:"green"},{score:{name:"$(player)",objective:"money"},color:"green"}]',
]
F["balance"] = [
    "# as the player",
    "scoreboard players add @s money 0",
    'execute if entity @s[tag=ewr_infinite] run return run tellraw @s [{text:"[EWR Bank] ",color:"gold"},{text:"Balance: unlimited (\u221e)",color:"green"}]',
    'tellraw @s [{text:"[EWR Bank] ",color:"gold"},{text:"Balance: $",color:"green"},{score:{name:"@s",objective:"money"},color:"green"}]',
]

def main():
    if os.path.isdir(DP):
        shutil.rmtree(DP)
    fd = os.path.join(DP, "data", NS, "function")
    os.makedirs(fd)
    for n, lines in F.items():
        open(os.path.join(fd, n + ".mcfunction"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    td = os.path.join(DP, "data", "minecraft", "tags", "function")
    os.makedirs(td)
    json.dump({"values": [f"{NS}:tick"]}, open(os.path.join(td, "tick.json"), "w"))
    json.dump({"values": [f"{NS}:load"]}, open(os.path.join(td, "load.json"), "w"))
    json.dump({"pack": {"description": "EWR economy: money, try_buy", "min_format": 121, "max_format": 121}},
              open(os.path.join(DP, "pack.mcmeta"), "w"), indent=1)
    print("ewr_econ:", len(F), "functions ->", DP)

if __name__ == "__main__":
    main()
