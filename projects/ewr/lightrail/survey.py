import sys,os,json
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
pts = sys.argv[1]
script = '''
import math
pts=%s
for i in range(len(pts)-1):
    (x1,z1),(x2,z2)=pts[i],pts[i+1]
    L=math.hypot(x2-x1,z2-z1); n=max(1,int(L//4))
    for k in range(n+1):
        x=x1+(x2-x1)*k/n; z=z1+(z2-z1)*k/n
        bx,bz=math.floor(x),math.floor(z)
        g=ground(bx,bz)
        col=[]
        for y in range(g,g-12,-1):
            w=(world_block(bx,y,bz) or '').replace('minecraft:','').split('[')[0]
            if w not in ('water','air','seagrass','tall_seagrass','kelp','kelp_plant'):
                col=(y,w);break
        top=(world_block(bx,g,bz) or '').replace('minecraft:','').split('[')[0]
        print(bx,bz,'top',g,top,'solid',col)
''' % pts
r=S.build(script,0,0,0,name='survey',dry_run=True)
d=json.loads(r) if r.startswith('{') else None
print(d['printed'] if d and 'printed' in d else r[:3000])
