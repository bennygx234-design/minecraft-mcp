"""Paid ride test: python test_paid_ride.py FROM:TO:MONEY ...  (armor stands with a temporary money score,
run ewr:buy/<from>_<to> as each; reports refused/arrived and the money left; kills the stands)"""
import sys, time, os
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcmcp.engine import Engine
import gen
e = Engine()
tri = [p.split(':') for p in sys.argv[1:]]
for i, (a, b, m) in enumerate(tri):
    x, y, z = gen.NODES[a]
    e.cmd(f'summon armor_stand {gen.f(x)} {gen.f(y)} {gen.f(z)} {{Tags:["ewrt_test","ewrt_p{i}"]}}')
    e.cmd(f'scoreboard players set @e[type=armor_stand,tag=ewrt_p{i}] money {m}')
    r = e.cmd(f'execute as @e[type=armor_stand,tag=ewrt_p{i}] at @s run function ewr:buy/{a.lower()}_{b.lower()}')
    print(f'{a}->{b} fare ${gen.fare(a, b)} money {m}:', r)
t0 = time.time(); done = {}
riding = {i for i in range(len(tri)) if 'passed' in e.cmd(f'execute if entity @e[type=armor_stand,tag=ewrt_p{i},tag=ewrt_ride]')}
print('riding:', sorted(riding))
while len(done) < len(riding) and time.time() - t0 < 150:
    time.sleep(1)
    for i in riding - set(done):
        if 'passed' not in e.cmd(f'execute if entity @e[type=armor_stand,tag=ewrt_p{i},tag=ewrt_ride]'):
            done[i] = (round(time.time() - t0), e.cmd(f'data get entity @e[type=armor_stand,tag=ewrt_p{i},limit=1] Pos').split(':', 1)[-1].strip())
for i, (a, b, m) in enumerate(tri):
    left = e.cmd(f'scoreboard players get @e[type=armor_stand,tag=ewrt_p{i},limit=1] money')
    print(f'{a}->{b}: {"REFUSED" if i not in riding else done.get(i, "TIMEOUT")}  expected {gen.NODES[b]} | {left}')
print('cars left:', e.cmd('execute if entity @e[type=block_display,tag=ewrt_car]'))
e.cmd('kill @e[type=armor_stand,tag=ewrt_test]')
