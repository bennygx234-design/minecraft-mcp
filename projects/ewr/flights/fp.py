import sys, math, pickle
sys.path.insert(0, r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\planes')
import build_planes as B
def cells(livery, size, x, z, yaw):
    """2-D occupied cells of a ghast-anchored flyable plane"""
    out = set()
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    for p in B.model(livery, size):
        for (px, py, pz) in p.corners() + [p.center]:
            pass
        xs = [q[0] for q in p.corners()]; zs = [q[2] for q in p.corners()]
        n = 4
        for i in range(n + 1):
            for j in range(n + 1):
                lx = min(xs) + (max(xs) - min(xs)) * i / n; lz = min(zs) + (max(zs) - min(zs)) * j / n
                # MC yaw: local +z -> (-sin, cos)
                wx = x + lx * c - lz * s; wz = z + lx * s + lz * c
                out.add((math.floor(wx), math.floor(wz)))
    return out
PARKED = [('jetblue','narrow',-0.5,243.15,-180),('delta','narrow',-0.5,225.85,0),('alaska','narrow',22.5,225.85,0),
          ('american','narrow',22.5,243.15,-180),('american','narrow',31.5,241.4,61.2),
          ('emirates','wide',7.06,175.5,90),('lufthansa','narrow',-1.85,155.5,90),('delta','regional',-1.65,183.5,90),
          ('alaska','regional',21.41,151.5,90)]
occ = {}
for p in PARKED:
    for cc in cells(*p): occ.setdefault(cc, []).append(p[0])
best = []
for size in ('narrow', 'regional'):
  for yaw in (90, 180, -90, 0):
    for x in range(5, 34):
        for z in range(185, 215):
            cs = cells('emirates', size, x + 0.5, z + 0.5, yaw)
            hit = sum(1 for c in cs if c in occ)
            if hit == 0 and all(-12 <= c[0] <= 36 for c in cs):
                best.append((size, yaw, x, z))
print(len(best)); print(best[:80])
