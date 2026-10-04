# north maintenance area helpers (exec after kit.py)
FONT = {
 "H": ["X.X","X.X","XXX","X.X","X.X"], "A": [".X.","X.X","XXX","X.X","X.X"],
 "N": ["X..X","XX.X","X.XX","X..X","X..X"], "G": ["XXX","X..","X.X","X.X","XXX"],
 "R": ["XX.","X.X","XX.","X.X","X.X"], "1": [".X.","XX.",".X.",".X.","XXX"],
 "2": ["XX.","..X",".X.","X..","XXX"], "3": ["XX.","..X",".X.","..X","XX."],
 "F": ["XXX","X..","XX.","X..","X.."], "B": ["XX.","X.X","XX.","X.X","XX."],
 "O": ["XXX","X.X","X.X","X.X","XXX"], " ": ["."],
}
def text_width(st):
    return sum(len(FONT[c][0]) for c in st) + len(st) - 1
def text_south(s, t0, ytop, st, block):
    """block letters on plane s, readable from the south (-s); columns run +t"""
    t = t0
    for c in st:
        g = FONT[c]; w = len(g[0])
        for r, row in enumerate(g if c != " " else []):
            for k, ch in enumerate(row):
                if ch == "X":
                    put(s, t + k, ytop - r, block)
        t += w + 1
def text_east(t, s0, ytop, st, block):
    """block letters on plane t, readable from the east (+t); columns run +s"""
    s = s0
    for c in st:
        g = FONT[c]; w = len(g[0])
        for r, row in enumerate(g if c != " " else []):
            for k, ch in enumerate(row):
                if ch == "X":
                    put(s + k, t, ytop - r, block)
        s += w + 1
def bizjet(v, stripe="blue_concrete"):
    """small business jet, nose to local -z, ~12 long, 11 span"""
    w = "white_concrete"
    v.box(0, 1, -5, 0, 2, 5, w); v.set(0, 1, -6, w)
    v.set(0, 2, -5, "black_stained_glass")
    for z in (-3, -1, 1): v.set(0, 2, z, "light_blue_stained_glass")
    v.box(0, 1, -4, 0, 1, 4, stripe)
    for i in range(1, 6):
        v.box(-i, 1, 0 + i // 3, -i, 1, 1 + i // 3, w); v.box(i, 1, 0 + i // 3, i, 1, 1 + i // 3, w)
    v.box(-1, 2, 2, -1, 2, 3, "light_gray_concrete"); v.box(1, 2, 2, 1, 2, 3, "light_gray_concrete")
    v.box(0, 3, 4, 0, 4, 5, stripe); v.box(-2, 5, 5, 2, 5, 5, w)
    v.set(0, 0, -4, "black_concrete"); v.set(-1, 0, 1, "black_concrete"); v.set(1, 0, 1, "black_concrete")
def tug(v, color="yellow_concrete"):
    """aircraft tug 2x4, front to local -z"""
    v.box(0, 0, -2, 1, 0, 1, "black_concrete")
    v.box(0, 1, -2, 1, 1, 1, color)
    v.set(0, 2, 0, "black_concrete"); v.set(1, 2, 0, "black_concrete")
    v.set(0, 2, 1, "spruce_stairs[facing=south]"); v.set(1, 2, -1, "lever[face=floor,facing=north]")
    v.set(0, 1, -3, "iron_bars")
def gpu(v):
    v.box(0, 0, 0, 1, 1, 1, "yellow_terracotta"); v.set(0, 2, 0, "iron_trapdoor[half=bottom]")
