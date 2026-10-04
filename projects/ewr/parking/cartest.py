import os, sys, time
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp import server as S
print(S.run_commands(["execute positioned -77.5 68 238.5 rotated 90 0 run function ewr_cars:spawn_ferrari"]))
time.sleep(3)
print(S.run_commands(["execute positioned -77.5 68 238.5 run data get entity @e[type=horse,tag=ewrcar,distance=..3,limit=1] Pos",
                      "execute positioned -77.5 68 238.5 run data get entity @e[type=horse,tag=ewrcar,distance=..3,limit=1] Health",
                      "execute positioned -77.5 68 238.5 if entity @e[tag=ewrcar_part,distance=..4]"]))
print(S.run_commands(["execute positioned -77.5 68 238.5 run function ewr_cars:remove_nearest"]))
time.sleep(1)
print(S.run_commands(["execute positioned -77.5 68 238.5 if entity @e[tag=ewrcar_part,distance=..6]",
                      "execute positioned -77.5 68 238.5 if entity @e[type=horse,tag=ewrcar,distance=..6]"]))
