# EWR / City transit network — shared route map (WORLD coordinates)

The ride follows these lines. The light-rail track is built under them; the datapack moves riders along them.
All coordinates are world (x, y, z). "Ride level" = the height the rider's FEET travel at.

## Nodes
| id | name | stand point (feet) | notes |
|---|---|---|---|
| A  | AirTrain Terminal A station | (-43.5, 73, 238) | platform on the existing elevated AirTrain deck (deck block y=72) |
| B  | AirTrain Terminal B station | (-43.5, 73, 159) | |
| C  | AirTrain Terminal C station | (-43.5, 73, 126) | |
| MJ | AirTrain junction for the Marriott | (-43.5, 73, 197) | track point, no station |
| S  | AirTrain south end | (-43.5, 73, 270) | track point |
| N  | AirTrain north end | (-43.5, 73, 84) | track point |
| MAR | Marriott / garages stop | (-66, 64, 197) | ground, in front of the Marriott entrance |
| HAN | Hangars stop | (4, 64, 5) | ground, on the apron in front of the three hangars |
| CAR | Cargo stop | (-10, 64, 278) | ground, FedEx apron |
| MAN | Manor stop | (83, 75, -97) | ground, just outside the manor's south gate |
| BUR | Burj Khalifa lobby stop | (145, 69, -122) | the Burj lobby entrance (plaza walkway) |
| TOP | Burj Khalifa observation deck | (170, 221, -132) | destination only (inside the deck); arrive by a final snap |

## Lines (polylines; ride along these in order, either direction)
- AirTrain (existing track, feet y=73): S (-43.5,73,270) — A (-43.5,73,238) — MJ (-43.5,73,197) — B (-43.5,73,159) — C (-43.5,73,126) — N (-43.5,73,84)
- Marriott spur: MJ — (-55,73,197) — (-66,66,197) — MAR (-66,64,197)
- Hangar spur: N — (-43.5,80,40) — (4,74,10) — HAN (4,64,5)
- Cargo spur (REVISED: clears the FedEx warehouse roof, y≈77): S — (-43.5,82,285) — (-10,82,280) — (-10,70,278) — CAR (-10,64,278)
- City light rail (NEW elevated track, ride level y=86): N — (-43.5,86,60) — (-43.5,86,-30) — (20,86,-78) — (83,86,-88) — MAN via (83,78,-95) — MAN (83,75,-97)
- City light rail to the Burj: (83,86,-88) — (130,86,-92) — (145,78,-108) — BUR (145,69,-122)
- Burj top express: BUR — (150,90,-112) — (150,230,-112) — TOP (170,221,-132) (final segment is a snap/teleport into the deck)

Routing between any two stops = shortest path through these lines (they form a tree).
