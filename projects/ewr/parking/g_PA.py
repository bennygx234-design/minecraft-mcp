exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\hdr.py").read())
RENTAL = {0: ("Hertz", "yellow"), 1: ("Avis", "red"), 2: ("Enterprise", "green"), 3: ("National", "lime"),
          4: ("Budget", "orange"), 5: ("Alamo", "blue")}
KINDS = {(0, 4): ("acc", None), (1, 4): ("ev", None), (2, 4): ("acc", None), (3, 4): ("acc", None),
         (4, 4): ("ev", None), (5, 4): ("ev", None), (6, 1): ("ev", None), (6, 2): ("ev", None)}
garage("PA", 54, 98, 6, "blue_concrete", (72, 88), S=59, core=95,
       bays=[(71, 73), (75, 77), (79, 81), (83, 85), (87, 89), (91, 93), (95, 97)],
       lines=[70, 74, 78, 82, 86, 90, 94], label="P-A", kinds=KINDS, rental=RENTAL)
# rental level signs at the core door + on the aisle side of the first pillar line
for k, (nm, col) in RENTAL.items():
    x, z = P(94, -128); b.sign(x, 4 * k + 1, z, [nm.upper(), "Rental cars", f"Level {k + 1}", "bays 1-6"], facing="south", wall=False)
report_bays()
dump_bays(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\bays_PA.json")
