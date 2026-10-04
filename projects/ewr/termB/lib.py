# Terminal B helpers (exec after kit.py). Plan facings: 'N'=+s, 'S'=-s, 'E'=+t (airside), 'W'=-t (landside)
FACE = {"N": "north", "S": "south", "E": "east", "W": "west"}
BACK = {"N": (-1, 0), "S": (1, 0), "E": (0, -1), "W": (0, 1)}   # where the supporting block is (ds, dt)


def psign(s, t, y, lines, facing, backing=None, wood="birch"):
    """wall sign at plan (s,t) readable from `facing` side; optionally place its backing block."""
    if backing:
        ds, dt = BACK[facing]
        put(s + ds, t + dt, y, backing)
    x, z = P(s, t)
    b.sign(x, y, z, lines, facing=FACE[facing], wall=True, wood=wood)


def pstairs(s, t, y, facing):
    """single stair block; facing = plan dir of the high back side? (Minecraft facing = direction the step climbs toward)"""
    put(s, t, y, f"smooth_quartz_stairs[facing={FACE[facing]},half=bottom]")


def seat(s, t, y, looks, block="polished_andesite_stairs"):
    """chair whose sitter looks toward plan dir `looks`"""
    x, z = P(s, t)
    b.chair(x, y, z, FACE[looks], block)


def octa(dx, dz, r):
    return max(abs(dx), abs(dz)) <= r and abs(dx) + abs(dz) <= r + r // 2


FONT = {
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "1": [".#", "##", ".#", ".#", ".#"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
    " ": ["..", "..", "..", "..", ".."],
}


def text_width(txt):
    return sum(len(FONT[c][0]) for c in txt) + len(txt) - 1


def pixel_text_west(txt, s_start, t, y_top, block):
    """letters readable from the west (viewer looks +t): text runs from high s to low s."""
    s = s_start
    for c in txt:
        g = FONT[c]
        for r, row in enumerate(g):
            for i, ch in enumerate(row):
                if ch == "#":
                    put(s - i, t, y_top - r, block)
        s -= len(g[0]) + 1
