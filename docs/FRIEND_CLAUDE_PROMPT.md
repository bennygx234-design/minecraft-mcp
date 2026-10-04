# Prompt for your friend's Claude

Send your friend the **whole "Minecraft MCP" folder** (zip it), then have him paste the prompt below into
Claude: Claude Code works best, or a Claude chat where he uploads the folder. It sets his Claude up to
design builds for the shared server.

How it works, in short: the server and its MCP run on Benny's PC, so his Claude can't place blocks directly.
Instead, it writes complete build scripts, checks them offline with the included checker, and he sends the
`.py` file to Benny. Benny's Claude then places it live, in one go, with undo.

---

```
You are helping me build things on a shared Minecraft Java 26.3 server that my friend Benny hosts. I play on it
as AniYiga (I'm an operator). Benny's Claude runs a "minecraft" MCP server on his PC that places whole
structures from Python build scripts in one shot (with undo). My job with you: design builds as build scripts,
check them offline, and hand Benny a finished .py file that his Claude can place with no edits.

The folder "Minecraft MCP" is in my working directory. Read these first:
- README.md                 — what's in the world, teleport coordinates, how things work
- docs/BUILDER_API.md       — every builder command available in a build script (this is the API you write against)
- examples/manor.py, examples/burj_khalifa.py, examples/newark_airport.py — real scripts that were built; copy their style
- docs/NEWARK_BRIEF.md and docs/TRANSIT_MAP.md — coordinate frames and where things are (don't build on top of them)

Rules for every build script you write:
1. Coordinates in a script are LOCAL to an origin (x east, y up, z south; y=0 = walking level, ground at y=-1).
   At the top of the file put a comment block with: build name, the WORLD origin to use (X, Y, Z), the footprint
   in world coordinates, and what it is. Ask me where I want it if I haven't said; pick open land away from the
   existing builds listed in the README (manor x 54..112 z -148..-98, Burj x 124..216 z -181..-89, airport
   x -82..129 z -42..324, highway/light rail between them).
2. Build the whole structure in one script: walls, floors, roofs, windows, doors, lighting, furniture,
   interiors. Use functions for repeated parts and b.at(x, y, z, rot) to place/rotate them. Real block ids for
   Minecraft 26.3 only (e.g. iron_chain, not chain). Keep a single script under ~1 million blocks.
3. Validate before handing it over:  python "Minecraft MCP/mcp/check_build.py" my_build.py
   It must print "OK" (it catches typos and invalid block states and shows size/palette). Python 3.11+ is needed;
   if it isn't installed, tell me how to install it.
4. Hand-off: give me the final .py file plus a 3-line note for Benny: build name, world origin, footprint.
   Benny pastes that into his Claude: "Build <file> at origin X Y Z with the minecraft MCP's build tool".
5. While playing I can test small things myself with in-game commands (I'm an op): /tp, /give, /fill, /setblock,
   /function ewr_planes:spawn (flyable plane), /function ewr_cars:spawn_ferrari (supercar).

Start by reading the README and BUILDER_API, then ask me what I want to build.
```
