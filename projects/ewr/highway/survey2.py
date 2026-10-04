import sys,os,json
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
x1,x2,z1,z2,st = map(int, sys.argv[1:6])
script = f'''
nat={{'grass_block':'g','sand':'s','dirt':'d','gravel':'v','stone':'o','clay':'c','coarse_dirt':'d','mud':'m','podzol':'d','sandstone':'s','dirt_path':'p'}}
other={{}}
for z in range({z1},{z2}+1,{st}):
    r=[]
    for x in range({x1},{x2}+1,{st}):
        g=ground(x,z)
        w=world_block(x,g+1,z) or ''
        wb=(world_block(x,g,z) or '').replace('minecraft:','').split('[')[0]
        c='~' if 'water' in w else nat.get(wb,'X')
        if c=='X': other[wb]=other.get(wb,0)+1
        r.append(c+str(g%100).zfill(2))
    print(str(z).rjust(5)+' '+''.join(r))
print('      '+''.join(str(x%1000).rjust(3) for x in range({x1},{x2}+1,{st})))
print(other)
'''
r=S.build(script,0,0,0,name='survey',dry_run=True)
d=json.loads(r) if r.startswith('{') else None
print(d['printed'] if d and 'printed' in d else r[:3000])
