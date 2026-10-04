# north portico: remove the areaway railing that ran across the portico floor
for x in range(76, 105):
    for y in (8, 9):
        if not (79 <= x <= 83 or 85 <= x <= 89 or 91 <= x <= 95 or 97 <= x <= 101) or True:
            pass
for x in range(76, 105):
    b.set(x, 8, 41, 'air'); b.set(x, 9, 41, 'air')
# restore the back-row columns' shafts if they were at z 41 (columns at rz -3 -> z 42, footprint z 41..43)
for cx in (81, 99):
    for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        for y in (9,):
            b.set(cx + dx, y, 42 + dz, 'quartz_pillar')
    b.box(cx - 1, 8, 41, cx + 1, 8, 43, 'smooth_quartz')
