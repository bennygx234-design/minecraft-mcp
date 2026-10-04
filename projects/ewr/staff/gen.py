"""EWR staff: generates the ewr_staff datapack (employees = mannequin + interaction entity).

    python gen.py            # write the datapack from survey_*.json (+ extra.json)
Then (RCON):  reload ; function ewr_staff:spawn_all

Interface used:  function ewr_econ:try_buy {price, item, then}   (as + at the buyer)
Click flow:  interaction entity (tag ewrs_hit, CustomName = employee id) -> tick polls the ones within 6 blocks
of a player for `interaction` data -> ewr_staff:hit -> `execute on target` (the clicking player) ->
ewr_staff:npc/<id> (greeting + menu).  Menu buttons use `/trigger ewrs_buy set N` (works for non-ops); the
dispatcher only honours a purchase while the right employee is within 10 blocks.
"""
import hashlib
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DP = r"C:\Users\benny\minecraft-mcp\server\world\datapacks\ewr_staff"
NS = "ewr_staff"

# ----------------------------------------------------------------------------------------- inputs
STAFF = []
CAR_SPOTS = []
MARRIOTT_FLOORS = (2, 9)
for fn in sorted(os.listdir(HERE)):
    if not (fn.startswith("survey_") and fn.endswith(".json")):
        continue
    d = json.load(open(os.path.join(HERE, fn), encoding="utf-8"))
    if isinstance(d, dict):
        STAFF += d.get("staff", [])
        CAR_SPOTS += d.get("car_spots", [])
        if d.get("marriott"):
            MARRIOTT_FLOORS = (2, int(d["marriott"].get("total_storeys", 9)))
    else:
        STAFF += d
if os.path.exists(os.path.join(HERE, "overrides.json")):
    ov = json.load(open(os.path.join(HERE, "overrides.json"), encoding="utf-8"))
    drop = set(ov.get("drop", []))
    STAFF = [p for p in STAFF if p["id"] not in drop]
    for p in STAFF:
        p.update(ov.get("patch", {}).get(p["id"], {}))
    STAFF += ov.get("add", [])
    if ov.get("car_spots"):
        CAR_SPOTS = ov["car_spots"]
    if ov.get("marriott_floors"):
        MARRIOTT_FLOORS = tuple(ov["marriott_floors"])

seen = set()
for p in STAFF:
    p["id"] = "".join(c if c.isalnum() or c == "_" else "_" for c in p["id"].lower())
    while p["id"] in seen:
        p["id"] += "x"
    seen.add(p["id"])
    p["airline"] = (p.get("airline") or None)
    p["brand"] = (p.get("brand") or None)


def h(s, n):
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % n


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ----------------------------------------------------------------------------------------- tables
AIRLINES = {  # id: (display, chest, legs, hat or None, name colour, home terminal for plane stands, size)
    "united": ("United", 0x1B2A5C, 0x1B2A5C, None, "blue", "C", "narrow"),
    "delta": ("Delta", 0xA6192E, 0x0B1F41, None, "red", "A", "narrow"),
    "american": ("American", 0x36495A, 0x6E7B85, None, "gray", "A", "narrow"),
    "jetblue": ("JetBlue", 0x003876, 0x1C1C3C, None, "dark_blue", "A", "narrow"),
    "alaska": ("Alaska", 0x01426A, 0x0B2341, None, "dark_aqua", "A", "narrow"),
    "spirit": ("Spirit", 0xFFE600, 0x1A1A1A, None, "yellow", "A", "narrow"),
    "lufthansa": ("Lufthansa", 0x05164D, 0x05164D, 0x05164D, "dark_blue", "B", "narrow"),
    "emirates": ("Emirates", 0xC8B48A, 0xC8B48A, 0xC60C30, "dark_red", "B", "wide"),
    "fedex": ("FedEx", 0x4D148C, 0x1A1A1A, None, "dark_purple", "B", "narrow"),
    "ups": ("UPS", 0x351C15, 0x351C15, None, "gold", "B", "narrow"),
    "ewr": ("EWR Air", 0x2F6FA8, 0x1A1A1A, None, "aqua", "B", "narrow"),
    "swiss": ("SWISS", 0x1A1A1A, 0x1A1A1A, None, "red", "B", "narrow", "ewr"),
    "austrian": ("Austrian", 0xD81E05, 0x1A1A1A, 0xD81E05, "red", "B", "narrow", "ewr"),
    "sas": ("SAS", 0x000F4B, 0x000F4B, None, "dark_blue", "B", "narrow", "ewr"),
    "airindia": ("Air India", 0x8C1D40, 0x8C1D40, None, "dark_red", "B", "wide", "ewr"),
    "tap": ("TAP Air Portugal", 0x1C6B3C, 0x1A1A1A, None, "dark_green", "B", "narrow", "ewr"),
    "elal": ("El Al", 0x0E2A5C, 0x0E2A5C, None, "blue", "B", "narrow", "ewr"),
    "aircanada": ("Air Canada", 0x1A1A1A, 0x1A1A1A, None, "red", "B", "narrow", "ewr"),
}
ALIAS = {"swiss": "swiss", "austrian": "austrian", "sas": "sas", "air india": "airindia", "tap": "tap",
         "el al": "elal", "air canada": "aircanada", "united": "united", "delta": "delta", "american": "american",
         "jetblue": "jetblue", "alaska": "alaska", "spirit": "spirit", "lufthansa": "lufthansa", "emirates": "emirates"}
for p in STAFF:
    if not p["airline"] and p["role"] in ("checkin", "gate", "pilot", "attendant"):
        lab = p.get("label", "").lower()
        for k, v in ALIAS.items():
            if lab.startswith(k):
                p["airline"] = v
                break


def livery(a):
    al = AIRLINES[a]
    return al[7] if len(al) > 7 else a
BRANDS = {  # rental brand colours (chest, name colour)
    "hertz": (0xFFD100, "yellow"), "avis": (0xD4002A, "red"), "enterprise": (0x169A5A, "dark_green"),
    "national": (0x0E6B3A, "green"), "budget": (0xF26B21, "gold"), "alamo": (0x1E4C9A, "blue"),
    "sixt": (0xFF5F00, "gold"), "dollar": (0xC8102E, "red"), "thrifty": (0x0072CE, "aqua"),
}
SKINS = ["alex", "ari", "efe", "kai", "makena", "noor", "steve", "sunny", "zuri"]
NAMES = ["Maria", "James", "Aisha", "Carlos", "Priya", "Daniel", "Grace", "Omar", "Sofia", "Kevin", "Lena",
         "Marcus", "Yuki", "Andre", "Fatima", "Tom", "Elena", "Raj", "Chloe", "Victor", "Nina", "Samuel",
         "Ines", "Darnell", "Mei", "Patrick", "Zara", "Luis", "Hannah", "Kwame", "Rosa", "Ethan", "Leila",
         "Mateo", "Olivia", "Dev", "Isabel", "Jamal", "Anna", "Hiro", "Gabriela", "Noah", "Amara", "Tony",
         "Claire", "Ravi", "Bianca", "Frank", "Selin", "Malik", "Joy", "Oscar", "Tara", "Felix", "Ngozi",
         "Diego", "Ruth", "Sean", "Lucia", "Ben", "Kiara", "Paolo", "Esther", "Ivan", "Nadia", "Rocco",
         "Simone", "Wei", "Deborah", "Hugo", "Layla", "Max", "Erin", "Tariq", "Vera", "Jorge", "Alice",
         "Kofi", "Dana", "Luca", "Imani", "Pete", "Sara", "Arjun", "Monica", "Eli", "Rhea", "Gus", "Mila",
         "Reggie", "Ada", "Nico", "Pam", "Ken", "Lola", "Sanjay", "Iris", "Bruno"]

# role: (title, chest, legs, boots, hat, mainhand, offhand, name colour)
ROLE = {
    "checkin": ("Check-in", None, None, 0x1A1A1A, None, "paper", None, None),
    "gate": ("Gate Agent", None, None, 0x1A1A1A, None, "paper", None, None),
    "attendant": ("Flight Attendant", None, None, 0x1A1A1A, None, None, None, None),
    "pilot": ("Captain", 0xF2F2F2, 0x101820, 0x101820, 0x101820, None, None, "white"),
    "tsa": ("TSA Officer", 0x2E4A7D, 0x1C1C1C, 0x111111, None, "book", None, "dark_blue"),
    "cbp": ("CBP Officer", 0x1F3A2E, 0x1F3A2E, 0x111111, 0x1F3A2E, "writable_book", None, "dark_green"),
    "shop": ("Shop Assistant", 0x2B2B2B, 0x3A3A3A, 0x1A1A1A, None, "book", None, "light_purple"),
    "food": ("Server", 0xF2F2F2, 0x2B2B2B, 0x1A1A1A, 0xF2F2F2, "bread", None, "gold"),
    "baggage": ("Baggage Services", 0xE5E500, 0x2B3A55, 0x1A1A1A, None, "name_tag", None, "yellow"),
    "info": ("Information", 0x0B5394, 0x1C1C1C, 0x1A1A1A, None, "map", None, "aqua"),
    "rental": ("Rental Agent", None, 0x1A1A1A, 0x1A1A1A, None, "tripwire_hook", None, None),
    "reception": ("Marriott Front Desk", 0x2B2B2B, 0x1A1A1A, 0x111111, None, "book", None, "dark_red"),
    "bellhop": ("Bellhop", 0x8B1A1A, 0x1A1A1A, 0x111111, 0x8B1A1A, None, None, "red"),
    "bartender": ("Bartender", 0xF2F2F2, 0x111111, 0x111111, None, "honey_bottle", None, "gold"),
    "garage": ("Parking Attendant", 0xFF7F00, 0x2B3A55, 0x1A1A1A, None, "paper", None, "gold"),
    "atc": ("Air Traffic Control", 0xDCE6F0, 0x4A4A4A, 0x2B2B2B, None, "spyglass", None, "aqua"),
    "mechanic": ("Aircraft Mechanic", 0x3A5BA0, 0x3A5BA0, 0x2B2B2B, None, "iron_pickaxe", None, "blue"),
    "firefighter": ("ARFF Firefighter", 0xC9A227, 0xC9A227, 0x1A1A1A, 0xB02E26, "water_bucket", None, "red"),
    "concierge": ("Concierge", 0x1B1B1B, 0x1B1B1B, 0x111111, None, "book", None, "gold"),
    "cargo": ("Cargo Handler", 0x4D148C, 0x1A1A1A, 0x1A1A1A, None, "chest", None, "dark_purple"),
    "ramp": ("Ramp Agent", 0xC6FF00, 0x2B3A55, 0x1A1A1A, 0xF2F2F2, "end_rod", "end_rod", "green"),
    "sales": ("Sales Consultant", 0x1A1A1A, 0x1A1A1A, 0x111111, None, "paper", None, "red"),
    "train": ("AirTrain Attendant", 0x1D4F91, 0x14284B, 0x111111, 0x1D4F91, "paper", None, "aqua"),
    "butler": ("Butler", 0x111111, 0x111111, 0x111111, None, None, None, "dark_gray"),
    "guard": ("Manor Guard", None, None, None, None, "iron_sword", "shield", "gray"),
    "deck": ("Observation Deck", 0x1B2A5C, 0x1B1B1B, 0x111111, None, "spyglass", None, "aqua"),
}
for k in ("concierge",):
    pass

# greetings: role -> list of lines ({place} = label, {airline} = airline name, {brand})
LINES = {
    "checkin": ["Welcome to {airline}! Passport or ID, please. Any bags to check today?",
                "Good to see you! Window or aisle? I'll get you on the next {airline} departure.",
                "Hi there! {airline} check-in is open. Do you have your confirmation number?"],
    "gate": ["Boarding begins shortly at {place}. Have your boarding pass ready!",
             "Welcome to {place}! We're on time today. Group 1 boards first.",
             "This is {place}. Please keep your boarding pass and ID handy."],
    "attendant": ["Hi! We'll be boarding soon. Can't wait to have you on board.",
                  "Welcome! Remember: seatbelts fastened whenever the sign is on.",
                  "Hello! Just heading to the aircraft. Have a lovely flight!"],
    "pilot": ["Good day! Clear skies over Newark today. Should be a smooth ride.",
              "Hello! Just finishing the flight plan. Runway 22R is in use today.",
              "Hi there! Want a tip? Space to climb, look down to descend."],
    "tsa": ["Boarding pass and ID, please. Laptops and liquids out of your bag.",
            "Next! Please step through the walk-through when the light is green.",
            "Shoes, belts and jackets in the bin, please. Thanks for your patience."],
    "cbp": ["Welcome to the United States. Passport and customs form, please.",
            "Purpose of your visit? Business or pleasure?",
            "Anything to declare? Fruits, plants, more than $10,000 in cash?"],
    "shop": ["Hi! Magazines, snacks, neck pillows... let me know if you need anything.",
             "Welcome in! Duty-free deals all day for international travellers.",
             "Hello! The bestsellers are on the left. Have a great trip!"],
    "food": ["Hi! What can I get started for you?",
             "Welcome! Fresh out of the oven, everything on the board is available.",
             "Hey there! Grab a seat, I'll bring it right over."],
    "baggage": ["Welcome to Newark! Your bags will be on this carousel shortly.",
                "Lost luggage? I can file a report for you right here.",
                "Hi! Oversize items come out at the end of the belt."],
    "info": ["Welcome to Newark Liberty! The AirTrain is upstairs; it links all terminals.",
             "Hi! Need directions? Terminals A, B and C are on the AirTrain, plus the Marriott and rental cars.",
             "Hello! Rental cars and the Marriott are on the landside. The AirTrain gets you there."],
    "rental": ["Welcome to {brand}! Looking for something fast?",
               "Hi! {brand} has supercars on the lot today. Pick one below.",
               "Welcome! Driver's licence ready? Choose your car and I'll bring it around."],
    "reception": ["Welcome to the Newark Airport Marriott! Checking in?",
                  "Good evening and welcome! A room for tonight?",
                  "Hello! Breakfast is served from 6 to 10 in the lobby."],
    "bellhop": ["Welcome to the Marriott! May I take your bags?",
                "Good day! The elevators are just past the front desk.",
                "Hello! Need a hand with your luggage?"],
    "bartender": ["Welcome to the lobby bar! What are you having?",
                  "Evening! Our signature drink is the Liberty Spritz.",
                  "Hi! Long layover? Pull up a stool."],
    "garage": ["Welcome to EWR parking! Take a ticket, park anywhere marked.",
               "Hi! The garage is open. Pay at the machine before you leave.",
               "Hello! Daily, economy and short-term parking all through here."],
    "atc": ["Newark Tower. Traffic is busy; runways 4L and 4R in use.",
            "Hi! Just keeping the jets apart. Watch your altitude out there!",
            "Tower here. Wind 220 at 12, altimeter 30.01. Cleared to look around!"],
    "mechanic": ["Hey! Doing a routine check on this bird. Mind the tools.",
                 "Hi there! Engine inspection today. She'll be flying again tomorrow.",
                 "Hello! Every jet gets checked here before it flies."],
    "firefighter": ["ARFF Station! We can reach any runway in under three minutes.",
                    "Hi! Just checked the trucks. Foam tanks are full.",
                    "Hello! Safety first on the airfield."],
    "concierge": ["Welcome! How may I help you today?",
                  "Good day! It's a pleasure to have you with us.",
                  "Hello! Can I arrange anything for your visit?"],
    "cargo": ["Hi! Sorting tonight's packages. This hub never sleeps.",
              "Hey! Overnight freight is loading now.",
              "Hello! Every box here is on a plane within hours."],
    "ramp": ["Hi! Stay behind the yellow line, engines can start any minute.",
             "Hey there! I'm marshalling the next arrival in.",
             "Hello! Ear protection on the apron, please."],
    "sales": ["Welcome to the showroom! Every car here is for sale.",
              "Hi! Looking for something with a little more horsepower?",
              "Hello! Take a look around; the buttons on the panel bring the car to the Delivery Bay."],
    "train": ["Welcome to the AirTrain! Fares are by distance.",
              "Hi! Pick your stop on the board and the tram will take you there.",
              "Hello! The AirTrain links Terminals A, B, C, the Marriott, the hangars, cargo and the city."],
    "butler": ["Good day. Welcome to the Stone Manor. May I take your coat?",
               "Welcome. The great hall is through here; the library is upstairs.",
               "Good evening. Tea will be served in the great hall shortly."],
    "guard": ["Halt! Oh, a visitor. Welcome to the Stone Manor.",
              "The manor is open to guests. Please mind the fountain.",
              "All quiet at the gate. Go on through."],
    "deck": ["Welcome to At the Top! You're nearly 2,000 feet up (in Minecraft blocks).",
             "Hi! The best view of the airport is to the south-west.",
             "Welcome to the observation deck! Take the water hole to go back down."],
}
LINES["concierge_burj"] = ["Welcome to the Burj Khalifa! The left elevator door takes you to the top.",
                           "Good day! The observation deck is open. Use the left door to go up.",
                           "Welcome! The deck is at the very top. Enjoy the view."]
LINES["concierge_fbo"] = ["Welcome to the FBO! Your private jet is on the ramp.",
                          "Good day! Coffee and fresh cookies in the lounge while we fuel your jet.",
                          "Welcome! The private jets are just outside. Right-click the cockpit to board."]

# role-specific extra info line (string or None)
def info_line(p):
    r = p["role"]
    if r == "sales":
        return ("Prices: Ferrari $250,000 · Lamborghini $220,000 · Black Lamborghini $300,000. "
                "Press a CHOOSE YOUR CAR button on the panel; your car appears in the Delivery Bay. "
                + (p.get("note_buttons") or ""))
    if r == "train":
        return "Fares are by distance. Press the button on the board for your stop, then wait on the platform."
    if r == "info":
        return "AirTrain stops: Terminal A, B, C, Marriott, Hangars, Cargo, Manor, Burj lobby and Burj top."
    return None


# ----------------------------------------------------------------------------------------- planes
# flyable-plane stands on the taxiway east of the terminals (x 48.5, nose north); all verified clear
STANDS = [  # (slot, x, z, terminal, description)
    (1, 48.5, 240.5, "A", "the taxiway east of Terminal A"),
    (2, 48.5, 214.5, "A", "the taxiway east of Terminal A"),
    (3, 48.5, 178.5, "B", "the taxiway east of Terminal B"),
    (4, 48.5, 152.5, "B", "the taxiway east of Terminal B"),
    (5, 48.5, 122.5, "C", "the taxiway east of Terminal C"),
    (6, 48.5, 96.5, "C", "the taxiway east of Terminal C"),
    (7, 48.5, 268.5, "A", "the taxiway south of Terminal A"),
    (8, 48.5, 68.5, "C", "the taxiway north of Terminal C"),
]
BRAND_LEVEL = {"hertz": 1, "avis": 2, "enterprise": 3, "national": 4, "budget": 5, "alamo": 6}
FLIGHT_PRICE = 500
SCENIC_PRICE = 350
SCENIC = os.path.exists(r"C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\flights\BOOK_READY.txt")
RENT_PRICE = 150
ROOM_PRICE = 200
CARS = [  # trigger value, place function, label
    (1, "ferrari", "Ferrari"), (2, "lambo_yellow", "Yellow Lamborghini"), (3, "lambo_orange", "Orange Lamborghini"),
    (4, "lambo_green", "Green Lamborghini"), (5, "lambo_black", "Black Lamborghini")]

# ----------------------------------------------------------------------------------------- build
F = {}


def txt(text, color="white", **kw):
    d = {"text": text, "color": color}
    d.update(kw)
    return d


def snbt(o):
    """JSON-ish -> SNBT text component (keys unquoted)."""
    if isinstance(o, dict):
        return "{" + ",".join(f"{k if k.replace('_', '').isalnum() else chr(34) + k + chr(34)}:{snbt(v)}" for k, v in o.items()) + "}"
    if isinstance(o, list):
        return "[" + ",".join(snbt(v) for v in o) + "]"
    if isinstance(o, bool):
        return "1b" if o else "0b"
    if isinstance(o, (int, float)):
        return str(o)
    return '"' + esc(str(o)) + '"'


def button(label, trig, hover, color="green"):
    return {"text": f"[{label}]", "color": color, "bold": True,
            "click_event": {"action": "run_command", "command": f"/trigger ewrs_buy set {trig}"},
            "hover_event": {"action": "show_text", "value": hover}}


def leather(item, color):
    return {"id": f"minecraft:leather_{item}", "count": 1,
            "components": {"minecraft:dyed_color": color}}


def outfit(p):
    r = p["role"]
    title, chest, legs, boots, hat, main, off, ncol = ROLE[r]
    al = AIRLINES.get(p["airline"]) if p["airline"] else None
    if r in ("checkin", "gate", "attendant") and al:
        chest, legs = al[1], al[2]
        hat = al[3] if r in ("gate", "attendant") or h(p["id"], 2) else hat
        ncol = al[4]
    elif r in ("checkin", "gate", "attendant"):
        chest, legs, ncol = 0x2F6FA8, 0x1A1A1A, "aqua"
    if r == "pilot" and al:
        ncol = al[4]
    if r == "rental":
        bc = BRANDS.get((p["brand"] or "").lower().split()[0] if p["brand"] else "", (0x2F6FA8, "aqua"))
        chest, ncol = bc
    if r == "cargo" and "ups" in (p.get("label", "") + p["id"]).lower():
        chest, legs, ncol = 0x351C15, 0x351C15, "gold"
    eq = {}
    if r == "guard":
        eq = {"head": {"id": "minecraft:iron_helmet", "count": 1}, "chest": {"id": "minecraft:iron_chestplate", "count": 1},
              "legs": {"id": "minecraft:iron_leggings", "count": 1}, "feet": {"id": "minecraft:iron_boots", "count": 1}}
    else:
        if chest is not None:
            eq["chest"] = leather("chestplate", chest)
        if legs is not None:
            eq["legs"] = leather("leggings", legs)
        if boots is not None:
            eq["feet"] = leather("boots", boots)
        if hat is not None:
            eq["head"] = leather("helmet", hat)
    if main:
        eq["mainhand"] = {"id": f"minecraft:{main}", "count": 1}
    if off:
        eq["offhand"] = {"id": f"minecraft:{off}", "count": 1}
    return title, eq, ncol or "white"


def role_title(p):
    r = p["role"]
    al = AIRLINES.get(p["airline"]) if p["airline"] else None
    if r == "checkin":
        return f"{al[0] if al else 'Airline'} Check-in"
    if r == "gate":
        return f"{p.get('label', 'Gate')}"
    if r in ("attendant", "pilot") and al:
        return f"{al[0]} {ROLE[r][0]}"
    if r == "rental":
        return f"{p['brand'] or 'Rental'} Rentals"
    if r in ("food", "shop", "baggage", "mechanic", "firefighter", "cargo", "ramp", "garage", "concierge"):
        return p.get("label") or ROLE[r][0]
    return ROLE[r][0]


def greet_key(p):
    if p["role"] == "concierge":
        lab = (p.get("label", "") + p["id"]).lower()
        if "burj" in lab:
            return "concierge_burj"
        if "fbo" in lab:
            return "concierge_fbo"
    return p["role"]


used_names = {}
for i, p in enumerate(STAFF):
    k0 = (h(p["id"], len(NAMES)) + i * 7) % len(NAMES)
    nm = NAMES[k0]
    for k in range(len(NAMES)):
        if NAMES[(k0 + k) % len(NAMES)] not in used_names:
            nm = NAMES[(k0 + k) % len(NAMES)]
            break
    else:
        nm = nm + " " + "ABCDEFGHJKLMNPRSTW"[i % 18] + "."
    used_names[nm] = p["id"]
    if p["role"] == "pilot":
        nm = "Capt. " + nm
    p["name"] = nm
    p["skin"] = SKINS[(h(p["id"] + "s", 9) + i) % 9]
    p["model"] = "slim" if h(p["id"] + "m", 2) else "wide"
    p["title"] = role_title(p)
    p["eq"], p["ncol"] = outfit(p)[1:]

# --- spawn / remove
spawn = ["# summon every employee (kills existing ones first)", f"function {NS}:remove_all"]
for p in STAFF:
    x, y, z = p["x"] + 0.5, p["y"], p["z"] + 0.5
    yaw = p["yaw"]
    tags = ["ewr_staff", "ewrs_npc", f"ewrs_r_{p['role']}", f"ewrs_m_{p['id']}"]
    if p["airline"]:
        tags.append(f"ewrs_air_{p['airline']}")
    m = {"Tags": tags, "CustomName": {"text": p["name"], "color": p["ncol"]}, "CustomNameVisible": True,
         "description": {"text": p["title"], "color": "gray"},
         "profile": {"texture": f"entity/player/{p['model']}/{p['skin']}", "model": p["model"]},
         "Rotation": [float(yaw), 0.0], "NoGravity": True, "immovable": True, "Invulnerable": True,
         "PersistenceRequired": True, "Silent": True, "equipment": p["eq"],
         "drop_chances": {k: 0.0 for k in p["eq"]}}
    ms = snbt(m).replace(f"Rotation:[{float(yaw)},0.0]", f"Rotation:[{float(yaw)}f,0.0f]")
    ms = ms.replace("drop_chances:{" + ",".join(f"{k}:0.0" for k in p["eq"]) + "}",
                    "drop_chances:{" + ",".join(f"{k}:0.0f" for k in p["eq"]) + "}")
    spawn.append(f"summon minecraft:mannequin {x} {y} {z} {ms}")
    spawn.append(f'summon minecraft:interaction {x} {y} {z} {{Tags:["ewr_staff","ewrs_hit"],CustomName:"{p["id"]}",'
                 f'width:0.8f,height:1.95f,response:1b}}')
    spawn.append(f"scoreboard players set @e[type=mannequin,tag=ewrs_m_{p['id']},limit=1] ewrs_yaw {int(yaw)}")
spawn.append(f'tellraw @a[tag=ewrs_dev] {{text:"[ewr_staff] {len(STAFF)} employees on duty",color:"gray"}}')
F["spawn_all"] = spawn
F["remove_all"] = ["kill @e[tag=ewr_staff]"]

# --- load / tick
F["load"] = [
    "scoreboard objectives add ewrs_buy trigger",
    "scoreboard objectives add ewrs_t dummy",
    "scoreboard objectives add ewrs_tmp dummy",
    "scoreboard objectives add ewrs_yaw dummy",
    "scoreboard objectives add ewrs_cd dummy",
    "scoreboard objectives add ewrs_pl dummy",
    "scoreboard objectives add ewrs_lv dummy",
]
F["tick"] = [
    "# clicks: only interaction boxes within 6 blocks of a player are checked",
    f"execute as @a[gamemode=!spectator] at @s as @e[type=interaction,tag=ewrs_hit,distance=..6] if data entity @s interaction run function {NS}:hit",
    f"execute as @a[scores={{ewrs_buy=1..}}] at @s run function {NS}:buy/dispatch",
    "scoreboard players remove @a[scores={ewrs_cd=1..}] ewrs_cd 1",
    "scoreboard players add #t ewrs_t 1",
    f"execute if score #t ewrs_t matches 10.. run function {NS}:look_tick",
]
F["look_tick"] = [
    "scoreboard players set #t ewrs_t 0",
    f"execute as @a[gamemode=!spectator] at @s as @e[type=mannequin,tag=ewrs_npc,distance=..6] run tag @s add ewrs_near",
    f"execute as @e[type=mannequin,tag=ewrs_near] at @s run function {NS}:look",
    f"execute as @e[type=mannequin,tag=ewrs_turned,tag=!ewrs_near] at @s unless entity @a[gamemode=!spectator,distance=..7] run function {NS}:unlook",
    "tag @e[type=mannequin,tag=ewrs_near] remove ewrs_near",
]
F["look"] = ["tp @s ~ ~ ~ facing entity @p[gamemode=!spectator] eyes", "tag @s add ewrs_turned"]
F["unlook"] = ["tag @s remove ewrs_turned",
               "execute store result storage ewr_staff:t yaw float 1 run scoreboard players get @s ewrs_yaw",
               f"function {NS}:unlook_m with storage ewr_staff:t"]
F["unlook_m"] = ["$tp @s ~ ~ ~ $(yaw) 0"]
F["hit"] = [
    "# as the clicked interaction entity: run its employee's handler as the clicking player, then clear",
    f"execute at @s as @e[type=mannequin,tag=ewrs_npc,distance=..0.3,limit=1] at @s run tp @s ~ ~ ~ facing entity @p[gamemode=!spectator] eyes",
    f"execute at @s as @e[type=mannequin,tag=ewrs_npc,distance=..0.3,limit=1] run tag @s add ewrs_turned",
    f"function {NS}:route with entity @s",
    "data remove entity @s interaction",
    "data remove entity @s attack",
]
F["route"] = [f"$execute on target if entity @s[type=player,scores={{ewrs_cd=..0}}] at @s run function {NS}:npc/$(CustomName)",
              f"$execute on target if entity @s[type=player] unless score @s ewrs_cd matches -2147483648.. at @s run function {NS}:npc/$(CustomName)"]

# --- per-employee handlers
def say_line(p, line):
    return (f'tellraw @s [{snbt(txt("[" + p["name"] + " · " + p["title"] + "] ", p["ncol"], bold=False))},'
            f'{snbt(txt(line, "white"))}]')


for p in STAFF:
    al = AIRLINES.get(p["airline"]) if p["airline"] else None
    fmt = dict(place=p.get("label", ""), airline=al[0] if al else "our airline", brand=p["brand"] or "our rental desk")
    lines = [l.format(**fmt) for l in LINES[greet_key(p)]]
    L = ["scoreboard players set @s ewrs_cd 10",
         "playsound minecraft:entity.villager.ambient neutral @s ~ ~ ~ 0.4 1.3",
         f"execute store result score #r ewrs_tmp run random value 1..{len(lines)}"]
    for k, line in enumerate(lines, 1):
        L.append(f"execute if score #r ewrs_tmp matches {k} run " + say_line(p, line))
    extra = info_line(p)
    if extra:
        L.append(f"tellraw @s {snbt(txt('  ' + extra, 'gray'))}")
    r = p["role"]
    if r == "checkin" and p["airline"] in AIRLINES:
        L.append("scoreboard players enable @s ewrs_buy")
        idx = list(AIRLINES).index(p["airline"])
        chat = [snbt(txt('  ')), snbt(button(f'Flight on {al[0]} - ${FLIGHT_PRICE}', 100 + idx, f'Book a flyable {al[0]} jet. It will be waiting on a taxiway stand by the terminal.'))]
        acts = [{"label": {"text": f"Flight on {al[0]} - ${FLIGHT_PRICE}", "color": "green"},
                 "tooltip": {"text": f"Your own flyable {al[0]} jet, waiting on a taxiway stand by the terminal"},
                 "width": 260, "action": {"type": "run_command", "command": f"/trigger ewrs_buy set {100 + idx}"}}]
        if SCENIC:
            chat += [snbt(txt(' ')), snbt(button(f'Burj Scenic Flight - ${SCENIC_PRICE}', 50, 'Automated sightseeing flight past the Burj Khalifa. Books the next departure and sends you to the gate.', 'gold'))]
            acts.append({"label": {"text": f"Burj Khalifa Scenic Flight - ${SCENIC_PRICE}", "color": "gold"},
                         "tooltip": {"text": "Automated sightseeing flight: books the next departure and sends you to the gate"},
                         "width": 260, "action": {"type": "run_command", "command": "/trigger ewrs_buy set 50"}})
        dlg = {"type": "minecraft:multi_action",
               "title": {"text": f"{al[0]} Check-in", "color": "white"},
               "body": {"type": "minecraft:plain_message", "contents": {"text": f"{p['name']}: Where are we flying today?"}},
               "actions": acts, "columns": 1, "exit_action": {"label": {"text": "Not now"}}}
        L.append(f"dialog show @s {snbt(dlg)}")
        L.append("tellraw @s [" + ",".join(chat) + "]")
    elif r == "rental":
        L.append("scoreboard players enable @s ewrs_buy")
        L.append(f"scoreboard players set @s ewrs_lv {BRAND_LEVEL.get((p['brand'] or 'hertz').lower(), 1)}")
        btns = [snbt(txt("  Rent a car, $%d: " % RENT_PRICE, "white"))]
        for t, fnm, lab in CARS:
            btns.append(snbt(button(lab, t, f"Rent the {lab} for ${RENT_PRICE}. It waits in our level of garage P-A.", "gold")))
            btns.append(snbt(txt(" ")))
        L.append("tellraw @s [" + ",".join(btns) + "]")
    elif r == "reception":
        L.append("scoreboard players enable @s ewrs_buy")
        L.append(f"tellraw @s [{snbt(txt('  '))},{snbt(button(f'Room key - ${ROOM_PRICE}', 10, 'One night at the Newark Airport Marriott. You get a room key.'))}]")
    F[f"npc/{p['id']}"] = L

# --- purchases
D = ["# as + at the player who pressed a menu button (trigger ewrs_buy). Needs the right employee within 10 blocks.",
     "scoreboard players operation #b ewrs_tmp = @s ewrs_buy",
     "scoreboard players reset @s ewrs_buy"]
near_rental = "if entity @e[type=mannequin,tag=ewrs_r_rental,distance=..10]"
for t, fnm, lab in CARS:
    D.append(f"execute if score #b ewrs_tmp matches {t} {near_rental} run function {NS}:rent/{fnm}")
D.append(f"execute if score #b ewrs_tmp matches 1..5 unless entity @e[type=mannequin,tag=ewrs_r_rental,distance=..10] run tellraw @s {snbt(txt('Please see a rental agent at the rental center to rent a car.', 'red'))}")
D.append(f"execute if score #b ewrs_tmp matches 10 if entity @e[type=mannequin,tag=ewrs_r_reception,distance=..10] run function ewr_econ:try_buy {{price:{ROOM_PRICE}, item:\"Marriott room key\", then:\"{NS}:sell/room_key\"}}")
D.append(f"execute if score #b ewrs_tmp matches 10 unless entity @e[type=mannequin,tag=ewrs_r_reception,distance=..10] run tellraw @s {snbt(txt('Please see the Marriott front desk for a room.', 'red'))}")
for idx, a in enumerate(AIRLINES):
    D.append(f"execute if score #b ewrs_tmp matches {100 + idx} if entity @e[type=mannequin,tag=ewrs_r_checkin,tag=ewrs_air_{a},distance=..10] run function {NS}:fly/{a}")
D.append(f"execute if score #b ewrs_tmp matches 100..199 unless entity @e[type=mannequin,tag=ewrs_r_checkin,distance=..10] run tellraw @s {snbt(txt('Please book at an airline check-in counter.', 'red'))}")
D.append(f"execute if score #b ewrs_tmp matches 900 run function {NS}:fly/walk")
if SCENIC:
    D.append(f"execute if score #b ewrs_tmp matches 50 if entity @s[tag=ewr_flt_booked] run return run tellraw @s {snbt(txt('You already have a Burj Scenic Flight booking. Head to gate A10 in Terminal A (function ewr_flights:status shows the next departure).', 'yellow'))}")
    D.append(f"execute if score #b ewrs_tmp matches 50 if entity @s[tag=ewr_flt_pax] run return run tellraw @s {snbt(txt('You are already on a scenic flight!', 'yellow'))}")
    D.append(f"execute if score #b ewrs_tmp matches 50 if entity @e[type=mannequin,tag=ewrs_r_checkin,distance=..10] run function ewr_econ:try_buy {{price:{SCENIC_PRICE}, item:\"Burj Scenic Flight\", then:\"ewr_flights:book\"}}")
    D.append(f"execute if score #b ewrs_tmp matches 50 unless entity @e[type=mannequin,tag=ewrs_r_checkin,distance=..10] run tellraw @s {snbt(txt('Please book at an airline check-in counter.', 'red'))}")
print("SCENIC (ewr_flights) wired:", SCENIC)
F["buy/dispatch"] = D

# rental cars: garage P-A, one company per level (bays from the parking agent: parkingays_PA.json).
# pick the renter's company level (set when they talked to that agent), first free space, else recycle a parked car
BAYS = json.load(open(os.path.join(HERE, "..", "parking", "bays_PA.json"), encoding="utf-8"))
LEVELS = {}
for bay in BAYS:
    if bay["tag"].startswith("P-A L") and str(bay.get("kind", "")).startswith("rental"):
        LEVELS.setdefault(int(bay["tag"][5:]), []).append(bay)
for L in LEVELS:
    LEVELS[L].sort(key=lambda q: -q["world"][2])
BRAND_LEVEL = {"hertz": 1, "avis": 2, "enterprise": 3, "national": 4, "budget": 5, "alamo": 6}
CAR_SPOTS = [1]
for t, fnm, lab in CARS:
    R = ["scoreboard players set #slot ewrs_tmp 0",
         "execute unless score @s ewrs_lv matches 1..6 run scoreboard players set @s ewrs_lv 1"]
    for L, bays in sorted(LEVELS.items()):
        for k, q in enumerate(bays, 1):
            x, y, z = q["world"]
            R.append(f"execute if score #slot ewrs_tmp matches 0 if score @s ewrs_lv matches {L} positioned {x} {y} {z} unless entity @e[type=horse,tag=ewrcar,distance=..2.5] run scoreboard players set #slot ewrs_tmp {L * 10 + k}")
    for L, bays in sorted(LEVELS.items()):
        for k, q in enumerate(bays, 1):
            x, y, z = q["world"]
            R.append(f"execute if score #slot ewrs_tmp matches 0 if score @s ewrs_lv matches {L} positioned {x} {y} {z} if entity @e[type=horse,tag=ewrcar,tag=!ewrcar_driving,distance=..2.5] run scoreboard players set #slot ewrs_tmp {-(L * 10 + k)}")
    R.append(f"execute if score #slot ewrs_tmp matches 0 run return run tellraw @s {snbt(txt('Sorry, every space on our level is taken by a car someone is driving. Try again in a minute.', 'red'))}")
    R.append(f"function ewr_econ:try_buy {{price:{RENT_PRICE}, item:\"{lab} rental\", then:\"{NS}:rent/give_{fnm}\"}}")
    F[f"rent/{fnm}"] = R
    G = []
    for L, bays in sorted(LEVELS.items()):
        for k, q in enumerate(bays, 1):
            x, y, z = q["world"]; n = L * 10 + k
            G.append(f"execute if score #slot ewrs_tmp matches {-n} positioned {x} {y} {z} as @e[type=horse,tag=ewrcar,tag=!ewrcar_driving,distance=..2.5,limit=1] at @s run function ewr_cars:internal/remove_car")
            G.append(f"execute if score #slot ewrs_tmp matches {-n} run scoreboard players set #slot ewrs_tmp {n}")
    for L, bays in sorted(LEVELS.items()):
        for k, q in enumerate(bays, 1):
            x, y, z = q["world"]; n = L * 10 + k
            G.append(f"execute if score #slot ewrs_tmp matches {n} positioned {x} {y} {z} rotated {q['yaw']} 0 run function ewr_cars:place/{fnm}")
            G.append(f"execute if score #slot ewrs_tmp matches {n} run tellraw @s [{snbt(txt('[Rental] ', 'gold'))},"
                     f"{snbt(txt(f'Your {lab} is on level {L}, space {k} of garage P-A ({int(x)}, {y}, {int(z)}). Follow the walkway and signs from the counters. Right-click the car to get in, W to drive, sneak to get out. Enjoy!', 'white'))}]")
    F[f"rent/give_{fnm}"] = G

# Marriott room key
lo, hi = MARRIOTT_FLOORS
F["sell/room_key"] = [
    f"execute store result storage ewr_staff:k floor int 1 run random value {lo}..{hi}",
    "execute store result storage ewr_staff:k room int 1 run random value 10..30",
    f"function {NS}:sell/room_key_m with storage ewr_staff:k",
]
F["sell/room_key_m"] = [
    '$give @s minecraft:tripwire_hook[minecraft:custom_name={text:"Room key",color:"gold",italic:false},'
    'minecraft:lore=[{text:"Newark Airport Marriott",color:"gray",italic:false},{text:"Room $(floor)$(room) · Floor $(floor)",color:"white",italic:false}],'
    'minecraft:enchantment_glint_override=true] 1',
    '$tellraw @s [{text:"[Marriott] ",color:"dark_red"},{text:"Here is your key: room $(floor)$(room) on floor $(floor). The elevators are just past the front desk. Enjoy your stay!",color:"white"}]',
]

# flights: pick a stand (airline's terminal first), recycle a parked sold plane if all are taken, charge, spawn
for idx, (a, al) in enumerate(AIRLINES.items()):
    order = [s for s in STANDS if s[3] == al[5]] + [s for s in STANDS if s[3] != al[5]]
    R = ["scoreboard players set #slot ewrs_tmp 0"]
    for s in order:
        R.append(f"execute if score #slot ewrs_tmp matches 0 positioned {s[1]} 64 {s[2]} unless entity @e[type=happy_ghast,tag=ewr_plane,distance=..18] run scoreboard players set #slot ewrs_tmp {s[0]}")
    for s in order:
        R.append(f"execute if score #slot ewrs_tmp matches 0 positioned {s[1]} 64 {s[2]} if entity @e[type=happy_ghast,tag=ewrs_sold,tag=ewr_parked,distance=..3] run scoreboard players set #slot ewrs_tmp {-s[0]}")
    R.append(f"execute if score #slot ewrs_tmp matches 0 run return run tellraw @s {snbt(txt('Sorry, all aircraft stands are occupied. Fly or remove a plane (function ewr_planes:remove_nearest) and try again.', 'red'))}")
    R.append(f"function ewr_econ:try_buy {{price:{FLIGHT_PRICE}, item:\"{al[0]} flight\", then:\"{NS}:fly/give_{a}\"}}")
    F[f"fly/{a}"] = R
    G = []
    for s in STANDS:
        G.append(f"execute if score #slot ewrs_tmp matches {-s[0]} positioned {s[1]} 64 {s[2]} as @e[type=happy_ghast,tag=ewrs_sold,tag=ewr_parked,distance=..3,limit=1] at @s run function ewr_planes:internal/remove_self")
        G.append(f"execute if score #slot ewrs_tmp matches {-s[0]} run scoreboard players set #slot ewrs_tmp {s[0]}")
    for s in STANDS:
        G.append(f'execute if score #slot ewrs_tmp matches {s[0]} run function ewr_planes:spawn_at {{x:{s[1]},y:64,z:{s[2]},yaw:180,livery:"{livery(a)}",size:"{al[6]}"}}')
        G.append(f"execute if score #slot ewrs_tmp matches {s[0]} as @e[type=happy_ghast,tag=ewr_plane] if score @s ewr_id = #next ewr_id run tag @s add ewrs_sold")
        G.append(f"execute if score #slot ewrs_tmp matches {s[0]} run tellraw @s [{snbt(txt('[' + al[0] + '] ', al[4]))},"
                 f"{snbt(txt(f'You are booked! Your {al[0]} jet is waiting at stand {s[0]} on {s[4]}, at ({int(s[1])}, 64, {int(s[2])}), nose north. Right-click the cockpit (just behind the nose) to board; W to fly, Space to climb, Shift to get off. ', 'white'))},"
                 f"{snbt(button('Walk me to my plane', 900, 'Teleports you beside your plane'))}]")
    G.append("scoreboard players operation @s ewrs_pl = #slot ewrs_tmp")
    G.append("scoreboard players enable @s ewrs_buy")
    F[f"fly/give_{a}"] = G
W = [f"execute unless score @s ewrs_pl matches 1.. run return run tellraw @s {snbt(txt('You have no flight booked. Book one at an airline check-in counter.', 'red'))}"]
for s in STANDS:
    # beside the nose on the west side, facing east toward the cockpit
    W.append(f"execute if score @s ewrs_pl matches {s[0]} run tp @s {s[1] - 5} 64 {s[2] - 7} -90 0")
W.append("scoreboard players reset @s ewrs_pl")
F["fly/walk"] = W

# --- help / dev
by_role = {}
for p in STAFF:
    by_role.setdefault(p["role"], []).append(p)
Hh = ['tellraw @s {text:"--- EWR Staff ---",color:"aqua",bold:true}',
      f'tellraw @s {{text:"{len(STAFF)} employees. Right-click anyone at a counter to talk. Paid services: airline check-in (flights ${FLIGHT_PRICE}), rental cars (${RENT_PRICE}), Marriott front desk (room key ${ROOM_PRICE}).",color:"white"}}',
      'tellraw @s {text:"Admin: /function ewr_staff:spawn_all (respawn) | ewr_staff:remove_all",color:"gray"}']
F["help"] = Hh

# ----------------------------------------------------------------------------------------- write
if os.path.isdir(DP):
    shutil.rmtree(DP)
fd = os.path.join(DP, "data", NS, "function")
for name, lines in F.items():
    path = os.path.join(fd, *name.split("/")) + ".mcfunction"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
tg = os.path.join(DP, "data", "minecraft", "tags", "function")
os.makedirs(tg, exist_ok=True)
json.dump({"values": [f"{NS}:load"]}, open(os.path.join(tg, "load.json"), "w"))
json.dump({"values": [f"{NS}:tick"]}, open(os.path.join(tg, "tick.json"), "w"))
json.dump({"pack": {"description": "EWR staff: employees at every counter (mannequins + interactions)",
                    "min_format": [121, 0], "max_format": [200, 0]}},
          open(os.path.join(DP, "pack.mcmeta"), "w"), indent=1)
json.dump([{k: p[k] for k in ("id", "role", "name", "title", "x", "y", "z", "yaw")} for p in STAFF],
          open(os.path.join(HERE, "roster.json"), "w"), indent=0)
print(f"{len(STAFF)} staff, {len(F)} functions, {len(CAR_SPOTS)} car spots -> {DP}")
from collections import Counter
print(Counter(p["role"] for p in STAFF))
