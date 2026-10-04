import sys, os, json
os.environ['MCMCP_KEEP_FORCELOAD'] = '1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
src = open('highway.py', encoding='utf-8').read()
cut = src.index('# ---- profile ----')
script = 'PART=0\n' + src[:cut] + '''
n = 0
for x in range(-66, 92):
    for z in range(-98, 77):
        r = locate(x, z)
        if r is None or abs(r[1]) > 5.5 or r[0] < 0 or r[0] > A5: continue
        if not allowed(x, z) or in_airport(x, z): continue
        for y in range(66, 96):
            w = world_block(x, y, z) or ''
            if w.endswith('_leaves') or w.split('[')[0].endswith('_log'):
                if y >= 70 or 'leaves' in w:
                    pass
                put(x, y, z, 'air'); n += 1
print('cleared', n)
'''
mode = sys.argv[1]
r = S.build(script, 0, 0, 0, name='ewr-highway-treeclear', dry_run=(mode == 'dry'), seed=7)
d = json.loads(r); print({k: d.get(k) for k in ('id', 'blocks', 'blocks_changed', 'printed', 'palette_top')})
