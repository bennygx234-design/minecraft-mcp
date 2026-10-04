import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
from mcmcp.server import engine, _GroundIgnore, block_name
import statistics
xa,za,xb,zb=-330,-260,-80,-70
added=engine.load_area('minecraft:overworld',xa,za,xb,zb,timeout=200); engine.flush()
ign=_GroundIgnore(); H={}
for x in range(xa,xb+1,2):
  for z in range(za,zb+1,2):
    t=engine.world.top_block(x,z,'minecraft:overworld',ignore=ign)
    if t:
      wet = block_name(t[1]) in ('minecraft:water','minecraft:ice') or engine.world.block(x,t[0]+1,z,'minecraft:overworld')=='minecraft:water'
      H[(x,z)]=(t[0],wet)
res=[]
W,D=150,120
for x in range(xa,xb-W+1,6):
  for z in range(za,zb-D+1,6):
    pts=[H[(px,pz)] for px in range(x,x+W,2) for pz in range(z,z+D,2) if (px,pz) in H]
    nw=sum(p[1] for p in pts); hs=[p[0] for p in pts]
    m=statistics.median(hs)
    cut=sum(max(0,h-m) for h in hs); fill=sum(max(0,m-h) for h in hs)
    res.append((cut+fill, x,z,m,min(hs),max(hs),nw))
res.sort()
for r in res[:15]: print(r)
import json; json.dump({f'{k[0]},{k[1]}':v for k,v in H.items()}, open(r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\heights.json','w'))
