import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine, block_name, _GroundIgnore
from collections import Counter
W=engine.world; ign=_GroundIgnore()
xa,xb,za,zb,st=map(int,sys.argv[1:6])
engine.load_area('minecraft:overworld',xa,za,xb,zb,timeout=300); engine.flush()
names=Counter()
for z in range(za,zb+1,st):
    row=[]
    for x in range(xa,xb+1,st):
        t=W.top_block(x,z,'minecraft:overworld',ignore=ign)
        n=block_name(t[1]).replace('minecraft:',''); names[n]+=1
        row.append(f'{t[0]-60:2d}' if n not in('water',) else '~~')
    print(f'{z:5d} '+' '.join(row))
print(names.most_common(25))
