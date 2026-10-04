import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine
W=engine.world; D='minecraft:overworld'
engine.load_area(D,-95,-102,-20,-60,timeout=200); engine.flush()
def surf(x,z):
    for y in range(85,55,-1):
        b=W.block(x,y,z,D) or 'minecraft:air'
        if b.endswith(':air') or 'lantern' in b: continue
        if 'slab' in b and 'type=top' not in b and 'double' not in b: return y+0.5, b
        return y+1, b
bad=0
lanes=[[(x,z) for x in range(-33,-26)] for z in range(-63,-100,-1)] + [[(x,z) for z in range(-99,-92)] for x in range(-34,-94,-1)]
prev=None
for row in lanes:
    s=[surf(x,z) for x,z in row]
    for (x,z),(h,bk) in zip(row,s):
        for dy in (0,1):
            a=W.block(x,int(h+0.5)+dy if h%1==0 else int(h)+1+dy-1,z,D)
        if not any(k in bk for k in ('concrete','slab','andesite','smooth_stone')):
            print('odd', x,z,h,bk); bad+=1
    hs=[h for h,_ in s]
    if prev and max(abs(a-b) for a,b in zip(hs,prev))>0.5: print('step', row[0], prev, hs); bad+=1
    prev=hs
print('bad',bad)
