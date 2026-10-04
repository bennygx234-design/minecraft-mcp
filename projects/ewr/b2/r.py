import sys,os
os.environ['MCMCP_KEEP_FORCELOAD']='1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
a=sys.argv[1:]
if a[0]=='render':
    x1,y1,z1,x2,y2,z2=map(int,a[1:7]); out=a[7]; view=a[8] if len(a)>8 else 'south_east'
    cut=int(a[9]) if len(a)>9 else None
    img=S.render(x1,y1,z1,x2,y2,z2,view=view,cutaway=cut); open(out,'wb').write(img.data); print('wrote',out)
elif a[0]=='surf':
    x1,z1,x2,z2,st=map(int,a[1:6]); print(S.surface_map(x1,z1,x2,z2,step=st))
elif a[0]=='scan':
    print(S.scan_region(*map(int,a[1:7])))
elif a[0] in ('build','dry'):
    import json,time
    script=open(a[1],encoding='utf-8').read(); X,Y,Z=map(int,a[3:6])
    for i in range(3):
        r=S.build(script,X,Y,Z,name=a[2],dry_run=(a[0]=='dry'),seed=7)
        if 'not load' in r: time.sleep(3); continue
        break
    try:
        d=json.loads(r); print(json.dumps({k:d.get(k) for k in ("id","blocks","blocks_changed","min","max","size","palette_top","printed","post_errors","seconds")},indent=1))
    except Exception: print(r[:4000])
elif a[0]=='undo':
    print(S.undo(a[1]))
