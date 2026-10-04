import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine, block_name
W=engine.world
z=int(sys.argv[1]); xa,xb=int(sys.argv[2]),int(sys.argv[3])
engine.load_area('minecraft:overworld',xa,z,xb,z,timeout=200); engine.flush()
for x in range(xa,xb+1):
    t=W.top_block(x,z,'minecraft:overworld')
    print(x, t[0], block_name(t[1]).replace('minecraft:',''))
