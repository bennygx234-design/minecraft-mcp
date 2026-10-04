# Minecraft MCP: how everything works

This folder explains the Minecraft world Claude has been building on Benny's PC, and how to use it.

## The world

A private Minecraft **Java Edition 26.3** server runs on Benny's PC, in creative mode. Here's what's in it:

| Place | What it is | Teleport |
|---|---|---|
| Stone Manor | Walled manor: great hall, library, bedroom, kitchen and guest wings, 4 towers, fountain | `/tp 83 75 -97` (south gate) |
| Burj Khalifa | 248 blocks tall, about 1:3.3 scale, Y-shaped plan, lobby, "At the Top" observation deck, elevator | `/tp 145 69 -122` (lobby) · `/tp 170 221 -132` (deck) |
| Newark Liberty Intl (EWR) | Modelled on the FAA diagram at 1 block = 10 m: runways 4L/22R, 4R/22L and 11/29, plus taxiways | `/tp 40 90 150` (overview) |
| ↳ Terminal A | New 2022 terminal: wavy roof, check-in, security, food halls, gate pier | `/tp -28 73 238` |
| ↳ Terminal B | International terminal: customs, duty-free, 3 gate pods | `/tp -36 73 159` |
| ↳ Terminal C | United hub: curved hall, 3 concourses | `/tp -30 70 110` |
| ↳ Hangars | 3 hangars, the FBO (private aviation) and the ARFF fire station | `/tp 4 64 5` |
| ↳ Cargo | FedEx hub, UPS, fuel farm | `/tp -10 64 278` |
| ↳ Landside | Parking garages, Marriott hotel, rental cars, control tower | `/tp -51 108 160` (tower cab) |
| AirTrain + light rail | Elevated line through the airport, plus the city line to the Manor and the Burj | `/tp 70 92 -78` |
| Highway | Road and bay bridge from the airport to the Manor | `/tp -50 69 -58` (bridge) |
| Supercars | Drivable Ferraris and Lamborghinis, and a dealership with spawn buttons | (dealership near the highway's city end) |
| Flyable planes | Airline-branded jets and private jets you can fly | at the gates, in the hangars and at the FBO |

## Joining the server

- **Benny** (this PC): Multiplayer → **Claude's Build Server** (address `localhost`).
- **Friends:** Multiplayer → Add Server → **`stamina-vega.tun.ply.gg`**. If that fails, add `:51530`.
- **It's private:** only whitelisted players can join (buggati354, AniYiga, pitaishere and DanoobJ). To add someone, have Claude run `whitelist add <name>`, or type `/whitelist add <name>` in the game as an operator.
- **Both players are operators**, so every command works.

## After a restart of this PC

1. Double-click **Start Server.bat**. Wait for "Done", then keep the window open.
2. Double-click **Start Tunnel (friends).bat** so friends can join. Keep that window open too.

Or just ask Claude to "start the Minecraft server and the tunnel".

## Getting around

- **Ride the trains:** at any station, press the button for where you want to go. A tram car carries you along the track. Stops:
  - Terminal A, B and C
  - Hangars, Cargo, Marriott
  - Manor, Burj lobby, and Burj top
- **Fly a plane:** right-click the cockpit (just behind the nose) to board, look to steer, **W** to fly, **Space** to climb, look down to descend, and **Shift** to get off.
  - **Airline jets:** `/function ewr_planes:spawn_<airline>`, where `<airline>` is united, delta, american, jetblue, alaska, spirit, lufthansa, emirates, fedex, ups or ewr.
  - **Sizes:** `/function ewr_planes:spawn/<airline>_regional`, `_narrow` or `_wide`.
  - **Private jets:** `/function ewr_planes:spawn_private`, or `spawn_private_red` / `spawn_private_gold`.
  - **Speed:** `/function ewr_planes:speed/slow`, `cruise`, `fast` or `turbo`.
  - **Remove and help:** `/function ewr_planes:remove_nearest` removes the nearest plane, and `/function ewr_planes:help` lists every command in chat.
  - **Parked flyable jets** (21 of them) are at every gate, in each hangar, at the FBO (private jets), at cargo, and at the runway 04L end.
- **Drive a supercar:** at the dealership, press a "CHOOSE YOUR CAR" button and the car appears in the **Delivery Bay**. Or use `/function ewr_cars:spawn_ferrari` (there are also lambo variants). Right-click to get in, look to steer, **W** to drive, **sneak** to get out.
- **Go fast:**
  - `/effect give @s speed infinite 10 true`
  - `/give @s elytra` and `/give @s firework_rocket 64`
  - hold Ctrl while flying in creative
- **Burj elevator:** in the lobby, the left door goes UP and the deck's water hole goes DOWN.

## Added later

### Money
- Your balance shows on the sidebar.
- **Infinite money:** buggati354, AniYiga, pitaishere and DanoobJ (gold ∞). Everyone else starts with $1,000.
- **Train fares:** $3–$34, priced by distance and shown on each station button.

| Item | Price |
|---|---|
| Ferrari | $250k |
| Lambos | $220k |
| Black Lambo | $300k |
| Rental car (P-A garage) | $150 |
| Flight on an airline | $500 |
| Burj scenic flight | $350 |
| Marriott room key | $200 |

- **Admin commands:**
  - `function ewr_econ:give {player:"name",amount:1000}`
  - `function ewr_econ:add_infinite {player:"name"}`

### Employees
- 101 staff across the terminals, landside, hangars, cargo and city. Right-click one to talk.
- **Who sells things:** check-in agents sell flights and the Burj scenic flight, rental agents rent cars, and the Marriott desk sells room keys.
- **Commands:** `function ewr_staff:spawn_all` brings everyone back; `ewr_staff:remove_all` removes them.

### Automated Burj scenic flights
- An Emirates "EK 2026" leaves gate A10 at Terminal A every 4 minutes, orbits the Burj at y 222 and lands on 22R.
- **To ride:** buy a ticket at a check-in counter. You're sent to the gate and seated automatically.
- **Commands:** `function ewr_flights:depart_now` launches a flight now; `ewr_flights:help` lists the rest.

### Planes
- 26 flyable airline jets, private jets, and B-2s: the hangar B-2 at `/tp 165 64 72`, and the military apron at `/tp 140 76 70`.
- **Speed:**
  - Hold W to throttle up.
  - Top speeds: airliners about 60 blocks/s, B-2 about 68–80 blocks/s. That's the vanilla limit, set by the vehicle "moved too quickly" check.
  - Settings: `function ewr_planes:speed/max`, `turbo`, `fast`, `cruise` or `slow`.

### White House
- Location: x -270..-91, z -236..-81, with a road to the highway.
- **Teleports:**
  - North gate: `/tp -180 80 -226`
  - Oval Office: `/tp -249 72 -146 180 0`
  - South Lawn: `/tp -180 72 -91`
- **Security:** 37 Secret Service agents with rooftop snipers.
  - Without an **Authorized Pass**, you get a warning, then the snipers shoot you (outdoors), or you're arrested into the East Wing holding cell for 60 s.
  - buggati354 has a pass. Give one with `function ewr_whitehouse:give_pass {player:"name"}`.
  - Switch it off with `function ewr_whitehouse:security_off` (`security_on` to turn it back on).

### Parking
- 125 garage spaces sized for the supercars, 36 of them rental spaces in garage P-A (one level per company).
- Curb spaces at Terminals A, B and C, plus dealership spaces.

## Backups
- **World backup** (2026-10-03): `C:\Users\benny\minecraft-mcp-archive\world_backup_2026-10-03.zip`.
- **Agent work:** the full archive (scripts and renders) is at `C:\Users\benny\minecraft-mcp-archive\ewr_full_2026-10-03`. The scripts are also in git under `projects/ewr/`.

## How the building works

Claude doesn't place blocks one at a time. It:

1. Writes a whole structure as a short Python **build script**, using the builder API in `docs/BUILDER_API.md`: rooms, roofs, stairs, furniture, curves and reusable rotated modules.
2. The MCP turns the whole script into **one structure template** and places it with a single command. The 100k-block manor took about 5 seconds.
3. Before placing, it saves what was there, so **every build can be undone**.
4. It **renders** builds as textured pictures to check them, including cutaways of each floor.

Parts of a big project can be split between several Claude agents building at the same time in separate zones. That's how Newark was built: 7 agents worked in parallel, each in its own zone.

| Item | Location |
|---|---|
| MCP code (also in this folder under `mcp/`) | `C:\Users\benny\minecraft-mcp` |
| Server | `C:\Users\benny\minecraft-mcp\server` (world in `server\world`) |
| Datapacks (trains, planes, cars) | `server\world\datapacks\ewr_transit`, `ewr_planes`, `ewr_cars` |
| Claude Code registration | MCP server **`minecraft`**, user scope |
| Backups | The singleplayer copies "Claude's Manor" and "Claude's Manor + Burj Khalifa" in `.minecraft\saves` are old snapshots |

## Folder contents

| Path | What it is |
|---|---|
| `README.md` | This file |
| `FRIEND_CLAUDE_PROMPT.md` | Paste this into your friend's Claude so it can design builds for the server |
| `docs/BUILDER_API.md` | Every builder command a build script can use |
| `docs/NEWARK_BRIEF.md` | The airport's coordinate frame, zones and rules |
| `docs/TRANSIT_MAP.md` | Train stations and routes, in world coordinates |
| `examples/` | Real build scripts: `manor.py`, `burj_khalifa.py`, `burj_elevator.py`, `newark_airport.py`, `newark_kit.py` (plane/jet-bridge helpers) |
| `mcp/` | The MCP itself |
| `mcp/check_build.py` | Offline checker for build scripts: `python check_build.py script.py` |
| `screenshots/` | Pictures of the builds |
| `Start Server.bat`, `Start Tunnel (friends).bat` | Start-up shortcuts |

The `mcp/` folder contains:
- `mcmcp/`: the code (engine, builder, renderer, NBT, RCON)
- `run_server.py`: what Claude Code launches
- `data/`: the 26.3 block catalog
- `tools/`: the client launcher, window capture and screenshot drivers

## Notes

- **Real players are online,** so builds appear live. Ask Claude to undo anything you don't like.
- **The server listens only on this PC.** Friends come in through the playit.gg tunnel, and the remote-control port (RCON) is never exposed.
- **Scale and height limit:** Newark is 1 block = 10 m. The Burj is 1:3.3, the tallest that fits under the y=319 build limit.
