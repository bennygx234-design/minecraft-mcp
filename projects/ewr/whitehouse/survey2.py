import sys,os; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.server import engine, block_name
xa,xb,za,zb,st = map(int, sys.argv[1:6])
added=engine.load_area('minecraft:overworld',xa,za,xb,zb,timeout=300); engine.flush()
W=engine.world
code={'gray_concrete':'#','yellow_concrete':'y','white_concrete':'w','water':'~','grass_block':'.','sand':':','stone':'s','smooth_stone':'S','polished_andesite':'a','dirt':'d','light_gray_concrete':'L'}
for z in range(za,zb+1,st):
    row=''
    for x in range(xa,xb+1,st):
        t=W.top_block(x,z,'minecraft:overworld')
        n=block_name(t[1]).replace('minecraft:','') if t else ' '
        row+=code.get(n, n[0].upper())
    print(f'{z:5d} '+row)
