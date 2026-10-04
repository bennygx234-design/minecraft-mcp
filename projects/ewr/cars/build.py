import sys, os; os.environ['MCMCP_KEEP_FORCELOAD']='1'
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
script=open(sys.argv[1]).read()
x,y,z=map(int,sys.argv[2:5])
print(S.build(script, x, y, z, name=sys.argv[5], dry_run=(sys.argv[6]=='dry')))
