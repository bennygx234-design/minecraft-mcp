"""Ride test with armor stands: python test_ride.py FROM:TO [FROM:TO ...]
Summons a tagged test armor stand at each FROM stand, runs ewr:start/<from>_<to> as it, polls until it
has left its car (arrived) or times out, prints final positions vs. TRANSIT stand points, kills the stands."""
import re, sys, time, os
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcmcp.engine import Engine
import gen
e = Engine()
pairs = [p.split(':') for p in sys.argv[1:]]
for i, (a, b) in enumerate(pairs):
    x, y, z = gen.NODES[a]
    e.cmd(f'summon armor_stand {gen.f(x)} {gen.f(y)} {gen.f(z)} {{Tags:["ewrt_test","ewrt_t{i}"]}}')
    print(a, '->', b, e.cmd(f'execute as @e[type=armor_stand,tag=ewrt_t{i}] run function ewr:start/{a.lower()}_{b.lower()}'))
t0 = time.time(); done = {}
while len(done) < len(pairs) and time.time() - t0 < 120:
    time.sleep(1)
    for i, (a, b) in enumerate(pairs):
        if i in done: continue
        if 'passed' not in e.cmd(f'execute if entity @e[type=armor_stand,tag=ewrt_t{i},tag=ewrt_ride]'):
            r = e.cmd(f'data get entity @e[type=armor_stand,tag=ewrt_t{i},limit=1] Pos')
            done[i] = (round(time.time() - t0), r.split(':', 1)[-1].strip())
for i, (a, b) in enumerate(pairs):
    print(f'{a}->{b}: expected {gen.NODES[b]}  got {done.get(i, "TIMEOUT")}')
print('cars left:', e.cmd('execute if entity @e[type=block_display,tag=ewrt_car]'))
e.cmd('kill @e[type=armor_stand,tag=ewrt_test]')
