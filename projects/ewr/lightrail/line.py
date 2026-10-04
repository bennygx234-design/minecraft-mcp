exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\lightrail\lr_lib.py").read())
for nm in SELECT:
    top_of, path = emit_line(nm)
    pl = pillar_line(nm, top_of, path)
    print(nm, 'deck cells', len(top_of), 'pillars', len(pl), pl)
flush()
