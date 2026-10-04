import sys,os
os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp import server as S
a=list(map(int,sys.argv[1:7])); out=sys.argv[7]; view=sys.argv[8] if len(sys.argv)>8 else 'south_east'
img=S.render(*a, view=view); open(out,'wb').write(img.data); print('ok',out)
