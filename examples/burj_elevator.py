# Bubble-column elevator for the Burj Khalifa (run with origin = tower centre at plaza level: 170, 68, -135).
# Replaces the ladder shaft. Up car: soul sand base. Down car: magma base. Lobby floor y=0, deck floor y=152.
DECK = 152

# shaft walls: 5 x 3 glass tube from the lobby floor to the deck floor
b.walls(-2, 0, -1, 2, DECK, 1, "white_stained_glass")
for y in range(1, DECK + 1):
    b.set(0, y, 0, "sea_lantern" if y % 8 == 0 else "white_stained_glass")       # lit divider
    b.set(-1, y, 0, "bubble_column[drag=false]")                                  # up
    b.set(1, y, 0, "bubble_column[drag=true]")                                    # down
b.set(-1, 0, 0, "soul_sand")
b.set(1, 0, 0, "magma_block")
b.set(0, 0, 0, "polished_blackstone")

# lobby doors (south face of the shaft); water can't flow into door blocks
b.door(-1, 1, 1, "north", "birch_door", hinge="left")
b.door(1, 1, 1, "north", "birch_door", hinge="right")
b.sign(-1, 3, 2, ["ELEVATOR", "UP", "to At the Top"], facing="south")
b.sign(1, 3, 2, ["ELEVATOR", "DOWN", "arrivals"], facing="south")
b.set(0, 3, 2, "air")

# deck: shaft walls stop at the floor, both cars open to the deck
for x in range(-2, 3):
    for z in range(-1, 2):
        for y in range(DECK + 1, DECK + 4):
            b.set(x, y, z, "air")
b.sign(-1, DECK + 1, 1, ["ARRIVAL", "step off"], facing="south", wall=False)
b.sign(1, DECK + 1, 1, ["ELEVATOR DOWN", "jump in the", "water"], facing="south", wall=False)
