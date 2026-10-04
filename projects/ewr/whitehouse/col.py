import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine, block_name
W=engine.world
pts=[tuple(map(int,p.split(','))) for p in sys.argv[1:]]
xs=[p[0] for p in pts]; zs=[p[1] for p in pts]
engine.load_area('minecraft:overworld',min(xs),min(zs),max(xs),max(zs),timeout=200); engine.flush()
for (x,z) in pts:
    col=[]
    for y in range(95,58,-1):
        bn=W.block(x,y,z,'minecraft:overworld')
        if bn and bn!='minecraft:air' and 'cave_air' not in bn:
            col.append(f'{y}:{bn.replace("minecraft:","")}')
    print(x,z,' | '.join(col[:6]))
