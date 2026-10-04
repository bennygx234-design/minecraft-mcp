exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\termB\lib.py").read())
# ---- Terminal B headhouse: plan s 121..165, t -99..-82 ------------------------------------------
S1, S2, T1, T2 = 121, 165, -99, -82
W = "white_concrete"
GL = "light_blue_stained_glass"
FLOOR = {"smooth_quartz": 4, "polished_diorite": 1}

pbox(S1, S2, T1, T2, 0, 24, "air")
rect(S1, S2, T1, T2, -1, FLOOR)            # arrivals floor
rect(S1, S2, T1, T2, 8, "smooth_quartz")   # departures floor / arrivals ceiling
rect(S1, S2, T1, T2, 17, W)                # roof

# ---- shell ------------------------------------------------------------------------------------
for y in range(0, 17):
    if y == 8:
        continue
    for s in range(S1, S2 + 1):
        mull = (s - S1) % 4 == 0
        put(s, T1, y, W if mull or y in (7, 16) else GL)                 # west curtain wall
        put(s, T2, y, W if mull or y in (0, 7, 9, 16) else "glass")      # east (airside) wall
    for t in range(T1, T2 + 1):
        for s in (S1, S2):
            put(s, t, y, W if (t - T1) % 4 == 0 or y in (0, 7, 16) else GL)
# floor edge band
for s in range(S1, S2 + 1):
    put(s, T1, 8, "light_gray_concrete"); put(s, T2, 8, "light_gray_concrete")
for t in range(T1, T2 + 1):
    put(S1, t, 8, "light_gray_concrete"); put(S2, t, 8, "light_gray_concrete")

# skylights + lights
for s in range(S1 + 2, S2 - 1):
    put(s, -93, 17, "glass"); put(s, -88, 17, "glass")
for s in range(S1 + 3, S2 - 1, 5):
    for t in range(T1 + 3, T2 - 1, 5):
        put(s, t, 8, "sea_lantern")
    for t in (-96, -90.5, -85):
        put(s, t, 17, "sea_lantern")
# parapet + rooftop "TERMINAL B" fascia (reads from the landside / AirTrain)
for s in range(S1, S2 + 1):
    put(s, T2, 18, W)
for t in range(T1, T2 + 1):
    put(S1, t, 18, W); put(S2, t, 18, W)
pbox(S1 + 1, S2 - 1, T1, T1, 18, 24, "blue_concrete")
pbox(S1 + 1, S2 - 1, T1 + 1, T1 + 1, 18, 24, W)
pixel_text_west("TERMINAL B", 163, T1, 23, "white_concrete")

# ================= GROUND LEVEL (y0..7): arrivals, baggage claim, customs =====================
# street doors on the landside facade
for s0 in (125, 133, 141, 151, 161):
    pbox(s0, s0 + 1, T1, T1, 0, 2, "air")
# public arrivals hall t -98..-96; glass screen at t -95 with exits
pbox(122, 164, -95, -95, 0, 7, "light_gray_stained_glass")
pbox(122, 164, -95, -95, 0, 0, W)
pbox(127, 130, -95, -95, 0, 2, "air")      # domestic claim opening
pbox(161, 162, -95, -95, 0, 2, "air")      # international customs exit
psign(160, -96, 3, ["Customs Exit", "International", "Arrivals"], "W")
psign(131, -96, 3, ["Baggage Claim", "Carousels 1-2"], "W")
# car rental / info desks and benches in the public hall
for s in range(145, 150):
    put(s, -98, 0, "polished_andesite")
psign(147, -97, 2, ["Ground", "Transportation", "Taxi - Bus - Car"], "E", wood="spruce")
put(147, -98, 1, "light_gray_concrete")
for s in (123, 124, 152, 153, 154, 165 - 9):
    seat(s, -98, 0, "E", "quartz_stairs")
for s in (122, 164):
    put(s, -98, 0, "potted_bamboo")

# landside stairs (arrivals hall <-> departures hall), climbing +s, top flush with departures floor
x, z = P(136, -98)
b.stairs_run(x, 0, z, "north", 9, "smooth_quartz_stairs", width=2, support="white_concrete")
pbox(136, 143, -98, -97, 8, 8, "air")

# wall between domestic claim and the secure international side
pbox(137, 137, -94, -85, 0, 7, W)
pbox(137, 137, -94, -85, 3, 5, "light_gray_stained_glass")

def carousel(c, num):
    """racetrack bag belt along t at plan s=c"""
    for t in range(-93, -85):
        for s in (c - 1, c + 1):
            put(s, t, 0, "polished_blackstone_slab[type=top]")
    for s in (c - 1, c, c + 1):
        put(s, -93, 0, "polished_blackstone_slab[type=top]"); put(s, -86, 0, "polished_blackstone_slab[type=top]")
    pbox(c, c, -92, -87, 0, 1, "light_gray_concrete")
    put(c, -87, 2, "black_concrete"); put(c, -87, 3, "black_concrete")
    psign(c, -88, 3, ["Carousel %d" % num], "W")
    bags = ["blue_shulker_box", "red_shulker_box", "black_shulker_box", "gray_shulker_box", "lime_shulker_box"]
    for k, t in enumerate(range(-92, -86, 2)):
        put(c - 1, t, 1, bags[(k + num) % 5]); put(c + 1, t + 1, 1, bags[(k + num + 2) % 5])

# domestic claim (south)
carousel(126, 1); carousel(132, 2)
# airside stairs from the departures sterile corridor down into immigration (climbing -s)
x, z = P(139, -83)
b.stairs_run(x, 0, z, "south", 9, "smooth_quartz_stairs", width=2, support="white_concrete")
pbox(132, 139, -84, -83, 8, 8, "air")

# CBP passport control: booth line at s=145, queue s 140..144
for t in range(-94, -82):
    if t % 2 == 0:
        put(145, t, 0, "polished_andesite")
        put(145, t, 1, "light_gray_stained_glass"); put(145, t, 2, "light_gray_stained_glass")
        put(145, t, 3, "smooth_quartz_slab[type=bottom]")
        psign(144, t, 1, ["CBP", "Passport", "Control"], "S")
for t in range(-93, -84, 2):           # queue stanchions
    put(142, t, 0, "iron_bars")
for t in range(-92, -83, 2):
    put(141, t, 0, "iron_bars")
psign(143, -95 + 1, 4, ["U.S. Customs &", "Border Protection", "All Passports"], "S", backing="light_gray_concrete")
# international claim (north) + customs desk
carousel(150, 3); carousel(156, 4)
for t in (-94, -93):
    put(161, t, 0, "green_concrete"); put(163, t, 0, "red_concrete")
psign(160, -93, 1, ["Nothing to", "Declare"], "S", wood="spruce")
psign(164, -93, 1, ["Goods to", "Declare"], "N", wood="spruce")

# ================= DEPARTURES (y9..16): check-in, security, sterile corridor ===================
# AirTrain entrance (station platform is just west at t -107..-100, deck y8)
pbox(149, 153, T1, T1, 9, 11, "air")
pbox(149, 153, T1, T1, 12, 12, "blue_concrete")
psign(151, -98, 12, ["AirTrain", "Terminal B", "<- Station"], "E", wood="spruce")
# railings around stair holes
for s in range(136, 144):
    put(s, -96, 9, "glass")
put(135, -98, 9, "glass"); put(135, -97, 9, "glass")
for s in range(132, 140):
    put(s, -85, 9, "glass")
put(140, -84, 9, "glass"); put(140, -83, 9, "glass")

def island(sa, sb, airlines):
    """check-in island: counter t-93, agents t-92, bag belt t-91, back wall t-90 with airline signs"""
    for s in range(sa, sb + 1):
        put(s, -93, 9, "white_concrete")
        put(s, -93, 10, "smooth_quartz_slab[type=bottom]")
        put(s, -91, 9, "polished_blackstone_slab[type=bottom]")
        pbox(s, s, -90, -90, 9, 13, "light_gray_concrete")
        put(s, -90, 14, "blue_concrete")
    for k, name in enumerate(airlines):
        s = sb - 1 - k * 3
        if s >= sa:
            psign(s, -91, 12, [name, "Check-in"], "W")
            put(s, -92, 9, "polished_andesite_stairs[facing=east]")   # agent stool
    # end caps
    for s in (sa, sb):
        put(s, -92, 9, "white_concrete")

island(122, 134, ["Lufthansa", "SWISS", "Austrian", "SAS"])
island(137, 147, ["Emirates", "Air India", "TAP Portugal", "El Al"])
island(155, 164, ["Delta", "Alaska", "Air Canada"])
# FIDS boards on the island ends facing the central concourse
pbox(147, 147, -93, -90, 10, 14, "black_concrete")
pbox(155, 155, -93, -90, 10, 14, "black_concrete")
fids = [["DEPARTURES", "LH 403 FRA 18:05", "EK 202 DXB 22:30"],
        ["DEPARTURES", "DL 117 CDG 19:40", "TP 204 LIS 21:10"],
        ["AI 144 BOM 20:15", "LY 26 TLV 23:55", "AS 33 SEA 17:50"],
        ["SK 910 CPH 18:45", "LX 19 ZRH 22:05", "OS 90 VIE 17:30"]]
for k, t in enumerate(range(-93, -89)):
    psign(148, t, 13, fids[k], "N")
    psign(154, t, 13, fids[(k + 2) % 4], "S")
for k, t in enumerate(range(-93, -89)):
    psign(148, t, 11, ["Gates B40-B68", "-> Security"], "N")
    psign(154, t, 11, ["Gates B40-B68", "-> Security"], "S")
# benches & planters in the landside hall
for s in list(range(124, 133, 1)) + list(range(157, 164)):
    if s % 3:
        seat(s, -97, 9, "W", "smooth_quartz_stairs")
for s in (123, 135, 148, 154, 164):
    put(s, -98, 9, "potted_azalea_bush")

# TSA checkpoint at t-87: lanes at s = 145,148,151,154,157 (post c-1, walk c, x-ray c+1)
pbox(122, 164, -87, -87, 9, 11, "light_gray_stained_glass")
for c in (145, 148, 151, 154, 157):
    pbox(c - 1, c - 1, -87, -87, 9, 11, "iron_block")     # detector post
    pbox(c, c, -87, -87, 9, 10, "air")                    # walk-through
    put(c, -87, 11, "iron_block")                         # lintel
    put(c, -87, 9, "light_weighted_pressure_plate")
    for t in range(-89, -84):                             # belt
        put(c + 1, t, 9, "polished_blackstone_slab[type=top]")
    pbox(c + 1, c + 1, -87, -87, 9, 10, "gray_concrete")  # x-ray tunnel
    put(c + 1, -87, 11, "black_concrete")
    put(c + 1, -88, 10, "gray_carpet")
    psign(c, -88, 11, ["TSA", "Lane %d" % ((c - 142) // 3)], "W")
    put(c - 1, -86, 9, "gray_concrete")                   # bin table / officer post
pbox(144, 158, -87, -87, 12, 13, "blue_concrete")
psign(151, -88, 13, ["TSA Security", "Checkpoint", "Gates B40-B68"], "W")
psign(151, -86, 13, ["Welcome to", "Terminal B", "Gates ->"], "E")
# queue stanchions
for s in range(140, 162, 2):
    put(s, -89, 9, "iron_bars")

# ---- sterile corridor t -86..-83 + connectors on the east wall -------------------------------
for c in (127, 143, 158):
    pbox(c - 1, c + 1, T2, T2, 9, 11, "air")
    pbox(c - 1, c + 1, T2, T2, 12, 12, "blue_concrete")
psign(127, -83, 12, ["Gates B40-B47", "Satellite B1"], "W")
psign(143, -83, 12, ["Gates B51-B57", "Satellite B2"], "W")
psign(158, -83, 12, ["Gates B60-B68", "Satellite B3"], "W")
psign(131, -84, 11, ["International", "Arrivals", "Passport Control"], "N")
# duty free (south end)
for s in range(122, 126):
    pbox(s, s, -83, -83, 9, 11, {"purple_stained_glass": 1, "pink_stained_glass": 1, "orange_stained_glass": 1})
    put(s, -86, 9, "smooth_quartz")
    put(s, -86, 10, "potted_white_tulip" if s % 2 else "potted_allium")
psign(124, -84, 12, ["DUTY FREE", "Americas"], "W", backing=None)
pbox(122, 125, -85, -84, 12, 12, "blue_concrete")
# seating near connector 1
for s in (129, 130):
    seat(s, -86, 9, "E")
# food court s 145..156
for s in range(145, 157):
    put(s, -83, 9, "smooth_stone_slab[type=top]" if s % 3 else "smoker[facing=west]")
    put(s, -83, 11, "orange_concrete")
psign(150, -84, 11, ["Garden State", "Diner"], "W", wood="spruce")
psign(153, -84, 11, ["Pizza &", "Coffee"], "W", wood="spruce")
for s in range(146, 156, 3):
    put(s, -85, 9, "oak_fence"); put(s, -85, 10, "white_carpet")
    seat(s - 1, -85, 9, "N", "oak_stairs"); seat(s + 1, -85, 9, "S", "oak_stairs")
# duty free (north end)
for s in range(160, 165):
    pbox(s, s, -83, -83, 9, 11, {"yellow_stained_glass": 1, "light_blue_stained_glass": 1, "lime_stained_glass": 1})
    put(s, -86, 9, "smooth_quartz")
    put(s, -86, 10, "potted_red_tulip" if s % 2 else "potted_cornflower")
psign(162, -84, 12, ["DUTY FREE", "Fragrance &", "Spirits"], "W")
pbox(160, 164, -85, -84, 12, 12, "blue_concrete")
# hanging lanterns along the corridor
for s in range(123, 165, 4):
    put(s, -85, 16, "lantern[hanging=true]")
