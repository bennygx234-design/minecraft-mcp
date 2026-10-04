"""Report what is currently in the world at every panel cell (expect air before building, panel after)."""
import json, sys, os
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
from mcmcp import server as S
from mcmcp.engine import Engine
d = json.load(open(os.path.join(os.path.dirname(__file__), 'panels.json')))
e = S.engine
stops = sys.argv[1:] or list(d['cells'])
for a in stops:
    cells = d['cells'][a]
    xs = [c[0][0] for c in cells]; ys = [c[0][1] for c in cells]; zs = [c[0][2] for c in cells]
    got = e.read_cells(min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    bad = []
    for p, st in cells:
        cur = got[tuple(p)][0]
        want = 'minecraft:' + st.split('[')[0]
        if cur.split('[')[0] not in ('minecraft:air', want):
            bad.append((p, cur))
        elif cur.split('[')[0] != want:
            bad.append((p, 'MISSING ' + cur))
    conf = [b for b in bad if not b[1].startswith('MISSING')]
    print(a, len(cells), 'cells; missing:', len(bad) - len(conf), 'conflicts:', len(conf)); [print('  ', b) for b in conf[:12]]
