exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\hdr.py").read())
garage("P1", 188, 236, 4, "red_concrete", (196, 220), S=204, core=233,
       bays=[(197, 199), (193, 195), (189, 191), (216, 218), (220, 222), (224, 226), (228, 230), (232, 234)],
       lines=[200, 196, 192, 215, 219, 223, 227, 231, 235], label="P1",
       kinds={(0, 7): ("acc", None), (0, 6): ("acc", None), (1, 0): ("ev", None), (1, 4): ("ev", None)},
       pillars=[192, 219, 227])
report_bays()
dump_bays(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\bays_P1.json")
