exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\hdr.py").read())
garage("P4", 128, 150, 4, "green_concrete", (140,), S=132, core=147, bays=[], lines=[], label="P4",
       kinds={(0, 2): ("acc", None), (1, 1): ("ev", None), (4, 1): ("ev", None)},
       north_row=(143, 149, [(-141, -139), (-137, -135), (-133, -131)]), zone=3)
report_bays()
dump_bays(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\bays_P4.json")
