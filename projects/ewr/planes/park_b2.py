"""Wait for the military apron to have ground, then park a flyable B-2 at about (150, 64, 80) facing west."""
import sys, time
sys.path.insert(0, r"C:\Users\benny\minecraft-mcp")
from mcmcp.engine import Engine
e = Engine()
BAD = ("air", "water", "lava", "kelp", "seagrass", "bubble_column")
X0, Z0 = 150, 80
deadline = time.time() + 20 * 60
while True:
    e.flush(); e.world.invalidate() if hasattr(e.world, "invalidate") else None
    w = e.world
    g = w.block(X0, 63, Z0)
    probes = [(x, z) for x in range(X0 - 5, X0 + 11, 3) for z in range(Z0 - 16, Z0 + 17, 4)]
    ground_ok = all(not any(k in (w.block(x, 63, z) or "air") for k in BAD) for x, z in probes)
    clear = all((w.block(x, y, z) or "") == "minecraft:air" for x, z in probes for y in (64, 65, 66))
    print(time.strftime("%H:%M:%S"), "centre y63:", g, "ground_ok:", ground_ok, "clear:", clear, flush=True)
    if ground_ok and clear:
        top = w.top_block(X0, Z0)
        print("top", top)
        added = e.load_area("minecraft:overworld", X0 - 20, Z0 - 20, X0 + 20, Z0 + 20)
        try:
            print(e.cmd(f'function ewr_planes:spawn_at {{x:{X0}.5,y:64,z:{Z0}.5,yaw:90,livery:"b2",size:"b2"}}'))
            time.sleep(3)
            print(e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,name=\"B-2 Spirit (b2)\"] run data get entity @s Pos"))
            print(e.cmd("execute as @e[type=happy_ghast,tag=ewr_plane,name=\"B-2 Spirit (b2)\"] at @s if entity @e[type=block_display,tag=ewr_part,distance=..3]"))
        finally:
            e.release("minecraft:overworld", added)
        break
    if time.time() > deadline:
        print("gave up: no ground after 20 minutes")
        break
    time.sleep(120)
