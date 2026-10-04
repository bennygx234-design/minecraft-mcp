exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\plib.py").read())
# EWR Cars dealership customer parking, south forecourt east of the delivery bay.
# Plan s 370..380 (world z -60..-70), t 38..52 (world x 98..112); floor blocks y=7 (world 71), walk y=8.
# Delivery bay (t 30..36), its sign posts at t 37, the showroom (s >= 381/382) are not touched.
# North strip (s 396..402) is not used: light-rail pillars stand in it at (399,28), (400,36), (400,45).
FY = 8
S1, S2, T1, T2 = 370, 380, 38, 52

# clear vegetation / old lamp posts / azaleas above the lot (canopy at s 380..381 y 11 is kept: s<=379 above y 10)
pbox(S1, S2, T1, T2, FY, 10, "air")
pbox(S1, 379, T1, T2, 11, 16, "air")
# level paved floor (the south part was grass one block lower)
pbox(S1, S2, T1, T2, FY - 2, FY - 2, "stone")
rect(S1, S2, T1, T2, FY - 1, "gray_concrete")
# aisle t 45..51 (+ t 52 apron) open to the south and east; south edge = slab step (0.5 per block)
rect(S1, S1, 45, T2, FY - 1, "smooth_stone_slab[type=bottom]")
pbox(S1, S1, 45, T2, FY - 2, FY - 2, "gray_concrete")
# directional arrows in the aisle (inlaid)
for s in (373, 377):
    put(s, 48, FY - 1, "white_concrete")
# bays: nose west (-t), t 38..44, wheel stops at t 39; lines at s 373, 377
pline(373, 373, 38, 44, FY)
pline(377, 377, 38, 44, FY)
bay(378, 380, 38, 44, FY, "-t", kind="acc", tag="dealer")      # in front of the showroom doors
bay(374, 376, 38, 44, FY, "-t", kind="std", tag="dealer")
bay(370, 372, 38, 44, FY, "-t", kind="ev", tag="dealer", charger=(371, 37))
# lamp posts on the line ends, outside the aisle (t 37 is outside the delivery bay)
for s in (373, 377):
    put(s, 37, FY, "polished_blackstone_wall"); put(s, 37, FY + 1, "polished_blackstone_wall")
    put(s, 37, FY + 2, "sea_lantern")
# sign
x, z = P(377, 52)
b.sign(x, FY, z, ["CUSTOMER", "PARKING", "EWR Cars", "<- showroom"], facing="east", wall=False)
report_bays()
for bb in BAYS:
    print(bb["kind"], bb["world"], bb["yaw"])
