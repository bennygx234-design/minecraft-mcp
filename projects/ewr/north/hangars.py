exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\north\lib.py").read())

SB = 350          # back wall
EAVE = 14


def hangar(tw, te, sf, num, livery, big, rise, accent, ext_w, ext_e, tagline):
    tc = (tw + te) // 2
    hw = (te - tw) / 2.0

    def h(t):
        if t < tw or t > te:
            return EAVE
        dt = t - tc
        return EAVE + max(1, int(round(rise * math.sqrt(max(0.0, 1 - (dt / (hw + 0.5)) ** 2)))))

    def lo_of(t):
        top = h(t)
        return min(min(h(t - 1), top, h(t + 1)) + 1, top)

    # floor
    rect(sf, SB, tw, te, -1, "light_gray_concrete")
    # side + back walls
    for t in (tw, te):
        pbox(sf, SB, t, t, 0, EAVE, "light_gray_concrete")
        pbox(sf, SB, t, t, 0, 1, "gray_concrete")
    pbox(SB, SB, tw, te, 0, EAVE, "light_gray_concrete")
    pbox(SB, SB, tw, te, 0, 1, "gray_concrete")
    # exterior ribs + clerestory on exterior side walls
    for t, ext in ((tw, ext_w), (te, ext_e)):
        if not ext:
            continue
        for s in range(sf + 1, SB):
            if (s - sf) % 4 == 0:
                pbox(s, s, t, t, 2, EAVE, "white_concrete")
            else:
                pbox(s, s, t, t, 10, 12, "light_gray_stained_glass")
    # back wall windows (office level)
    for t in range(tw + 2, te - 1):
        if (t - tw) % 4 != 0:
            put(SB, t, 7, "glass"); put(SB, t, 8, "glass")
    # front: piers + header, opening y0..8
    pbox(sf, sf, tw, te, 9, EAVE, "white_concrete")
    pbox(sf, sf, tw + 1, te - 1, 0, 8, "air")
    for t in (tw, te):
        pbox(sf, sf, t, t, 0, 8, "light_gray_concrete")
        for y in range(0, 3):
            put(sf, t, y, "yellow_concrete" if y % 2 == 0 else "black_concrete")
    pbox(sf, sf, tw, te, EAVE, EAVE, "gray_concrete")       # cornice line
    # gables front/back + roof
    for t in range(tw, te + 1):
        top = h(t)
        lo = lo_of(t)
        for s in (sf, SB):
            if top > EAVE + 1:
                pbox(s, s, t, t, EAVE + 1, top - 1, "light_gray_concrete")
        for s in range(sf, SB + 1):
            rib = (s - sf) % 6 == 0 or s in (sf, SB)
            blk = "white_concrete" if rib else "light_gray_concrete"
            if not rib and abs(t - tc) <= 1 and (s - sf) % 2 == 1:
                blk = "light_blue_stained_glass"           # crown skylight
            pbox(s, s, t, t, lo, top, blk)
            if not rib and abs(t - tc) == int(hw // 2) and (s - sf) % 6 == 3:
                put(s, t, top, "sea_lantern")
        put(sf - 1, t, top, "smooth_stone_slab[type=bottom]")   # roof trim over the doors
    # interior: lanterns hung from the roof on chains
    for s in range(sf + 3, SB - 4, 6):
        for dt in (-int(hw * 0.75), -int(hw // 4), int(hw // 4), int(hw * 0.75)):
            tt = tc + dt
            lo = lo_of(tt)
            for y in range(lo - 3, lo):
                put(s, tt, y, "iron_chain")
            put(s, tt, lo - 4, "lantern[hanging=true]")
    # "HANGAR" on the header, big numeral on the gable
    tw_txt = text_width("HANGAR")
    text_south(sf, tc - tw_txt // 2, 13, "HANGAR", accent)
    text_south(sf, tc - 1, EAVE + 5, num, accent)
    # door track: top rails + parked door leaves + floor rails
    pbox(sf - 2, sf - 1, tw, te, 9, 9, "polished_blackstone")
    for t in (tw, te):
        pbox(sf - 2, sf - 1, t, t, 0, 8, "iron_block")
        put(sf - 2, t, 4, "gray_concrete"); put(sf - 1, t, 4, "gray_concrete")
    pbox(sf - 2, sf - 1, tw + 1, te - 1, -1, -1, "polished_blackstone")
    for t in ((te,) if tw == -68 else (tw, te)):  # wall signs on the door leaves
        x, z = P(sf - 3, t)
        b.sign(x, 3, z, ["HANGAR " + num, tagline, "", "EWR North"], facing="south")
    # floor markings: centreline + bay edge dashes
    rect(sf - 2, SB - 6, tc, tc, -1, "yellow_concrete")
    for s in range(sf + 1, SB - 4):
        if s % 2 == 0:
            put(s, tw + 1, -1, "yellow_concrete"); put(s, te - 1, -1, "yellow_concrete")
    # ---- back strip: workshop (ground) + mezzanine offices ----
    MZ = 5
    rect(346, 349, tw + 1, te - 1, MZ, "smooth_stone")
    for t in range(tw + 4, te - 1, 6):
        pbox(346, 346, t, t, 0, MZ - 1, "gray_concrete")
    for t in range(tw + 3, te - 2, 4):
        x, z = P(347, t)
        b.lamp(x, MZ - 1, z, "lantern", hanging=True)
    # offices s 347..349 on the mezzanine, glass front, walkway at s 346
    pbox(347, 347, tw + 1, te - 1, MZ + 1, MZ + 3, "light_gray_stained_glass_pane")
    rect(347, 349, tw + 1, te - 1, MZ + 4, "smooth_stone")
    ox = list(range(tw + 1, te, 8))
    for t in ox:
        if t > tw + 1:
            pbox(347, 349, t, t, MZ + 1, MZ + 3, "white_concrete")
        dt = t + 3
        if dt < te - 1:
            x, z = P(347, dt)
            b.door(x, MZ + 1, z, "north", "birch_door")
            for tt in (dt - 2, dt - 1):
                if tt > tw:
                    x2, z2 = P(349, tt)
                    b.set(x2, MZ + 1, z2, "spruce_slab[type=top]")
            x3, z3 = P(348, dt - 1); b.chair(x3, MZ + 1, z3, "north")
            if dt + 1 < te - 1 and dt + 1 not in ox:
                x4, z4 = P(349, dt + 1); b.bookshelves(x4, MZ + 1, z4, x4, MZ + 2, z4)
                x5, z5 = P(348, dt + 1); b.plant(x5, MZ + 1, z5, "potted_bamboo")
            if dt - 2 > tw:
                x6, z6 = P(349, dt - 2); b.set(x6, MZ + 2, z6, "lantern[hanging=false]")
    for t in range(tw + 2, te - 1, 4):
        put(348, t, MZ + 4, "sea_lantern")
    # stairs up to the mezzanine along the west wall
    for k in range(5):
        for tt in (tw + 1, tw + 2):
            x, z = P(341 + k, tt)
            b.set(x, k, z, "polished_andesite_stairs[facing=north]")
            if k > 0:
                b.box(x, 0, z, x, k - 1, z, "polished_andesite")
    # workshop under the mezzanine, along the back wall s 349
    tools = ["crafting_table", "smithing_table", "anvil[facing=east]", "grindstone[face=floor,facing=north]",
             "chest", "barrel", "blast_furnace[facing=south]", "stonecutter[facing=south]", "chest",
             "fletching_table", "cartography_table", "barrel", "lectern[facing=south]", "chipped_anvil[facing=east]"]
    i = 0
    for t in range(tw + 4, te - 1):
        name = tools[i % len(tools)]; i += 1
        x, z = P(349, t)
        if name == "chest":
            b.chest(x, 0, z, "south", [("iron_ingot", 16), ("redstone", 8), ("iron_bars", 12)])
        elif name == "barrel":
            b.barrel(x, 0, z, "up", [("coal", 32), ("copper_ingot", 16)])
        else:
            b.set(x, 0, z, name)
        if t % 3 == 0:
            put(349, t, 2, "iron_trapdoor[facing=south,half=top,open=true]")   # tool board
    for t in range(tw + 5, te - 3, 5):            # workbenches at s 347
        put(347, t, 0, "smooth_stone_slab[type=top]"); put(347, t + 1, 0, "smooth_stone_slab[type=top]")
        put(347, t, 1, "lantern[hanging=false]")
    x, z = P(SB - 1, tc)
    b.sign(x, 10, z, ["HANGAR " + num, tagline, "Maintenance", "Line Ops"], facing="south")
    # aircraft, nose toward the door
    L = 15 if big else 11
    sc = sf + 2 + L + 1
    v = at(sc, tc, 0, rot=2)
    plane(v, livery, big)
    span = 14 if big else 10
    ex = span // 2 + 1
    for xx in (-ex, ex):          # maintenance stands in front of the engines
        v.box(xx, 0, -5, xx, 1, -5, "scaffolding")
    v.box(-3, 0, -L + 3, -3, 2, -L + 3, "scaffolding")
    v.box(-4, 0, 0, -4, 0, 1, "red_concrete")      # tool carts
    v.set(-4, 1, 0, "chest[facing=west]")
    v.box(4, 0, 5, 4, 0, 6, "red_concrete"); v.set(4, 1, 5, "anvil[facing=north]")


hangar(-100, -68, 312, "1", "united", True, 6, "blue_concrete", True, False, "United TechOps")
hangar(-68, -44, 318, "2", "fedex", False, 5, "purple_concrete", False, False, "FedEx Line Maint")
hangar(-44, -20, 318, "3", "delta", False, 5, "red_concrete", False, False, "Delta TechOps")
