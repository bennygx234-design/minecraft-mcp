# shared helpers for the landside builds (exec'd after kit.py)
FONT = {
    "P": ["###", "#.#", "###", "#..", "#.."],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "M": ["#.#", "###", "###", "#.#", "#.#"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "N": ["#.#", "###", "###", "###", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "C": [".##", "#..", "#..", "#..", ".##"],
    "-": ["...", "...", "###", "...", "..."],
    " ": ["...", "...", "...", "...", "..."],
}


def glyph(ch, s0, t, y0, block):
    """3x5 glyph on a plane of constant t, readable from the east (+t): columns advance toward +s."""
    rows = FONT[ch]
    for r, row in enumerate(rows):
        for c, px in enumerate(row):
            if px == "#":
                put(s0 + c, t, y0 + 4 - r, block)


def etext(s0, t, y0, text, block):
    for i, ch in enumerate(text):
        glyph(ch, s0 + 4 * i, t, y0, block)


CAR_COLS = {"white_concrete": 5, "black_concrete": 4, "gray_concrete": 3, "light_gray_concrete": 3,
            "red_concrete": 2, "blue_concrete": 2, "yellow_concrete": 1, "green_concrete": 1,
            "cyan_concrete": 1, "orange_concrete": 1}
_cc = [k for k, w in CAR_COLS.items() for _ in range(w)]


def car(s, t, y, along="t", col=None):
    """1x2 car; along='t' means 2 long in the t direction (t, t+1)."""
    c = col or rng.choice(_cc)
    put(s, t, y, c)
    if along == "t":
        put(s, t + 1, y, c)
    else:
        put(s + 1, t, y, c)


def lamp_post(s, t, y, h=3):
    for k in range(h):
        put(s, t, y + k, "stone_brick_wall" if k == 0 else "iron_bars")
    put(s, t, y + h, "lantern[hanging=false]")
