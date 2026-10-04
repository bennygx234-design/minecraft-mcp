import sys, os; os.environ['MCMCP_KEEP_FORCELOAD']='1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
a=[int(v) for v in sys.argv[1:5]]
print(S.surface_map(*a, step=int(sys.argv[5]) if len(sys.argv)>5 else 1))
