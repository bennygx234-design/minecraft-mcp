import sys; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
from mcmcp.engine import Engine
e=Engine()
for c in sys.argv[1:]:
    print('>',c); print(e.cmd(c))
