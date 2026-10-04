exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Fix: UPS roof HVAC unit sat on the 'S' of the roof lettering; move it clear and restore the letter.
H = 10
pbox(4, 6, -84, -82, H + 1, H + 3, "air")
rect(4, 6, -84, -82, H, "light_gray_concrete")
S_ROWS = ["###", "#..", "###", "..#", "###"]
for r, row in enumerate(S_ROWS):
    for c, px in enumerate(row):
        if px == "#":
            put(8 - r, -86 + c, H + 1, "yellow_concrete")
pbox(2, 4, -82, -80, H + 1, H + 2, "light_gray_concrete")
rect(2, 4, -82, -80, H + 3, "iron_bars")
