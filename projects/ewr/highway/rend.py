import sys, os
os.environ['MCMCP_KEEP_FORCELOAD'] = '1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
x1, y1, z1, x2, y2, z2 = map(int, sys.argv[1:7])
out = sys.argv[7]
view = sys.argv[8] if len(sys.argv) > 8 else 'south_east'
img = S.render(x1, y1, z1, x2, y2, z2, view=view)
open(out, 'wb').write(img.data)
print('wrote', out)
