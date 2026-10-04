exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\plib.py").read())
# Terminal curb parking: parallel 3x7 bays on the strip between the AirTrain pillars (t -104) and the
# terminals' curb lanes / facades. Short-term = white lines, PICK-UP = yellow lines, accessible = blue.
SIGN = {"pickup": ["PICK-UP", "15 min max", "", ""], "short": ["SHORT-TERM", "parking", "1 hour", ""],
        "acc": ["ACCESSIBLE", "parking", "permit only", ""]}


def curb(name, t1, bays, sign_t):
    t2 = t1 + 2
    for (sa, kind) in bays:
        sb = sa + 6
        rect(sa, sb, t1, t2, -1, "gray_concrete")
        lc = "yellow_concrete" if kind == "pickup" else LINE
        pline(sa - 1, sa - 1, t1, t2, 0, lc); pline(sb + 1, sb + 1, t1, t2, 0, lc)
        bay(sa, sb, t1, t2, 0, "+s", kind="acc" if kind == "acc" else "std", stop=False, tag=f"{name} {kind}")
        x, z = P(sa + 2, sign_t)
        b.sign(x, 0, z, [SIGN[kind][0], SIGN[kind][1], SIGN[kind][2], f"Terminal {name}"], facing="east", wall=False)


curb("A", -102, [(48, "pickup"), (56, "pickup"), (75, "acc"), (83, "short"), (91, "short"), (99, "short")], -103)
curb("B", -102, [(121, "acc"), (129, "pickup"), (137, "pickup"), (154, "short"), (162, "short")], -103)
curb("C", -103, [(187, "short"), (195, "acc"), (203, "pickup"), (211, "pickup"), (219, "short"), (227, "short")], -104)
report_bays()
dump_bays(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\parking\bays_curbs.json")
