import sys,os,json
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
x1,x2,z1,z2,st = map(int, sys.argv[1:6])
script = f'''
rows=[]
for z in range({z1},{z2}+1,{st}):
    r=[]
    for x in range({x1},{x2}+1,{st}):
        g=ground(x,z)
        w=world_block(x,g+1,z) or ''
        wb=world_block(x,g,z) or ''
        tag='~' if 'water' in w else ('T' if ('log' in wb or 'leaves' in wb) else ' ')
        r.append(tag+str(g+64))
    print(str(z).rjust(5)+' '+' '.join(r))
print('      '+' '.join(str(x).rjust(3) for x in range({x1},{x2}+1,{st})))
'''
r=S.build(script,0,0,0,name='survey',dry_run=True)
d=json.loads(r) if r.startswith('{') else None
print(d['printed'] if d and 'printed' in d else r[:3000])
