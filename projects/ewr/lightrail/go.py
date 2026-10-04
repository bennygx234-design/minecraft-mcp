import sys,os,json,time
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
mode, script, name = sys.argv[1], sys.argv[2], sys.argv[3]
pre = sys.argv[4] if len(sys.argv) > 4 else ''
src = pre + '\n' + open(script, encoding='utf-8').read()
t=time.time()
r = S.build(src, 0, 0, 0, name=name, dry_run=(mode=='dry'), seed=7)
try:
    d=json.loads(r); print(json.dumps({k:d.get(k) for k in ('id','blocks','blocks_changed','min','max','size','palette_top','printed','post_errors','error')}, indent=1))
except Exception:
    print(r[:5000])
print('elapsed', round(time.time()-t,1))
