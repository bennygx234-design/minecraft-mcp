"""Check every employee's feet/head/floor blocks in-world: python verify.py"""
import json, sys
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.engine import Engine
e = Engine(); e.flush()
R = json.load(open(r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\staff\roster.json'))
pos = []
for p in R:
    for dy in (-1, 0, 1):
        pos.append((p['x'], p['y'] + dy, p['z']))
snap = e.snapshot(pos, 'minecraft:overworld')
SOFT = ('air', 'carpet', 'pressure_plate', 'button', 'torch', 'sign', 'banner', 'light', 'rail')
bad = 0
for p in R:
    f = snap[(p['x'], p['y'], p['z'])][0]; hd = snap[(p['x'], p['y'] + 1, p['z'])][0]; fl = snap[(p['x'], p['y'] - 1, p['z'])][0]
    ok = any(k in f for k in SOFT) and any(k in hd for k in SOFT) and 'air' not in fl
    if not ok:
        bad += 1
    print(('OK ' if ok else 'BAD'), p['id'], (p['x'], p['y'], p['z']), fl.split(':')[1], f.split(':')[1], hd.split(':')[1])
print('bad', bad, 'of', len(R))
