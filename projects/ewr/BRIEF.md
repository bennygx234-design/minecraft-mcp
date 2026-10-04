# Newark Liberty International (EWR) in Minecraft — builder brief

You are one of several agents building parts of a Minecraft model of Newark airport **at the same time**,
live on a running Minecraft Java 26.3 server that real players are walking around in. Stay strictly inside
your zone so you never collide with another agent.

## What already exists (stage 1, done)
Reclaimed land in a bay, ground surface at world y=63 (walking level y=64). Runways 04L/22R (plan t=0,
s 0..335) and 04R/22L (t=29, s 25..330), crosswind runway 11/29 crossing both near s≈294 diagonally,
taxiways (polished andesite, yellow centre lines) at t=-14 (s 2..300), t=-23 (s 40..290), t=14, with
cross-connectors; a smooth-stone terminal apron at s 50..215, t -72..-26; a north apron s 300..348,
t -100..-12; the loop road at t -122..-116 (s 30..235); the elevated AirTrain on pillars at t -104..-103,
deck at y=8, s 40..226, stations at s 72 (Terminal A), 151 (B), 184 (C) spanning t -107..-100;
NJ Turnpike on the east side (t 50..59). The real airport is rotated so runways run in-game north-south.

## Coordinates
Plan coords: **s** = blocks north of the 04L threshold, **t** = blocks east of the 04L centreline.
1 block = 10 m (buildings may be exaggerated a little in height so they read well).
World position = (60 + t, 64 + y, 310 - s). y = 0 is the walking level; ground blocks are at y = -1.
In-game north (-z) = plan +s. East (+x) = plan +t (toward the runways).

## Tools
Harness (use the project's Python):
```
PY=C:\Users\benny\minecraft-mcp\.venv\Scripts\python.exe
H=C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\run.py
$PY $H dry    <script.py> <name>      # validate: size, palette, typos -> fix before building
$PY $H build  <script.py> <name>      # place it live (one structure placement, undoable). Prints an id.
$PY $H render s1 s2 t1 t2 y1 y2 out.png [view] [cutaway_y]   # isometric PNG; open it with the Read tool
$PY $H scan   s1 s2 t1 t2 y1 y2       # ASCII layers for a small box
$PY $H undo   <id>
```
A build script is Python run with a builder `b` (origin fixed at the plan origin) plus `math`, `rng`.
**Start every script with**
```python
exec(open(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\kit.py").read())
```
Kit (plan-coordinate helpers): `P(s,t)->(x,z)`, `put(s,t,y,block)`, `rect(s1,s2,t1,t2,y,block)`,
`pbox(s1,s2,t1,t2,y1,y2,block,hollow=False)`, `at(s,t,y,rot)` (child view; its local -z = plan +s, rot =
quarter turns clockwise, so rot=1 makes local -z point to plan +t / the runways), `plane(view, livery,
big=False)` (airliner, nose to the view's local -z; liveries: united, delta, american, jetblue, alaska,
spirit, fedex, ups, lufthansa, emirates), `jet_bridge(s,t,length,'+t'|'-t'|'+s'|'-s', y=4)`.

Full builder API on `b` (builder x = t, z = -s): `b.set/box/clear/room/walls/floor/frame/line/
sphere/ellipsoid/dome/cylinder/pyramid/replace/door/double_door/window/ladder/stairs_run/gable_roof/hip_roof/
flat_roof/bed/chair/table/long_table/sofa/bookshelves/lamp/wall_torch/chest/barrel/kitchen/carpet/plant/sign/
summon/command`, and `b.at(x,y,z,rot)`. Signatures:
- `b.box(x1,y1,z1,x2,y2,z2, block, hollow=False)`, `b.room(x1,y1,z1,x2,y2,z2, wall, floor=None, ceiling=None)`
- `b.cylinder(cx,y,cz,r,height,block,hollow=False)`, `b.door(x,y,z,facing,'oak_door',hinge)` (facing = way you walk in)
- `b.chair(x,y,z,facing)` (facing = where the sitter looks), `b.lamp(x,y,z,'lantern',hanging=False)`
- `b.sign(x,y,z,['l1','l2'],facing='south',wall=True)`, `b.stairs_run(x,y,z,direction,length,block,width,support)`
Blocks: Minecraft ids like `white_concrete`, `light_gray_stained_glass`, `oak_stairs[facing=east]`; a dict
gives a weighted random mix. Invalid ids fail fast with suggestions. 26.x names: `iron_chain` (not chain).
Directions in block states are builder-local (north = -z = plan +s).

## Rules
1. Only place blocks inside your zone's plan box (any y from -1 to +60). You may repaint ground (y=-1)
   inside your zone. Never touch anything outside it, never change runways/taxiways outside your box.
2. Do not run raw server commands (no /time, /weather, /tp, /kill). Real players are online.
3. Keep each build under ~1.2M planned blocks; split big work into several builds.
4. Work loop: dry run -> build -> render your zone (open the PNG with Read and actually look at it) ->
   fix with another build or `undo` + rebuild. Do at most 3 fix rounds. Use cutaway renders to check
   interiors.
5. Model the REAL Newark building you were given (shape, layout, scale) as faithfully as the grid allows,
   and furnish interiors (check-in counters, security lanes, gate seating, shops/food, baggage claim,
   lights), so players can walk through. Use glass generously, white/light-gray modern materials.
6. Put your scripts in `C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\<your-zone>\`. Don't edit anything in
   C:\Users\benny\minecraft-mcp and don't touch server settings.
7. Final report (short): what you built and how it maps to the real airport, build ids, 2-3 world
   coordinates worth teleporting to (`/tp x y z`), script and render paths, anything unfinished.
