exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
# rental car center: roof band should be a parapet ring, not a full yellow slab
pbox(32, 49, -141, -129, 11, 11, "air")
for s in range(33, 49, 5):
    for t in (-139, -131):
        put(s, t, 11, "lantern[hanging=false]")
pbox(36, 44, -138, -132, 11, 12, "light_gray_concrete")   # rooftop plant room
