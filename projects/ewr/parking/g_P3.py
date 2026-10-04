exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\hdr.py").read())
garage("P3", 154, 184, 5, "orange_concrete", (166,), S=172, core=155,
       bays=[(165, 167), (161, 163), (157, 159)], lines=[168, 164, 160, 156], label="P3",
       kinds={(0, 2): ("acc", None), (1, 1): ("ev", None), (5, 1): ("ev", None)}, pillars=[160])
report_bays()
dump_bays(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\bays_P3.json")
