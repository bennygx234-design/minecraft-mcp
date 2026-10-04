"""Build (or dry-run) the station panels.  python build.py dry|build [STOP ...]
A/B/C go through the job harness (run.py, plan origin); city stops use S.build at the stand origin."""
import json, math, os, subprocess, sys
sys.path.insert(0, r'C:\Users\benny\minecraft-mcp')
os.environ["MCMCP_KEEP_FORCELOAD"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen
PY = r'C:\Users\benny\minecraft-mcp\.venv\Scripts\python.exe'
RUN = r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\run.py'
mode = sys.argv[1]
stops = sys.argv[2:] or gen.STOPS
ids = {}
for a in stops:
    script = os.path.join(HERE, 'panels', f'panel_{a}.py')
    if a in ('A', 'B', 'C'):
        r = subprocess.run([PY, RUN, mode, script, f'transit_panel_{a}'], capture_output=True, text=True)
        print(a, r.stdout.strip()[:600], r.stderr.strip()[-600:])
    else:
        from mcmcp import server as S
        sx, sy, sz = gen.NODES[a]
        o = (math.floor(sx), int(sy), math.floor(sz))
        r = S.build(open(script, encoding='utf-8').read(), *o, name=f'transit_panel_{a}', dry_run=(mode == 'dry'), seed=7)
        try:
            d = json.loads(r); print(a, {k: d.get(k) for k in ('id', 'blocks', 'blocks_changed', 'min', 'max', 'post_errors')})
        except Exception:
            print(a, r[:800])
