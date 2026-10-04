# Fix-up build for the EWR Cars showroom: "CHOOSE YOUR CAR" button panel + outdoor DELIVERY BAY.
# Same origin as showroom.py: world (88, 71, -86); local x = wx-88, y = wy-71, z = wz+86.

# ---- button panel on the north wall, just inside the drive-through entrance (world x 91..95, z -85) ----
b.box(3, 1, 1, 7, 4, 1, 'black_concrete')
b.box(3, 1, 1, 7, 1, 1, 'red_concrete')
b.box(3, 1, 2, 7, 4, 2, 'air')
CARS = [('FERRARI', 'Rosso red', '$250,000'), ('LAMBORGHINI', 'Yellow', '$220,000'), ('LAMBORGHINI', 'Orange', '$220,000'),
        ('LAMBORGHINI', 'Green', '$220,000'), ('LAMBORGHINI', 'Black', '$300,000')]   # prices: ewr_econ (cars/gen.py BUTTONS)
for i, (l1, l2, price) in enumerate(CARS):
    x = 3 + i                                              # world x 91..95
    b.set(x, 2, 2, 'stone_button[face=wall,facing=south]')  # world y 73, z -84
    b.sign(x, 3, 2, [l1, l2, price, 'press below'], facing='south', wall=True)
b.sign(5, 4, 2, ['CHOOSE', 'YOUR CAR', '- delivered to', 'the bay outside'], facing='south', wall=True)

# ---- delivery bay: world x 90..96, z -71..-63, floor y=71; cars face west (the highway) ----
b.box(0, -4, 15, 8, -1, 23, 'stone')
b.box(0, 1, 15, 8, 6, 23, 'air')
b.box(2, 0, 15, 8, 0, 23, 'smooth_stone')
for (xa, za, xb, zb) in ((2, 15, 8, 15), (2, 23, 8, 23), (2, 15, 2, 23), (8, 15, 8, 23)):
    b.box(xa, 0, za, xb, 0, zb, 'yellow_concrete')
for z in (18, 21):                                         # slot dividers
    b.box(3, 0, z, 7, 0, z, 'white_concrete')
# ramp up to the highway's raised edge (floor top 72 -> 72.5 -> 73.5 -> road 74)
b.box(1, 0, 15, 1, 0, 23, 'smooth_stone')
b.box(1, 1, 15, 1, 1, 23, 'smooth_stone_slab')
b.box(0, 0, 15, 0, 1, 23, 'smooth_stone')
b.box(0, 2, 15, 0, 2, 23, 'smooth_stone_slab')
# sign posts
b.set(9, 1, 16, 'yellow_concrete')
b.sign(9, 2, 16, ['DELIVERY BAY', 'cars ordered', 'at the panel', 'inside'], facing='east', wall=False)
b.set(9, 1, 22, 'yellow_concrete')
b.sign(9, 2, 22, ['DELIVERY BAY', 'max 3 cars;', 'oldest is', 'recycled'], facing='east', wall=False)
print('ok')
