# Fix-up build for the EWR Cars showroom: "CHOOSE YOUR CAR" button panel + outdoor DELIVERY BAY.
# Same origin as showroom.py: world (88, 71, -86); local x = wx-88, y = wy-71, z = wz+86.

# ---- button panel on the north wall, just inside the drive-through entrance (world x 91..95, z -85) ----
CARS = [('FERRARI', 'Rosso red', '$250,000'), ('LAMBORGHINI', 'Yellow', '$220,000'), ('LAMBORGHINI', 'Orange', '$220,000'),
        ('LAMBORGHINI', 'Green', '$220,000'), ('LAMBORGHINI', 'Black', '$300,000')]   # prices: ewr_econ (cars/gen.py BUTTONS)
for i, (l1, l2, price) in enumerate(CARS):
    x = 3 + i                                              # world x 91..95
    b.sign(x, 3, 2, [l1, l2, price, 'press below'], facing='south', wall=True)
b.sign(5, 4, 2, ['CHOOSE', 'YOUR CAR', '- delivered to', 'the bay outside'], facing='south', wall=True)

print('ok')
