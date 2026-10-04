import sys, os, json, time
os.environ['MCMCP_KEEP_FORCELOAD'] = '1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
mode, part = sys.argv[1], int(sys.argv[2])
src = open(r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\highway\highway.py', encoding='utf-8').read()
script = 'PART=%d\n' % part + src
t = time.time()
r = S.build(script, 0, 0, 0, name='ewr-highway-part%d' % part, dry_run=(mode == 'dry'), seed=7)
try:
    d = json.loads(r)
    print(json.dumps({k: d.get(k) for k in ('id', 'blocks', 'blocks_changed', 'min', 'max', 'size', 'palette_top',
                                             'printed', 'post_errors')}, indent=1))
except Exception:
    print(r[:4000])
print('elapsed', round(time.time() - t, 1))
