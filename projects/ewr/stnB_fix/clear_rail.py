exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# Open the Station B east rail onto Terminal B departures doorway (s 149..153).
for s in range(149, 154):
    for y in (9, 10):
        put(s, -100, y, 'air')
# Floor at y=8 between t=-100 and the terminal wall (t=-99) is already continuous
# (smooth_quartz at t=-100, light_gray_concrete threshold at t=-99) -- no fill needed.
