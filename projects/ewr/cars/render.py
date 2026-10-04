import sys, os; os.environ['MCMCP_KEEP_FORCELOAD']='1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
a=[int(v) for v in sys.argv[1:7]]
view=sys.argv[8] if len(sys.argv)>8 else 'south_east'
cut=int(sys.argv[9]) if len(sys.argv)>9 else None
img=S.render(*a, view=view, cutaway=cut)
open(sys.argv[7],'wb').write(img.data)
print(sys.argv[7])
