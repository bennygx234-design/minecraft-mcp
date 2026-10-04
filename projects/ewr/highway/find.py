import sys,os,json
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
script = '''
for z in range(-110,-42,3):
    for x in range(37,126,3):
        g=ground(x,z); wb=(world_block(x,g,z) or '')
        if 'concrete' in wb or 'andesite' in wb or 'smooth_stone' in wb: print(x,z,g,wb)
'''
r=S.build(script,0,0,0,name='s',dry_run=True); print(json.loads(r).get('printed'))
