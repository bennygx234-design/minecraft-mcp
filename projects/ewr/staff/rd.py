import sys; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); from mcmcp import server as S
a=[int(v) for v in sys.argv[1:7]]
print(S.scan_region(*a))
