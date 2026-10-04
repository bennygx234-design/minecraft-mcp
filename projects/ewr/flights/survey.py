import sys, os, re, math, pickle
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); sys.path.insert(0, r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\planes')
from mcmcp.engine import Engine
import build_planes as B
from PIL import Image, ImageDraw
e = Engine()
pos = re.findall(r'\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]', e.cmd('execute as @e[type=happy_ghast,tag=ewr_plane] run data get entity @s Pos'))
rot = re.findall(r'\[(-?[\d.]+)f, (-?[\d.]+)f\]', e.cmd('execute as @e[type=happy_ghast,tag=ewr_plane] run data get entity @s Rotation'))
names = re.findall(r'"([^"]+)"', e.cmd('execute as @e[type=happy_ghast,tag=ewr_plane] run data get entity @s CustomName'))
d = pickle.load(open('hmap.pkl', 'rb')); H, X1, Z1, T = d['H'], d['X1'], d['Z1'], d['T']
x0, x1, z0, z1 = -90, 135, -60, 330
S = 4
im = Image.new('RGB', ((x1 - x0) * S, (z1 - z0) * S)); px = im.load()
for x in range(x0, x1):
    for z in range(z0, z1):
        h = H[x - X1][z - Z1]; t = T.get((x, z), '')
        c = (0, 0, 120) if 'water' in t else ((min(255, 80 + (h - 63) * 8),) * 3 if h > 63 else ((90, 90, 90) if ('andesite' in t or 'stone' in t or 'concrete' in t) else (30, 70, 30)))
        if 'yellow' in t: c = (200, 200, 0)
        if 'white_concrete' in t and h == 63: c = (220, 220, 220)
        for i in range(S):
            for j in range(S):
                px[(x - x0) * S + i, (z - z0) * S + j] = c
dr = ImageDraw.Draw(im)
out = []
for (x, y, z), (yw, pt), n in zip(pos, rot, names):
    x, z, yw = float(x), float(z), float(yw)
    size = n.split('(')[1].rstrip(')')
    sz = B.SIZES[size]
    fx, fz = -math.sin(math.radians(yw)), math.cos(math.radians(yw))
    rx, rz = -fz, fx
    k = sz['k'] if 'k' in sz else 1
    nose = (x + fx * sz['nose'], z + fz * sz['nose']); tail = (x - fx * (sz['length'] - sz['nose']), z - fz * (sz['length'] - sz['nose']))
    wc = (x - fx * 7 * k, z - fz * 7 * k); hs = sz['span'] / 2
    P = lambda p: ((p[0] - x0) * S, (p[1] - z0) * S)
    dr.line([P(nose), P(tail)], fill=(255, 0, 0), width=3)
    dr.line([P((wc[0] + rx * hs, wc[1] + rz * hs)), P((wc[0] - rx * hs, wc[1] - rz * hs))], fill=(255, 0, 0), width=3)
    dr.text(P((x + 1, z)), n[:10], fill=(255, 255, 0))
    out.append((n, round(x, 1), round(z, 1), yw))
for gx in range(x0 - x0 % 10, x1, 10):
    dr.line([((gx - x0) * S, 0), ((gx - x0) * S, 6)], fill=(255, 255, 255)); dr.text(((gx - x0) * S + 1, 8), str(gx), fill=(255, 255, 255))
for gz in range(z0 - z0 % 10, z1, 10):
    dr.line([(0, (gz - z0) * S), (6, (gz - z0) * S)], fill=(255, 255, 255)); dr.text((8, (gz - z0) * S - 5), str(gz), fill=(255, 255, 255))
im.save('apron.png')
for o in out: print(o)
