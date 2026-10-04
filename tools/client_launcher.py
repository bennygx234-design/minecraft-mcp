"""Download and launch the vanilla 26.3 client in an isolated game folder (offline account).

Used to take real in-game screenshots of builds. Everything lives under
minecraft-mcp/client, so the user's own .minecraft is never touched.

  python tools/client_launcher.py download
  python tools/client_launcher.py launch [--name Claude] [--server 127.0.0.1:25565] [--width 1600 --height 900]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = os.path.join(ROOT, "client")
VERSION = "26.3"
VERSION_JSON = os.path.join(os.environ["APPDATA"], ".minecraft", "versions", VERSION, f"{VERSION}.json")
CLIENT_JAR = os.path.join(ROOT, "data", f"client-{VERSION}.jar")
sys.path.insert(0, ROOT)


def _java() -> str:
    from mcmcp.engine import JAVA
    return JAVA.replace("java.exe", "javaw.exe") if os.name == "nt" else JAVA


def _sha1(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fetch(url: str, dest: str, sha1: str | None = None) -> None:
    if os.path.exists(dest) and (sha1 is None or _sha1(dest) == sha1):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 16):
            f.write(chunk)
    if sha1 and _sha1(tmp) != sha1:
        os.remove(tmp)
        raise IOError(f"checksum mismatch for {url}")
    os.replace(tmp, dest)


def _rules_ok(rules, features=None) -> bool:
    if not rules:
        return True
    features = features or {}
    allowed = False
    for r in rules:
        ok = True
        os_ = r.get("os", {})
        if os_.get("name") and os_["name"] != "windows":
            ok = False
        if os_.get("arch") and os_["arch"] != ("x86" if platform.architecture()[0] == "32bit" else "x64"):
            ok = False
        vr = os_.get("versionRange")
        if vr:
            ver = tuple(int(p) for p in platform.version().split(".")[:3])
            mn = tuple(int(p) for p in vr.get("min", "0").split("."))
            mx = tuple(int(p) for p in vr.get("max", "999").split("."))
            if not (mn <= ver <= mx if "max" in vr else ver >= mn):
                ok = False
        for k, v in r.get("features", {}).items():
            if features.get(k) != v:
                ok = False
        if ok:
            allowed = r["action"] == "allow"
    return allowed


def manifest() -> dict:
    with open(VERSION_JSON, encoding="utf-8") as f:
        return json.load(f)


def libraries(j: dict) -> list[tuple[str, str, str]]:
    out = []
    for lib in j["libraries"]:
        if not _rules_ok(lib.get("rules")):
            continue
        art = lib.get("downloads", {}).get("artifact")
        if not art:
            continue
        if "arm64" in art["path"] and platform.machine().lower() not in ("arm64", "aarch64"):
            continue
        out.append((art["url"], os.path.join(CLIENT, "libraries", art["path"]), art["sha1"]))
    return out


def download() -> None:
    j = manifest()
    jobs = libraries(j)
    idx = j["assetIndex"]
    idx_path = os.path.join(CLIENT, "assets", "indexes", f"{idx['id']}.json")
    _fetch(idx["url"], idx_path, idx["sha1"])
    with open(idx_path, encoding="utf-8") as f:
        objects = json.load(f)["objects"]
    for o in objects.values():
        h = o["hash"]
        jobs.append((f"https://resources.download.minecraft.net/{h[:2]}/{h}",
                     os.path.join(CLIENT, "assets", "objects", h[:2], h), h))
    lc = j.get("logging", {}).get("client", {}).get("file")
    if lc:
        jobs.append((lc["url"], os.path.join(CLIENT, "assets", "log_configs", lc["id"]), lc["sha1"]))
    print(f"{len(jobs)} files to check/download")
    done = 0
    with ThreadPoolExecutor(16) as ex:
        for _ in ex.map(lambda a: _fetch(*a), jobs):
            done += 1
            if done % 500 == 0:
                print(f"  {done}/{len(jobs)}", flush=True)
    print("download complete")


def offline_uuid_for(name: str) -> uuid.UUID:
    """Same as Java's UUID.nameUUIDFromBytes("OfflinePlayer:" + name), which offline servers use."""
    b = bytearray(hashlib.md5(("OfflinePlayer:" + name).encode()).digest())
    b[6] = (b[6] & 0x0F) | 0x30
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b))


def _sub(s: str, vals: dict) -> str:
    for k, v in vals.items():
        s = s.replace("${" + k + "}", v)
    return s


def write_options(width: int, height: int) -> None:
    """First-launch defaults: no onboarding screens, keep rendering when unfocused, nice view."""
    os.makedirs(CLIENT, exist_ok=True)
    path = os.path.join(CLIENT, "options.txt")
    opts = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    k, v = line.rstrip("\n").split(":", 1)
                    opts[k] = v
    opts.update({
        "onboardAccessibility": "false", "skipMultiplayerWarning": "true", "joinedFirstServer": "true",
        "tutorialStep": "none", "pauseOnLostFocus": "false", "renderDistance": "16", "simulationDistance": "8",
        "fov": "0.15", "guiScale": "2", "narrator": "0", "soundCategory_master": "0.0", "fullscreen": "false",
        "overrideWidth": str(width), "overrideHeight": str(height), "graphicsMode": "1", "ao": "true",
        "entityShadows": "true", "renderClouds": "\"fast\"", "showSubtitles": "false", "hideBundleTutorial": "true",
    })
    with open(path, "w", encoding="utf-8") as f:
        for k, v in opts.items():
            f.write(f"{k}:{v}\n")


def launch(name: str, server: str | None, width: int, height: int) -> subprocess.Popen:
    j = manifest()
    write_options(width, height)
    natives = os.path.join(CLIENT, "natives")
    os.makedirs(natives, exist_ok=True)
    cp = [p for _, p, _ in libraries(j)] + [CLIENT_JAR]
    features = {"has_custom_resolution": True, "is_quick_play_multiplayer": bool(server)}
    offline_uuid = offline_uuid_for(name)
    vals = {
        "auth_player_name": name, "version_name": VERSION, "game_directory": CLIENT,
        "assets_root": os.path.join(CLIENT, "assets"), "assets_index_name": j["assetIndex"]["id"],
        "auth_uuid": offline_uuid.hex, "auth_access_token": "0", "clientid": "0", "auth_xuid": "0",
        "version_type": "release", "resolution_width": str(width), "resolution_height": str(height),
        "quickPlayMultiplayer": server or "", "natives_directory": natives, "launcher_name": "mcmcp",
        "launcher_version": "1", "classpath": os.pathsep.join(cp), "classpath_separator": os.pathsep,
        "library_directory": os.path.join(CLIENT, "libraries"), "user_type": "legacy", "quickPlayPath": "",
    }

    def expand(args):
        out = []
        for a in args:
            if isinstance(a, str):
                out.append(_sub(a, vals))
            elif _rules_ok(a.get("rules"), features):
                v = a["value"]
                out.extend(_sub(x, vals) for x in (v if isinstance(v, list) else [v]))
        return out

    jvm = expand(j["arguments"].get("default-user-jvm", [])) + expand(j["arguments"]["jvm"])
    lc = j.get("logging", {}).get("client")
    if lc:
        jvm.append(lc["argument"].replace("${path}", os.path.join(CLIENT, "assets", "log_configs", lc["file"]["id"])))
    game = [a for a in expand(j["arguments"]["game"]) if a != "--quickPlayPath" and a != ""]
    cmd = [_java()] + jvm + [j["mainClass"]] + game
    log = open(os.path.join(CLIENT, "client-console.log"), "ab")
    return subprocess.Popen(cmd, cwd=CLIENT, stdout=log, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["download", "launch"])
    ap.add_argument("--name", default="Claude")
    ap.add_argument("--server", default="127.0.0.1:25565")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    a = ap.parse_args()
    if a.action == "download":
        download()
    else:
        p = launch(a.name, a.server, a.width, a.height)
        print("client pid", p.pid)
