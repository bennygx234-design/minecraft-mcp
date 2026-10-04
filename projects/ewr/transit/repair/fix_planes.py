"""Repair for ewr_planes: I accidentally removed the shared 'ewr_id' objective (wiping plane/part links).
Re-link each block_display part to its plane by matching (block, transformation) against the build files."""
import re, sys, collections
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.engine import Engine
e = Engine()
FD = r'C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_planes\data\ewr_planes\function\internal'
IDS = {'ewr': 1, 'delta': 2, 'united': 3}   # EWR Air=1, Delta red=2, United blue=3 (set on the ghasts)
num = r'(-?[\d.]+)f?'

def sig(block, txt):
    vals = {}
    for k in ('left_rotation', 'translation', 'scale', 'right_rotation'):
        m = re.search(k + r':\s*\[([^\]]*)\]', txt)
        vals[k] = tuple(round(float(v.strip().rstrip('f')), 2) for v in m.group(1).split(',')) if m else None
    return (block.replace('minecraft:', ''), vals['translation'], vals['scale'], vals['left_rotation'])

need = {}
for t in IDS:
    c = collections.Counter()
    for line in open(FD + '/build_' + t + '.mcfunction', encoding='utf-8'):
        if line.startswith('summon block_display'):
            b = re.search(r'block_state:"([^"]+)"', line).group(1)
            c[sig(b.split('[')[0], line)] += 1
    need[t] = c

r = e.cmd('execute as @e[type=block_display,tag=ewr_part] run data get entity @s UUID')
uu = re.findall(r'\[I; (-?\d+), (-?\d+), (-?\d+), (-?\d+)\]', r)
def hexu(a):
    h = ''.join('%08x' % (int(x) & 0xffffffff) for x in a)
    return f'{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}'
parts = []
for a in uu:
    u = hexu(a)
    bs = e.cmd(f'data get entity {u} block_state')
    bm = re.search(r'"([^"]+)"', bs)
    tr = e.cmd(f'data get entity {u} transformation')
    parts.append((u, sig(bm.group(1) if bm else '?', tr)))
print('parts', len(parts))
left = {t: need[t].copy() for t in IDS}
assign = {}
# most specific signatures first (those that fit the fewest plane types)
parts.sort(key=lambda p: sum(1 for t in IDS if left[t][p[1]] > 0))
unmatched = []
for u, s in parts:
    cands = [t for t in IDS if left[t][s] > 0]
    if not cands:
        unmatched.append((u, s)); continue
    t = max(cands, key=lambda t: sum(left[t].values()))
    left[t][s] -= 1
    assign[u] = t
print('assigned', collections.Counter(assign.values()), 'unmatched', len(unmatched))
for u, s in unmatched[:5]:
    print('  unmatched', s)
if '--apply' in sys.argv:
    for u, t in assign.items():
        e.cmd(f'scoreboard players set {u} ewr_id {IDS[t]}')
    print('applied')
