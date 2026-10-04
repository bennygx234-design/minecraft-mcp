import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine, block_name
xa,xb,za,zb = map(int, sys.argv[1:5])
added=engine.load_area('minecraft:overworld',xa,za,xb,zb,timeout=200); engine.flush()
W=engine.world
code={'gray_concrete':'#','yellow_concrete':'y','white_concrete':'w','water':'~','grass_block':'.','sand':':','stone':'s','smooth_stone':'S','polished_andesite':'a','dirt':'d','light_gray_concrete':'L'}
print('     '+''.join(str(abs(x)//10%10) if x%10==0 else ' ' for x in range(xa,xb+1)))
for z in range(za,zb+1):
    row=''; hs=[]
    for x in range(xa,xb+1):
        t=W.top_block(x,z,'minecraft:overworld')
        if not t: row+=' '; continue
        n=block_name(t[1]).replace('minecraft:','')
        row+=code.get(n, n[0].upper())
    print(f'{z:5d}'+row)
