# -*- coding: utf-8 -*-
# Version: 1.0.1 - Production release (reliable lobby sweep)
"""Offline hall, energy-core preset unlocking, and complete local AI combat engine for NeoX Python 2.7 runtime."""

import os
import traceback
import sys
import gc
import re

DOC_DIRS = (
    "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents",
    "/storage/emulated/0/Android/data/com.netease.g104.cn/files/Netease/g104/Documents",
)

try:
    _UNICODE_TYPE = unicode
    _PY2 = True
except NameError:
    _UNICODE_TYPE = str
    _PY2 = False

NAME_PATH = "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/player_name.txt"
XML_PREFS_PATH = "/data/data/com.netease.g104.cn/shared_prefs/reborn_login.xml"
CMD_PATH = "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/cmd.py"
FPS_PATH = "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_fps.txt"
ENABLE_LIVE_REPL = False  # Production: REPL disabled to prevent 0.5s polling stutter

# Anti-overwrite self-defense: block APK extractLatestScript from overwriting this mod
for _d in DOC_DIRS:
    try:
        _tmp_path = os.path.join(_d, "reborn_offline.py.tmp")
        if os.path.isfile(_tmp_path):
            os.remove(_tmp_path)
        if not os.path.exists(_tmp_path):
            os.makedirs(_tmp_path)
    except Exception:
        pass

_running = False
_player = None
_account = None
_offline_rule_overrides = {}


def log(*args):
    try:
        parts = []
        for v in args:
            if isinstance(v, _UNICODE_TYPE):
                try:
                    parts.append(v.encode("utf-8"))
                except Exception:
                    parts.append(str(v))
            else:
                parts.append(str(v))
        msg = "[REBORN_OFFLINE] " + " ".join(parts)
        try:
            print(msg)
        except Exception:
            pass
        for _d in DOC_DIRS:
            try:
                if not os.path.isdir(_d):
                    try:
                        os.makedirs(_d)
                    except Exception:
                        pass
                _logfile = os.path.join(_d, "reborn_debug.log")
                with open(_logfile, "a") as f:
                    f.write(msg + "\n")
                break
            except Exception:
                pass
    except Exception:
        pass


log("=== REBORN MOD SCRIPT LOADED ===")
log("Python version:", sys.version)


_ZH_TO_EN = {
    u"\u7d22\u5c14": u"Thor",
    u"\u96f7\u795e": u"Thor",
    u"\u96f7\u795e\u7d22\u5c14": u"Thor",
    u"\u7d22\u5c14\xb7\u5965\u4e01\u68ee": u"Thor Odinson",
    u"\u795e\u5a01\u7d22\u5c14": u"Mighty Thor",
    u"\u7b80\xb7\u798f\u65af\u7279": u"Jane Foster",
    u"\u6d1b\u57fa": u"Loki",
    u"\u6d77\u59c6\u8fbe\u5c14": u"Heimdall",
    u"\u5973\u6b66\u795e": u"Valkyrie",
    u"\u74e6\u5c14\u57fa\u91cc": u"Valkyrie",
    u"\u5e0c\u8299": u"Lady Sif",
    u"\u6d77\u62c9": u"Hela",
    u"\u523d\u5b50\u624b": u"Executioner",
    u"\u65af\u79d1\u5c14\u5947": u"Skurge",
    u"\u6c99\u4eba": u"Sandman",
    u"\u5a01\u5ec9\xb7\u8d1d\u514b": u"Sandman",
    u"\u5f17\u6797\u7279\xb7\u9a6c\u5c14\u79d1": u"Sandman",
    u"\u8718\u86db\u4fa0": u"Spider-Man",
    u"\u8718\u86db\u4eba": u"Spider-Man",
    u"\u5f7c\u5f97\xb7\u5e15\u514b": u"Spider-Man",
    u"\u5f7c\u5f97": u"Peter Parker",
    u"\u7eff\u9b54": u"Green Goblin",
    u"\u8bfa\u66fc\xb7\u5965\u65af\u672c": u"Norman Osborn",
    u"\u7ae0\u9c7c\u535a\u58eb": u"Doctor Octopus",
    u"\u5965\u6258\xb7\u5965\u514b\u5854\u7ef4\u65af": u"Otto Octavius",
    u"\u795e\u79d8\u5ba2": u"Mysterio",
    u"\u79d8\u5883\u9b54": u"Mysterio",
    u"\u6606\u6c40\xb7\u8d1d\u514b": u"Quentin Beck",
    u"\u5c60\u6740": u"Carnage",
    u"\u514b\u83b1\u56fe\u65af\xb7\u5361\u8428\u8fea": u"Cletus Kasady",
    u"\u6bd2\u6db2": u"Venom",
    u"\u57c3\u8fea\xb7\u5e03\u6d1b\u514b": u"Eddie Brock",
    u"\u9ed1\u732b": u"Black Cat",
    u"\u8d39\u8389\u897f\u4e9a\xb7\u54c8\u8fea": u"Felicia Hardy",
    u"\u5e7d\u7075\u8718\u86db": u"Ghost-Spider",
    u"\u683c\u6e29\u8718\u86db": u"Spider-Gwen",
    u"\u683c\u6e29\xb7\u65af\u9edb\u897f": u"Spider-Gwen",
    u"\u683c\u6e29": u"Gwen Stacy",
    u"\u8fc8\u5c14\u65af\xb7\u83ab\u62c9\u83b1\u65af": u"Miles Morales",
    u"\u8fc8\u5c14\u65af": u"Miles Morales",
    u"\u7535\u5149\u4eba": u"Electro",
    u"\u730e\u4eba\u514b\u83b1\u6587": u"Kraven",
    u"\u514b\u83b1\u6587": u"Kraven",
    u"\u7280\u725b\u4eba": u"Rhino",
    u"\u874e\u5b50": u"Scorpion",
    u"\u86db\u4e1d": u"Silk",
    u"\u8718\u86db\u4fa02099": u"Spider-Man 2099",
    u"\u8718\u732a\u4fa0": u"Spider-Ham",
    u"\u94a2\u94c1\u4fa0": u"Iron Man",
    u"\u92fc\u9435\u4fe0": u"Iron Man",
    u"\u6258\u5c3c\xb7\u65af\u5854\u514b": u"Iron Man",
    u"\u6258\u5c3c": u"Tony Stark",
    u"\u6218\u4e89\u673a\u5668": u"War Machine",
    u"\u8a79\u59c6\u65af\xb7\u7f57\u5fb7\u65af": u"War Machine",
    u"\u7f57\u5fb7": u"War Machine",
    u"\u53cd\u6d69\u514b\u88c5\u7532": u"Hulkbuster",
    u"\u94c1\u5fc3": u"Ironheart",
    u"\u8389\u8389\xb7\u5a01\u5ec9\u59c6\u65af": u"Riri Williams",
    u"\u54c8\u76ae\xb7\u970d\u6839": u"Happy Hogan",
    u"\u54c8\u76ae": u"Happy Hogan",
    u"\u7f8e\u56fd\u961f\u957f": u"Captain America",
    u"\u53f2\u8482\u592b\xb7\u7f57\u6770\u65af": u"Captain America",
    u"\u53f2\u8482\u592b": u"Captain America",
    u"\u5361\u7279\u961f\u957f": u"Captain Carter",
    u"\u4f69\u5409\xb7\u5361\u7279": u"Peggy Carter",
    u"\u51ac\u5175": u"Winter Soldier",
    u"\u51ac\u5b63\u6218\u58eb": u"Winter Soldier",
    u"\u5df4\u57fa\xb7\u5df4\u6069\u65af": u"Winter Soldier",
    u"\u5df4\u57fa": u"Winter Soldier",
    u"\u730e\u9e70": u"Falcon",
    u"\u5c71\u59c6\xb7\u5a01\u5c14\u900a": u"Falcon",
    u"\u9ed1\u5be1\u5987": u"Black Widow",
    u"\u5a1c\u5854\u838e\xb7\u7f57\u66fc\u8bfa\u592b": u"Black Widow",
    u"\u5a1c\u5854\u838e": u"Natasha",
    u"\u9e70\u773c": u"Hawkeye",
    u"\u514b\u6797\u7279\xb7\u5df4\u987f": u"Hawkeye",
    u"\u6d69\u514b": u"Hulk",
    u"\u7eff\u5de8\u4eba": u"Hulk",
    u"\u5e03\u9c81\u65af\xb7\u73ed\u7eb3": u"Hulk",
    u"\u73ed\u7eb3": u"Bruce Banner",
    u"\u60ca\u5947\u961f\u957f": u"Captain Marvel",
    u"\u5361\u7f57\u5c14\xb7\u4e39\u5f17\u65af": u"Captain Marvel",
    u"\u5361\u7f57\u5c14": u"Carol Danvers",
    u"\u8681\u4eba": u"Ant-Man",
    u"\u65af\u79d1\u7279\xb7\u6717": u"Ant-Man",
    u"\u9ec4\u8702\u5973": u"Wasp",
    u"\u970d\u666e\xb7\u8303\xb7\u6234\u56e0": u"Wasp",
    u"\u7eef\u7ea2\u5973\u5deb": u"Scarlet Witch",
    u"\u7329\u7ea2\u5973\u5deb": u"Scarlet Witch",
    u"\u65fa\u8fbe\xb7\u9a6c\u514b\u897f\u83ab\u592b": u"Scarlet Witch",
    u"\u65fa\u8fbe": u"Scarlet Witch",
    u"\u5e7b\u89c6": u"Vision",
    u"\u5feb\u94f6": u"Quicksilver",
    u"\u76ae\u7279\u7f57\xb7\u9a6c\u514b\u897f\u83ab\u592b": u"Quicksilver",
    u"\u9ed1\u8c79": u"Black Panther",
    u"\u7279\u67e5\u62c9": u"Black Panther",
    u"\u82cf\u777f": u"Shuri",
    u"\u5965\u514b\u8036": u"Okoye",
    u"\u82f1\u56fd\u961f\u957f": u"Captain Britain",
    u"\u5e03\u83b1\u6069\xb7\u5e03\u62c9\u591a\u514b": u"Brian Braddock",
    u"\u706d\u9738": u"Thanos",
    u"\u8428\u8bfa\u65af": u"Thanos",
    u"\u4ea1\u5203\u591c\u4faf": u"Corvus Glaive",
    u"\u6697\u591c\u6bd4\u90bb\u661f": u"Proxima Midnight",
    u"\u4e4c\u6728\u5589": u"Ebony Maw",
    u"\u9ed1\u66dc\u9738\u738b": u"Cull Obsidian",
    u"\u9ed1\u77ee\u661f": u"Cull Obsidian",
    u"\u661f\u7235": u"Star-Lord",
    u"\u5f7c\u5f97\xb7\u594e\u5c14": u"Star-Lord",
    u"\u683c\u9c81\u7279": u"Groot",
    u"\u706b\u7bad\u6d63\u718a": u"Rocket Raccoon",
    u"\u706b\u7bad": u"Rocket Raccoon",
    u"\u52c7\u5ea6": u"Yondu",
    u"\u52c7\u5ea6\xb7\u4e4c\u4e39\u5854": u"Yondu",
    u"\u87b3\u8782\u5973": u"Mantis",
    u"\u66fc\u8482\u65af": u"Mantis",
    u"\u5fb7\u62c9\u514b\u65af": u"Drax",
    u"\u6bc1\u706d\u8005\u5fb7\u62c9\u514b\u65af": u"Drax the Destroyer",
    u"\u5361\u9b54\u62c9": u"Gamora",
    u"\u7f57\u5357": u"Ronan",
    u"\u6307\u63a7\u8005\u7f57\u5357": u"Ronan the Accuser",
    u"\u4e9a\u5f53\u672f\u58eb": u"Adam Warlock",
    u"\u5b87\u5b99\u672f\u58eb\u4e9a\u5f53": u"Adam Warlock",
    u"\u592a\u7a7a\u72d7\u79d1\u65af\u83ab": u"Cosmo",
    u"\u79d1\u65af\u83ab": u"Cosmo",
    u"\u81f3\u9ad8\u8fdb\u5316": u"High Evolutionary",
    u"\u5947\u5f02\u535a\u58eb": u"Doctor Strange",
    u"\u53f2\u8482\u82ac\xb7\u65af\u7279\u5170\u5947": u"Doctor Strange",
    u"\u53e4\u4e00": u"Ancient One",
    u"\u6076\u7075\u9a91\u58eb": u"Ghost Rider",
    u"\u5f3a\u5c3c\xb7\u5e03\u96f7\u6cfd": u"Ghost Rider",
    u"\u7f57\u6bd4\xb7\u96f7\u8036\u65af": u"Ghost Rider",
    u"\u83ab\u5ea6": u"Baron Mordo",
    u"\u83ab\u5ea6\u7537\u7235": u"Baron Mordo",
    u"\u9b54\u591a": u"Mordo",
    u"\u738b": u"Wong",
    u"\u514b\u83b1\u4e9a": u"Clea",
    u"\u5200\u950b\u6218\u58eb": u"Blade",
    u"\u5200\u950b": u"Blade",
    u"\u57c3\u91cc\u514b\xb7\u5e03\u9c81\u514b\u65af": u"Blade",
    u"\u6708\u5149\u9a91\u58eb": u"Moon Knight",
    u"\u9a6c\u514b\xb7\u65af\u4f69\u514b\u7279": u"Moon Knight",
    u"\u963f\u7f8e\u8389\u5361\xb7\u67e5\u7ef4\u5179": u"America Chavez",
    u"\u963f\u7f8e\u8389\u5361": u"America Chavez",
    u"\u67e5\u7ef4\u5179": u"America Chavez",
    u"\u91d1\u521a\u72fc": u"Wolverine",
    u"\u7f57\u6839": u"Wolverine",
    u"X\u6559\u6388": u"Professor X",
    u"\u67e5\u5c14\u65af\xb7\u6cfd\u7ef4\u5c14": u"Professor X",
    u"\u4e07\u78c1\u738b": u"Magneto",
    u"\u57c3\u91cc\u514b\xb7\u5170\u8c22\u5c14": u"Magneto",
    u"\u956d\u5c04\u773c": u"Cyclops",
    u"\u65af\u79d1\u7279\xb7\u8428\u9ed8\u65af": u"Cyclops",
    u"\u66b4\u98ce\u5973": u"Storm",
    u"\u5965\u7f57\u6d1b\xb7\u95e8\u7f57": u"Storm",
    u"\u7434\xb7\u845b\u857e": u"Phoenix",
    u"\u51e4\u51f0\u5973": u"Phoenix",
    u"\u91ce\u517d": u"Beast",
    u"\u6c49\u514b\xb7\u9ea6\u8003\u4f0a": u"Beast",
    u"\u5929\u4f7f": u"Angel",
    u"\u51b0\u4eba": u"Iceman",
    u"\u767d\u7687\u540e": u"Emma Frost",
    u"\u827e\u739b\xb7\u5f17\u7f57\u65af\u7279": u"Emma Frost",
    u"\u7075\u8776": u"Psylocke",
    u"\u724c\u7687": u"Gambit",
    u"\u94a2\u529b\u58eb": u"Colossus",
    u"\u79d8\u5ba2": u"Magik",
    u"\u674e\u5343\u6b22": u"Jubilee",
    u"\u9b54\u4ed9\u5b50": u"Pixie",
    u"\u7535\u7d22": u"Cable",
    u"\u591a\u7c73\u8bfa": u"Domino",
    u"\u591c\u884c\u8005": u"Nightcrawler",
    u"\u7f57\u5239\u5973": u"Rogue",
    u"\u5e7b\u5f71\u732b": u"Kitty Pryde",
    u"\u52b3\u62c9\xb7\u91d1\u5c3c": u"Laura Kinney",
    u"\u52b3\u62c9": u"X-23",
    u"\u7ea2\u5766\u514b": u"Juggernaut",
    u"\u706b\u4eba": u"Pyro",
    u"\u5251\u9f7f\u864e": u"Sabretooth",
    u"\u87fe\u870d\u4eba": u"Toad",
    u"\u6b7b\u4ea1\u5973": u"Lady Deathstrike",
    u"\u7ea2\u9b54\u9b3c": u"Azazel",
    u"\u9739\u96f3\u706b": u"Human Torch",
    u"\u5f3a\u5c3c\xb7\u65af\u6258\u59c6": u"Human Torch",
    u"\u795e\u5947\u5148\u751f": u"Mister Fantastic",
    u"\u91cc\u5fb7\xb7\u7406\u67e5\u5179": u"Mister Fantastic",
    u"\u9690\u5f62\u5973\u4fa0": u"Invisible Woman",
    u"\u82cf\u73ca\xb7\u65af\u901a": u"Invisible Woman",
    u"\u77f3\u5934\u4eba": u"The Thing",
    u"\u672c\xb7\u683c\u745e\u59c6": u"The Thing",
    u"\u7eb3\u6469": u"Namor",
    u"\u9ed1\u8760\u738b": u"Black Bolt",
    u"\u6c34\u6676": u"Crystal",
    u"\u7834\u5251\u8005": u"Lockjaw",
    u"\u7834\u4f24\u98ce": u"Lockjaw",
    u"\u6c34\u6676\u4e0e\u7834\u5251\u8005": u"Crystal & Lockjaw",
    u"\u591c\u9b54\u4fa0": u"Daredevil",
    u"\u8d85\u80c6\u4fa0": u"Daredevil",
    u"\u9a6c\u7279\xb7\u9ed8\u591a\u514b": u"Daredevil",
    u"\u60e9\u7f5a\u8005": u"The Punisher",
    u"\u5f17\u5170\u514b\xb7\u5361\u65af\u7279": u"The Punisher",
    u"\u94c1\u62f3": u"Iron Fist",
    u"\u4e39\u5c3c\xb7\u5170\u5fb7": u"Iron Fist",
    u"\u5362\u514b\xb7\u51ef\u5947": u"Luke Cage",
    u"\u827e\u4e3d\u5361": u"Elektra",
    u"\u91d1\u5e76": u"Kingpin",
    u"\u9776\u773c": u"Bullseye",
    u"\u6597\u7bf7\u4e0e\u5315\u9996": u"Cloak & Dagger",
    u"\u6597\u7bf7": u"Cloak",
    u"\u5315\u9996": u"Dagger",
    u"\u6b7b\u4f8d": u"Deadpool",
    u"\u97e6\u5fb7\xb7\u5a01\u5c14\u900a": u"Deadpool",
    u"\u97e6\u5fb7": u"Deadpool",
    u"\u6b7b\u4f8d\u5973\u4fa0": u"Lady Deadpool",
    u"\u5e05\u4f8d": u"Nicepool",
    u"\u72d7\u4f8d": u"Dogpool",
    u"\u5934\u4f8d": u"Headpool",
    u"\u5c0f\u6b7b\u4f8d": u"Kidpool",
    u"\u5a74\u513f\u6b7b\u4f8d": u"Babypool",
    u"\u725b\u4ed4\u6b7b\u4f8d": u"Cowboy Deadpool",
    u"\u4f0a\u5361\u6d1b\u65af": u"Ikaris",
    u"\u4f0a\u5361\u91cc\u65af": u"Ikaris",
    u"\u8482\u5a1c": u"Thena",
    u"\u745f\u897f": u"Sersi",
    u"\u5409\u5c14\u4f3d\u7f8e\u4ec0": u"Gilgamesh",
    u"\u91d1\u6208": u"Kingo",
    u"\u9a6c\u5361\u91cc": u"Makkari",
    u"\u6cd5\u65af\u6258\u65af": u"Phastos",
    u"\u8bf8\u514b": u"Druig",
    u"\u963f\u8d3e\u514b": u"Ajak",
    u"\u6c34\u7cbe": u"Sprite",
    u"\u6a21\u4eff\u5927\u5e08": u"Taskmaster",
    u"\u9ed1\u9a91\u58eb": u"Black Knight",
    u"\u6234\u6069\xb7\u60e0\u7279\u66fc": u"Dane Whitman",
    u"\u5c1a\u6c14": u"Shang-Chi",
    u"\u6587\u6b66": u"Wenwu",
    u"\u6218\u864e": u"War Tiger",
    u"\u6d6a": u"Wave",
    u"\u51b0\u6708\u82b1\u96ea": u"Luna Snow",
    u"\u96ea\u7199": u"Luna Snow",
    u"\u6708\u661f": u"Moonstar",
    u"\u4e39\u59ae\u5c14\xb7\u6708\u661f": u"Dani Moonstar",
    u"\u5e7d\u7075": u"Ghost",
    u"\u5e9e\u59c6": u"Pym",
    u"\u6bc1\u706d\u535a\u58eb": u"Doctor Doom",
    u"\u5f81\u670d\u8005\u5eb7": u"Kang the Conqueror",
    u"\u7ea2\u9ab7\u9ac5": u"Red Skull",
    u"\u6cfd\u83ab\u7537\u7235": u"Baron Zemo",
    u"\u4ea4\u53c9\u9aa8": u"Crossbones",
    u"\u9b54\u591a\u5ba2": u"MODOK",
    u"\u683c\u5c14": u"Gorr",
    u"\u5c60\u795e\u8005\u683c\u5c14": u"Gorr the God Butcher",
    u"\u5b99\u65af": u"Zeus",
    u"\u5168\u90e8\u82f1\u96c4": u"All Heroes",
    u"\u5168\u90e8\u7c7b\u578b": u"All Types",
    u"\u5168\u90e8": u"All",
    u"\u5e38\u7528\u82f1\u96c4": u"Frequent Heroes",
    u"\u5e38\u7528": u"Frequent",
    u"\u6bcf\u5468\u9650\u514d": u"Weekly Free",
    u"\u9650\u514d": u"Free",
    u"\u719f\u7ec3\u5ea6": u"Proficiency",
    u"\u5df2\u62e5\u6709": u"Owned",
    u"\u672a\u62e5\u6709": u"Not Owned",
    u"\u82f1\u96c4\u5b9a\u4f4d": u"Hero Role",
    u"\u5b9a\u4f4d": u"Role",
    u"\u96be\u5ea6": u"Difficulty",
    u"\u4e0a\u624b\u96be\u5ea6": u"Difficulty",
    u"\u6218\u6597\u578b": u"Fighter",
    u"\u6218\u6597": u"Fighter",
    u"\u80fd\u91cf\u578b": u"Energy",
    u"\u80fd\u91cf": u"Energy",
    u"\u5c04\u624b\u578b": u"Marksman",
    u"\u5c04\u624b": u"Marksman",
    u"\u523a\u5ba2\u578b": u"Assassin",
    u"\u523a\u5ba2": u"Assassin",
    u"\u6e38\u8d70\u578b": u"Assassin",
    u"\u6e38\u8d70": u"Assassin",
    u"\u5766\u514b\u578b": u"Tank",
    u"\u5766\u514b": u"Tank",
    u"\u8f85\u52a9\u578b": u"Support",
    u"\u8f85\u52a9": u"Support",
    u"\u6f2b\u5a01\u8d85\u7ea7\u6218\u4e89": u"Marvel Super War",
    u"\u6f2b\u5a01\u7279\u5de5": u"Marvel Agent",
    u"\u74e6\u574e\u8fbe\u6218\u573a": u"Wakanda Battlefield",
    u"\u74e6\u574e\u8fbe": u"Wakanda",
    u"\u5feb\u901f\u6e38\u620f": u"Quick Match",
    u"\u6392\u4f4d\u8d5b": u"Ranked Match",
    u"\u6392\u4f4d": u"Ranked",
    u"\u4eba\u673a\u5bf9\u6218": u"VS A.I.",
    u"\u4eba\u673a": u"VS A.I.",
    u"\u5a31\u4e50\u8d5b": u"Arcade",
    u"\u5a31\u4e50": u"Arcade",
    u"\u5f00\u623f\u95f4": u"Custom Room",
    u"\u521b\u5efa\u623f\u95f4": u"Create Room",
    u"\u52a0\u5165\u623f\u95f4": u"Join Room",
    u"\u82f1\u96c4\u8bad\u7ec3\u8425": u"Training Camp",
    u"\u8bad\u7ec3\u8425": u"Training",
    u"\u81ea\u7531\u8bad\u7ec3": u"Free Training",
    u"\u65b0\u624b\u8bad\u7ec3": u"Tutorial",
    u"\u5bf9\u6218": u"Battle",
    u"\u5339\u914d": u"Match",
    u"\u82f1\u96c4": u"Heroes",
    u"\u88c5\u5907": u"Equipment",
    u"\u5907\u6218": u"Preparation",
    u"\u5546\u57ce": u"Store",
    u"\u6d3b\u52a8": u"Events",
    u"\u6218\u7ee9": u"Stats",
    u"\u89c2\u6218": u"Spectate",
    u"\u90ae\u4ef6": u"Mail",
    u"\u597d\u53cb": u"Friends",
    u"\u8bbe\u7f6e": u"Settings",
    u"\u4efb\u52a1": u"Quests",
    u"\u65e5\u5e38\u4efb\u52a1": u"Daily Quests",
    u"\u6210\u957f\u4efb\u52a1": u"Growth Quests",
    u"\u80cc\u5305": u"Inventory",
    u"\u9053\u5177": u"Items",
    u"\u516c\u4f1a": u"Guild",
    u"\u8054\u76df": u"Alliance",
    u"\u6392\u884c\u699c": u"Leaderboard",
    u"\u6392\u884c": u"Leaderboard",
    u"\u6210\u5c31": u"Achievements",
    u"\u901a\u884c\u8bc1": u"Battle Pass",
    u"\u8d5b\u5b63\u901a\u884c\u8bc1": u"Season Pass",
    u"\u82f1\u96c4\u56fe\u9274": u"Hero Gallery",
    u"\u56fe\u9274": u"Gallery",
    u"\u76ae\u80a4\u56fe\u9274": u"Skin Gallery",
    u"\u76ae\u80a4": u"Skins",
    u"\u5916\u89c2": u"Cosmetics",
    u"\u7279\u5de5\u6863\u6848": u"Agent Profile",
    u"\u4e2a\u4eba\u4fe1\u606f": u"Personal Info",
    u"\u4e2a\u4eba\u4e3b\u9875": u"Profile",
    u"\u5386\u53f2\u6218\u7ee9": u"Match History",
    u"\u8363\u8a89": u"Honor",
    u"\u4fe1\u8a89\u79ef\u5206": u"Reputation",
    u"\u4fe1\u8a89\u7b49\u7ea7": u"Reputation Level",
    u"\u80fd\u6e90\u6838\u5fc3": u"Energy Core",
    u"\u6218\u672f\u652f\u63f4": u"Tactical Support",
    u"\u6cd5\u672f": u"Tactics",
    u"\u53ec\u5524\u5e08\u6280\u80fd": u"Spells",
    u"\u5feb\u6377\u7528\u8bed": u"Quick Chat",
    u"\u5c40\u5185\u5feb\u6377\u6d88\u606f": u"Quick Chat",
    u"\u914d\u7f6e": u"Loadout",
    u"\u65b9\u6848": u"Plan",
    u"\u63a8\u8350\u65b9\u6848": u"Recommended",
    u"\u5927\u795e\u65b9\u6848": u"Pro Build",
    u"\u9ed8\u8ba4\u65b9\u6848": u"Default Plan",
    u"\u81ea\u5b9a\u4e49\u65b9\u6848": u"Custom Plan",
    u"\u88c5\u5907\u63a8\u8350": u"Recommended Gear",
    u"\u6838\u5fc3\u88c5\u5907": u"Core Items",
    u"\u901a\u7528\u7206\u53d1": u"General Burst",
    u"\u6301\u7eed\u4f5c\u6218": u"Sustained Combat",
    u"\u9632\u62a4\u51b7\u5374": u"Defense Cooldown",
    u"\u751f\u5b58\u652f\u63f4": u"Survival Support",
    u"\u6280\u80fd\u63cf\u8ff0": u"Skill Description",
    u"\u6280\u80fd": u"Skills",
    u"\u88ab\u52a8\u6280\u80fd": u"Passive Skill",
    u"\u88ab\u52a8": u"Passive",
    u"\u4e3b\u52a8\u6280\u80fd": u"Active Skill",
    u"\u4e3b\u52a8": u"Active",
    u"\u51b7\u5374\u65f6\u95f4": u"Cooldown",
    u"\u6280\u80fd\u51b7\u5374": u"Skill CD",
    u"\u6d88\u8017": u"Cost",
    u"\u7269\u7406\u653b\u51fb": u"Physical Atk",
    u"\u80fd\u91cf\u5f3a\u5ea6": u"Energy Power",
    u"\u7269\u7406\u9632\u5fa1": u"Physical Def",
    u"\u80fd\u91cf\u6297\u6027": u"Energy Resist",
    u"\u7269\u7406\u4f24\u5bb3": u"Physical DMG",
    u"\u80fd\u91cf\u4f24\u5bb3": u"Energy DMG",
    u"\u771f\u5b9e\u4f24\u5bb3": u"True DMG",
    u"\u6700\u5927\u751f\u547d": u"Max HP",
    u"\u5f53\u524d\u751f\u547d": u"Current HP",
    u"\u751f\u547d\u503c": u"HP",
    u"\u6cd5\u529b\u503c": u"Mana",
    u"\u80fd\u91cf\u503c": u"Energy",
    u"\u51b7\u5374\u7f29\u51cf": u"CDR",
    u"\u66b4\u51fb\u7387": u"Crit Rate",
    u"\u66b4\u51fb\u4f24\u5bb3": u"Crit DMG",
    u"\u653b\u51fb\u901f\u5ea6": u"Atk Speed",
    u"\u79fb\u52a8\u901f\u5ea6": u"Move Speed",
    u"\u79fb\u901f": u"Move Speed",
    u"\u7269\u7406\u7a7f\u900f\u7387": u"Physical PEN %",
    u"\u80fd\u91cf\u7a7f\u900f\u7387": u"Energy PEN %",
    u"\u7269\u7406\u7a7f\u900f": u"Physical PEN",
    u"\u80fd\u91cf\u7a7f\u900f": u"Energy PEN",
    u"\u751f\u547d\u56de\u590d": u"HP Regen",
    u"\u7269\u7406\u5438\u8840": u"Physical Lifesteal",
    u"\u80fd\u91cf\u5438\u8840": u"Energy Lifesteal",
    u"\u5438\u8840": u"Lifesteal",
    u"\u97e7\u6027": u"Tenacity",
    u"\u5c04\u7a0b": u"Range",
    u"\u653b\u51fb\u8ddd\u79bb": u"Atk Range",
    u"\u65bd\u6cd5\u8ddd\u79bb": u"Cast Range",
    u"\u5f00\u59cb\u6e38\u620f": u"Start Game",
    u"\u5f00\u59cb\u5339\u914d": u"Start Match",
    u"\u8fdb\u5165\u6e38\u620f": u"Enter Game",
    u"\u5f00\u59cb": u"Start",
    u"\u786e\u5b9a\u9009\u62e9": u"Lock In",
    u"\u6362\u4eba": u"Switch Hero",
    u"\u786e\u8ba4": u"Confirm",
    u"\u786e\u5b9a": u"Confirm",
    u"\u53d6\u6d88": u"Cancel",
    u"\u8fd4\u56de\u5927\u5385": u"Return to Lobby",
    u"\u8fd4\u56de": u"Back",
    u"\u5173\u95ed": u"Close",
    u"\u9000\u51fa\u6e38\u620f": u"Exit Game",
    u"\u9000\u51fa": u"Exit",
    u"\u9009\u62e9": u"Select",
    u"\u63a8\u8350": u"Recommend",
    u"\u9ed8\u8ba4": u"Default",
    u"\u8d2d\u4e70": u"Buy",
    u"\u4f7f\u7528": u"Use",
    u"\u4f69\u6234": u"Equip",
    u"\u5378\u4e0b": u"Unequip",
    u"\u4fdd\u5b58": u"Save",
    u"\u91cd\u7f6e": u"Reset",
    u"\u7f16\u8f91": u"Edit",
    u"\u5347\u7ea7": u"Upgrade",
    u"\u89e3\u9501": u"Unlock",
    u"\u5206\u4eab": u"Share",
    u"\u4e00\u952e\u9886\u53d6": u"Claim All",
    u"\u9886\u53d6": u"Claim",
    u"\u514d\u8d39": u"Free",
    u"\u5df2\u88c5\u5907": u"Equipped",
    u"\u5df2\u4f7f\u7528": u"In Use",
    u"\u5df2\u4fdd\u5b58": u"Saved",
    u"\u6210\u529f": u"Success",
    u"\u5931\u8d25": u"Defeat",
    u"\u80dc\u5229": u"Victory",
    u"\u5e73\u5c40": u"Draw",
    u"\u7ee7\u7eed": u"Continue",
    u"\u518d\u6765\u4e00\u5c40": u"Play Again",
    u"\u793e\u4ea4": u"Social",
    u"\u57fa\u7840\u8bbe\u7f6e": u"Basic Settings",
    u"\u64cd\u4f5c\u8bbe\u7f6e": u"Controls",
    u"\u97f3\u6548\u8bbe\u7f6e": u"Audio",
    u"\u753b\u8d28\u8bbe\u7f6e": u"Graphics",
    u"\u754c\u9762\u8bbe\u7f6e": u"UI Settings",
    u"\u7f51\u7edc\u8bca\u65ad": u"Network Diagnostic",
    u"\u9ad8\u5e27\u7387": u"High Frame Rate",
    u"\u5e27\u7387": u"Frame Rate",
    u"\u8d85\u9ad8": u"Ultra",
    u"\u6781\u9ad8": u"Extreme",
    u"\u9ad8": u"High",
    u"\u4e2d": u"Medium",
    u"\u4f4e": u"Low",
    u"\u5f00\u542f": u"On",
    u"\u4e3b\u97f3\u91cf": u"Master Volume",
    u"\u97f3\u91cf": u"Volume",
    u"\u97f3\u4e50": u"Music",
    u"\u97f3\u6548": u"SFX",
    u"\u8bed\u97f3": u"Voice",
    u"\u9707\u52a8\u53cd\u9988": u"Haptic Feedback",
    u"\u9707\u52a8": u"Vibration",
    u"\u5185\u8d2d": u"In-App Purchase",
    u"\u5145\u503c": u"Recharge",
    u"\u5339\u914d\u4e2d": u"Matching...",
    u"\u5339\u914d\u6210\u529f": u"Match Found",
    u"\u8bf7\u786e\u8ba4": u"Please Confirm",
    u"\u7b49\u5f85\u5176\u4ed6\u73a9\u5bb6": u"Waiting for Players...",
    u"\u52a0\u8f7d\u4e2d": u"Loading...",
    u"\u51c6\u5907\u4e2d": u"Preparing...",
    u"\u8bf7\u9009\u62e9\u82f1\u96c4": u"Select a Hero",
    u"\u53cc\u65b9\u9009\u4eba": u"Hero Selection",
    u"\u5bf9\u6218\u5f00\u59cb": u"Battle Begins",
    u"\u51fb\u6740": u"Kill",
    u"\u88ab\u51fb\u6740": u"Slain",
    u"\u52a9\u653b": u"Assist",
    u"\u9996\u6740": u"First Blood",
    u"\u53cc\u6740": u"Double Kill",
    u"\u4e09\u8fde\u51b3\u80dc": u"Triple Kill",
    u"\u56db\u8fde\u8d85\u51e1": u"Quadra Kill",
    u"\u4e94\u8fde\u7edd\u4e16": u"Penta Kill",
    u"\u5927\u6740\u7279\u6740": u"Killing Spree",
    u"\u65e0\u4eba\u80fd\u6321": u"Unstoppable",
    u"\u8d85\u795e": u"Godlike",
    u"\u56e2\u706d": u"Ace",
    u"\u6467\u6bc1\u9632\u5fa1\u5854": u"Tower Destroyed",
    u"\u654c\u65b9\u9632\u5fa1\u5854\u88ab\u6467\u6bc1": u"Enemy Tower Destroyed",
    u"\u8fdb\u653b": u"Attack",
    u"\u64a4\u9000": u"Retreat",
    u"\u96c6\u5408": u"Assemble",
    u"\u53d1\u8d77\u8fdb\u653b": u"Initiate Attack",
    u"\u5f00\u59cb\u64a4\u9000": u"Fall Back",
    u"\u8bf7\u6c42\u96c6\u5408": u"Request Rally",
    u"\u5a01\u5ec9": u"William",
    u"\u8d1d\u514b": u"Baker",
    u"\u9a6c\u5c14\u79d1": u"Marko",
    u"\u5e03\u9c81\u65af": u"Bruce",
    u"\u514b\u6797\u7279": u"Clint",
    u"\u76ae\u7279\u7f57": u"Pietro",
    u"\u53f2\u8482\u82ac": u"Stephen",
    u"\u65af\u79d1\u7279": u"Scott",
    u"\u7f57\u8fea": u"Rhodey",
    u"\u5c71\u59c6": u"Sam",
    u"\u5df4\u57fa": u"Bucky",
    u"\u5361\u7f57\u5c14": u"Carol",
    u"\u7279\u67e5\u62c9": u"T'Challa",
    u"\u8212\u91cc": u"Shuri",
    u"\u76ae\u7279": u"Peter",
    u"\u8fc8\u5c14\u65af": u"Miles",
    u"\u683c\u6e29": u"Gwen",
    u"\u7b80": u"Jane",
    u"\u5546\u5e97": u"Store",
    u"\u5546\u573a": u"Store",
    u"\u6863\u6848": u"Profile",
    u"\u7279\u5de5": u"Agent",
    u"\u8865\u7ed9": u"Supply",
    u"\u519b\u68b0": u"Armory",
    u"\u519b\u5907": u"Armory",
    u"\u8654\u8bda\u70c8\u7130": u"Devout Flame",
    u"\u96f7\u795e3\uff1a\u8bf8\u795e\u9ec4\u660f": u"Thor: Ragnarok",
    u"\u8bf8\u795e\u9ec4\u660f": u"Ragnarok",
    u"\u5e0c\u8299\u5973\u58eb": u"Lady Sif",
    u"\u5973\u58eb": u"Lady",
    u"\u7ec8\u5c40\u4e4b\u6218": u"Endgame",
    u"\u65e0\u9650\u6218\u4e89": u"Infinity War",
    u"\u82f1\u96c4\u5185\u6218": u"Civil War",
    u"\u88c5\u7532": u"Armor",
    u"\u6218\u7532": u"Armor",
    u"\u7ecf\u5178": u"Classic",
    u"\u884c\u661f\u541e\u566e\u8005": u"Galactus",
    u"\u795e\u5a01": u"Mighty",
    u"\u89c9\u9192": u"Awakening",
    u"\u590d\u4ec7\u8005": u"Avengers",
    u"\u5149\u8f89": u"Radiance",
    u"\u672a\u6765": u"Future",
    u"\u6697\u9ed1": u"Dark",
    u"\u7ec8\u6781": u"Ultimate",
    u"\u539f\u7248": u"Original",
    u"\u9ed1\u591c": u"Night",
    u"\u7279\u5de5\u6863\u6848": u"Agent Profile",
    u"\u5c40\u5916\u88c5\u5907": u"Gear Loadout",
    u"\u82f1\u96c4\u5907\u6218": u"Preparation",
    u"\u5bf9\u6218\u5339\u914d": u"Matchmaking",
}

_SORTED_ZH_KEYS = tuple(sorted(_ZH_TO_EN.keys(), key=lambda k: -len(k)))

try:
    _UNICODE_TYPE = unicode
    _PY2 = True
except NameError:
    _UNICODE_TYPE = str
    _PY2 = False


def _to_unicode(val):
    if val is None:
        return u""
    if isinstance(val, _UNICODE_TYPE):
        return val
    if hasattr(val, "decode"):
        try:
            return val.decode("utf-8")
        except Exception:
            try:
                return val.decode("gbk")
            except Exception:
                try:
                    return val.decode("latin1", "replace")
                except Exception:
                    pass
    try:
        return _UNICODE_TYPE(val)
    except Exception:
        return u""


def _to_str(val):
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if hasattr(val, "encode"):
        try:
            res = val.encode("utf-8")
            if isinstance(res, str):
                return res
        except Exception:
            pass
    if hasattr(val, "decode"):
        try:
            return val.decode("utf-8")
        except Exception:
            pass
    try:
        return str(val)
    except Exception:
        return ""


def load_external_translations():
    """Load external English translations from loc_en.json if present on sdcard."""
    global _SORTED_ZH_KEYS
    import json
    paths = (
        "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/loc_en.json",
        "/storage/emulated/0/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/loc_en.json",
        "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/loc_en.txt",
    )
    loaded = 0
    for p in paths:
        if os.path.isfile(p):
            try:
                with open(p, "rb") as f:
                    content = f.read()
                if p.endswith(".json"):
                    data = json.loads(content)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            uk = _to_unicode(k)
                            uv = _to_unicode(v)
                            if uk and uv:
                                _ZH_TO_EN[uk] = uv
                                loaded += 1
                elif p.endswith(".txt"):
                    for line in content.splitlines():
                        line = line.strip()
                        if line and "\t" in line:
                            parts = line.split("\t", 1)
                            uk = _to_unicode(parts[0].strip())
                            uv = _to_unicode(parts[1].strip())
                            if uk and uv:
                                _ZH_TO_EN[uk] = uv
                                loaded += 1
                if loaded > 0:
                    log("Loaded %d additional translations from %s" % (loaded, p))
                    _SORTED_ZH_KEYS = tuple(sorted(_ZH_TO_EN.keys(), key=lambda k: -len(k)))
                    break
            except Exception:
                log("Error loading external translation from %s:" % p, traceback.format_exc())


_dump_completed = False


def _write_dump_summary(diagnostic_info, dump_result, table_stats, total_strings, total_tables):
    import json
    for target_dir in DOC_DIRS:
        try:
            if not os.path.isdir(target_dir):
                try:
                    os.makedirs(target_dir)
                except Exception:
                    pass

            summary_path = os.path.join(target_dir, "dump_summary.txt")
            with open(summary_path, "wb") as f:
                f.write("=== MARVEL SUPER WAR PROTO DUMP SUMMARY ===\n")
                if total_strings > 0:
                    f.write("Status: SUCCESS - Strings extracted!\n")
                else:
                    f.write("Status: IN PROGRESS / TABLES EMPTY AT CALL TIME\n")
                f.write("Total unique Chinese strings: %d\n" % total_strings)
                f.write("Total tables scanned: %d\n" % total_tables)
                if table_stats:
                    f.write("\n--- Extracted Table Details ---\n")
                    for t, cnt in sorted(table_stats.items(), key=lambda x: -x[1]):
                        f.write("- %s: %d Chinese text entries\n" % (t, cnt))
                f.write("\n--- Diagnostic Log ---\n")
                for line in diagnostic_info:
                    try:
                        if isinstance(line, _UNICODE_TYPE):
                            line = line.encode("utf-8")
                        f.write(str(line) + "\n")
                    except Exception:
                        pass

            log("[DUMP] Written dump_summary.txt to %s" % target_dir)

            if dump_result and total_strings > 0:
                json_path = os.path.join(target_dir, "gdata_dump.json")
                txt_path = os.path.join(target_dir, "unique_chinese_strings.txt")

                try:
                    with open(json_path, "wb") as f:
                        f.write(json.dumps(dump_result, ensure_ascii=False, indent=2).encode("utf-8"))
                    log("[DUMP] Successfully saved JSON to %s" % json_path)
                except Exception:
                    log("[DUMP] Failed to save JSON:", traceback.format_exc())

                try:
                    with open(txt_path, "wb") as f:
                        for s in dump_result["unique_strings"]:
                            if isinstance(s, _UNICODE_TYPE):
                                s = s.encode("utf-8")
                            f.write(s + "\n")
                    log("[DUMP] Successfully saved TXT to %s" % txt_path)
                except Exception:
                    log("[DUMP] Failed to save TXT:", traceback.format_exc())

            break
        except Exception:
            log("[DUMP] Error writing summary to %s: %s" % (target_dir, traceback.format_exc()))


def dump_all_game_strings():
    """Extract all Chinese game text (skills, items, heroes, descriptions) to JSON."""
    global _dump_completed
    if _dump_completed:
        return

    diag_log = []
    def dlog(msg):
        log("[DUMP] " + str(msg))
        diag_log.append(str(msg))

    dlog("Starting in-engine Proto Table String Dumper...")

    try:
        import game_env
        inst = game_env.GetInstance()
        dlog("game_env.GetInstance(): %s" % repr(inst))
        if not inst:
            dlog("game_env instance is None.")
            _write_dump_summary(diag_log, None, None, 0, 0)
            return

        gdata = getattr(inst, "game_data", None)
        if not gdata:
            dlog("inst.game_data is None. Checking alternatives...")
            try:
                import both.hall_util as hall_util
                gdata = getattr(hall_util, "gdata", None)
            except Exception:
                pass

        if not gdata:
            dlog("gdata could not be found.")
            _write_dump_summary(diag_log, None, None, 0, 0)
            return

        dlog("Found gdata: %s (type: %s)" % (repr(gdata), type(gdata)))

        all_tables = {}

        # 1. Attribute dicts on gdata
        for attr in ("_all_proto", "_protos", "protos", "proto_dict", "_proto_dict", "data", "_data", "_proto_data", "all_proto"):
            d = getattr(gdata, attr, None)
            if d is not None:
                dlog("Checking gdata.%s (type: %s)" % (attr, type(d)))
                if isinstance(d, dict):
                    for k, v in d.items():
                        if k not in all_tables:
                            all_tables[k] = v
                elif hasattr(d, "keys") and callable(d.keys):
                    try:
                        for k in d.keys():
                            if k not in all_tables:
                                all_tables[k] = d[k]
                    except Exception:
                        pass

        # 2. Known proto names via GetAllProtoByName / FindProto / GetProto
        KNOWN_PROTOS = (
            "SkillDescProto", "SkillProto", "EquipProto", "EquipSchemeProto",
            "HeroProto", "HeroBasicProto", "HeroSkinProto", "HeroInfoProto",
            "HeroCardProto", "HeroDataProto", "HeroBaseProto", "CoreProto",
            "EnergyCoreProto", "TacticProto", "SpellProto", "BuffProto",
            "AIMapProto", "MapInfoProto", "MapRuleProto", "MatchUIProto",
            "AchievementProto", "TaskProto", "ActivityProto", "ShopProto", "GoodsProto",
            "TalentProto", "HeroTalentProto", "SkillEffectProto", "SkinProto",
        )
        for name in KNOWN_PROTOS:
            for fn_name in ("GetAllProtoByName", "FindProto", "GetProto", "GetProtoByName", "FindProtoByName", "GetTable"):
                m = getattr(gdata, fn_name, None)
                if callable(m):
                    try:
                        p = m(name)
                        if p is not None:
                            all_tables[name] = p
                            break
                    except Exception:
                        pass

        dlog("Total proto tables to scan: %d (%s)" % (len(all_tables), ", ".join(list(all_tables.keys())[:15])))

        zh_re = re.compile(u'[\u4e00-\u9fff]')
        dump_result = {
            "version": "1.0",
            "tables": {},
            "unique_strings": []
        }
        unique_set = set()
        table_stats = {}

        fields_to_check = (
            "name", "skill_name", "hero_name", "desc", "description", "describe",
            "show_name", "skin_name", "title", "short_name", "story", "tips",
            "intro", "effect_desc", "passive_desc", "special_desc", "simple_desc",
            "skill_desc", "talent_desc", "core_desc", "detail", "sub_title", "explain"
        )

        for tname, tbl in all_tables.items():
            t_strings = {}
            rows = []

            # Method A: .items()
            if hasattr(tbl, "items") and callable(tbl.items):
                try:
                    rows = list(tbl.items())
                except Exception:
                    rows = []

            # Method B: .keys()
            if not rows and hasattr(tbl, "keys") and callable(tbl.keys):
                try:
                    for k in tbl.keys():
                        try:
                            rows.append((k, tbl[k]))
                        except Exception:
                            pass
                except Exception:
                    pass

            # Method C: iteration
            if not rows:
                try:
                    for k in tbl:
                        try:
                            rows.append((k, tbl[k]))
                        except Exception:
                            pass
                except Exception:
                    pass

            # Method D: .values()
            if not rows and hasattr(tbl, "values") and callable(tbl.values):
                try:
                    rows = list(enumerate(tbl.values()))
                except Exception:
                    pass

            if not rows:
                continue

            for row_id, row in rows:
                if row is None:
                    continue
                row_dict = {}

                keys_to_try = set(fields_to_check)
                if isinstance(row, dict):
                    keys_to_try.update(row.keys())
                elif hasattr(row, "keys") and callable(row.keys):
                    try:
                        keys_to_try.update(list(row.keys()))
                    except Exception:
                        pass
                if hasattr(row, "__dict__"):
                    keys_to_try.update(list(row.__dict__.keys()))

                try:
                    for a in dir(row):
                        if not a.startswith("_"):
                            keys_to_try.add(a)
                except Exception:
                    pass

                for f in keys_to_try:
                    val = None
                    try:
                        val = row[f]
                    except Exception:
                        pass
                    if val is None:
                        try:
                            val = getattr(row, f, None)
                        except Exception:
                            pass
                    if not val:
                        continue

                    if isinstance(val, (_UNICODE_TYPE, bytes if _PY2 else str)):
                        u_val = _to_unicode(val)
                        if u_val and zh_re.search(u_val):
                            clean_text = u_val.strip()
                            if clean_text:
                                row_dict[str(f)] = clean_text
                                unique_set.add(clean_text)
                    elif isinstance(val, (list, tuple)):
                        for elem in val:
                            if isinstance(elem, (_UNICODE_TYPE, bytes if _PY2 else str)):
                                u_elem = _to_unicode(elem)
                                if u_elem and zh_re.search(u_elem):
                                    clean_text = u_elem.strip()
                                    if clean_text:
                                        unique_set.add(clean_text)
                    elif isinstance(val, dict):
                        for sub_k, sub_v in val.items():
                            if isinstance(sub_v, (_UNICODE_TYPE, bytes if _PY2 else str)):
                                u_sub = _to_unicode(sub_v)
                                if u_sub and zh_re.search(u_sub):
                                    clean_text = u_sub.strip()
                                    if clean_text:
                                        unique_set.add(clean_text)

                if row_dict:
                    t_strings[str(row_id)] = row_dict

            if t_strings:
                dump_result["tables"][str(tname)] = t_strings
                table_stats[str(tname)] = len(t_strings)
                dlog("Table %s: extracted %d items with Chinese text" % (tname, len(t_strings)))

        dlog("Scan finished. Total unique strings: %d across %d tables" % (len(unique_set), len(table_stats)))

        dump_result["unique_strings"] = sorted(list(unique_set), key=lambda x: -len(x))
        dump_result["total_unique_strings"] = len(unique_set)
        dump_result["table_counts"] = table_stats

        _write_dump_summary(diag_log, dump_result, table_stats, len(unique_set), len(all_tables))

        if len(unique_set) > 0:
            _dump_completed = True
            log("[DUMP] DUMP COMPLETED SUCCESSFULLY! %d unique strings saved." % len(unique_set))

    except Exception:
        err_msg = traceback.format_exc()
        dlog("FATAL ERROR during dump_all_game_strings: " + err_msg)
        _write_dump_summary(diag_log, None, None, 0, 0)


def _translate(s):
    """Return the English equivalent of a Chinese string, or the original."""
    if not s:
        return s
    uni_s = _to_unicode(s)
    if not uni_s:
        return s

    if uni_s in _ZH_TO_EN:
        return _ZH_TO_EN[uni_s]

    stripped = uni_s.strip()
    if stripped in _ZH_TO_EN:
        rep = _ZH_TO_EN[stripped]
        return uni_s.replace(stripped, rep)

    # Whitespace-tolerant match (handles spaced Chinese characters on buttons)
    no_space = re.sub(r'[\s\u3000\u00a0\r\n]+', '', uni_s)
    if no_space in _ZH_TO_EN:
        return _ZH_TO_EN[no_space]

    modified = False
    for zh in _SORTED_ZH_KEYS:
        if zh in uni_s:
            uni_s = uni_s.replace(zh, _ZH_TO_EN[zh])
            modified = True

    return uni_s if modified else s


def _safe_set_text(node, setter_name, en_text):
    """Set text on a node trying UTF-8 str and unicode, single and dual-arg."""
    s = getattr(node, setter_name, None)
    if not callable(s):
        return False
    en_s = _to_str(en_text)
    en_u = _to_unicode(en_text)
    for cand in (en_s, en_u):
        try:
            s(cand)
            return True
        except TypeError:
            try:
                s(cand, False)
                return True
            except Exception:
                pass
        except Exception:
            pass
    return False


def translate_node(node):
    """Translate text content of an individual UI node or widget."""
    if not node:
        return
    for get_fn, set_fn in (
        ("getString", "setString"),
        ("GetString", "SetString"),
        ("getText", "setText"),
        ("GetText", "SetText"),
        ("getStringValue", "setText"),
        ("getStringValue", "setString"),
        ("getTitleText", "setTitleText"),
        ("GetTitleText", "SetTitleText"),
        ("getTitle", "setTitle"),
        ("GetTitle", "SetTitle"),
        ("get_text", "set_text"),
        ("get_string", "set_string"),
        ("get_title", "set_title"),
        ("getPlaceHolder", "setPlaceHolder"),
        ("getDescription", "setDescription"),
    ):
        g = getattr(node, get_fn, None)
        if callable(g):
            try:
                txt = g()
                if txt:
                    en = _translate(txt)
                    if en != txt:
                        _safe_set_text(node, set_fn, en)
            except Exception:
                pass


def translate_tree(node, depth=0, max_depth=15):
    """Recursively traverse and translate a UI node hierarchy."""
    if not node or depth > max_depth:
        return
    try:
        translate_node(node)
    except Exception:
        pass

    children = None
    for get_ch in ("getChildren", "GetChildren", "getItems", "GetItems", "getPages", "GetPages", "getCells", "GetCells"):
        cfn = getattr(node, get_ch, None)
        if callable(cfn):
            try:
                children = cfn()
                if children:
                    break
            except Exception:
                pass

    if children:
        for child in children:
            try:
                translate_tree(child, depth + 1, max_depth)
            except Exception:
                pass


def translate_panel(panel):
    """Translate all widgets on a panel or component instance."""
    if not panel:
        return
    for attr in (
        "panel", "_panel", "root_node", "_root_node", "nod_root",
        "node", "_node", "ui_node", "_ui_node", "widget", "_widget",
        "main_node", "_main_node", "view", "_view", "table_view", "_table_view",
        "list_view", "_list_view", "scroll_view", "_scroll_view",
        "content_node", "_content_node", "cell_list", "_cell_list"
    ):
        root = getattr(panel, attr, None)
        if root:
            try:
                translate_tree(root)
            except Exception:
                pass

    try:
        translate_tree(panel)
    except Exception:
        pass

    try:
        for k in dir(panel):
            if k.startswith("_"):
                continue
            val = getattr(panel, k, None)
            if val is not None and val is not panel:
                translate_node(val)
                for sub_attr in ("panel", "_panel", "root_node", "node"):
                    sub_root = getattr(val, sub_attr, None)
                    if sub_root:
                        try:
                            translate_tree(sub_root)
                        except Exception:
                            pass
    except Exception:
        pass


_ACTIVE_PANELS = []


def sweep_running_scene():
    """Traverse Cocos2d-x running scene graph to translate all currently visible nodes."""
    for mod_name in ("cc", "cocos", "cocos2d"):
        try:
            mod = __import__(mod_name)
            director = getattr(mod, "Director", None)
            if director:
                inst = getattr(director, "getInstance", None) or getattr(director, "sharedDirector", None)
                if callable(inst):
                    inst_obj = inst()
                    get_scene = getattr(inst_obj, "getRunningScene", None)
                    if callable(get_scene):
                        sc = get_scene()
                        if sc:
                            translate_tree(sc)
                            return True
        except Exception:
            pass
    return False


def hook_component_init(comp_cls):
    """Safely hook __init__ on a component class without closure-binding bugs."""
    if not comp_cls or not hasattr(comp_cls, "__init__") or hasattr(comp_cls, "_reborn_orig_init"):
        return
    orig_init = comp_cls.__init__
    comp_cls._reborn_orig_init = orig_init

    def localized_comp_init(self, *args, **kwargs):
        res = orig_init(self, *args, **kwargs)
        try:
            if self not in _ACTIVE_PANELS:
                _ACTIVE_PANELS.append(self)
            translate_panel(self)
        except Exception:
            pass
        return res

    comp_cls.__init__ = localized_comp_init


def patch_ui_localization():
    """Hook BasePanel and HallSceneComponent to auto-translate UI across all panels."""
    try:
        import ui.basepanel as basepanel
        cls = basepanel.BasePanel

        if hasattr(cls, "__init__") and not hasattr(cls, "_reborn_orig_init"):
            cls._reborn_orig_init = cls.__init__
            def localized_base_init(self, *args, **kwargs):
                res = cls._reborn_orig_init(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.__init__ = localized_base_init

        if hasattr(cls, "init_panel") and not hasattr(cls, "_reborn_orig_init_panel"):
            cls._reborn_orig_init_panel = cls.init_panel
            def localized_init_panel(self, *args, **kwargs):
                res = cls._reborn_orig_init_panel(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.init_panel = localized_init_panel

        if hasattr(cls, "show") and not hasattr(cls, "_reborn_orig_show"):
            cls._reborn_orig_show = cls.show
            def localized_show(self, *args, **kwargs):
                res = cls._reborn_orig_show(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.show = localized_show
    except Exception:
        pass

    # Hook HallSceneComponent directly for lobby menus and hero displays
    try:
        import game_ui.dialog.hall.hs_components.hall_scene_right_top as rt
        import game_ui.dialog.hall.hs_components.hall_scene_left_center as lc
        import game_ui.dialog.hall.hs_components.hall_scene_entry as entry
        import game_ui.dialog.hall.hs_components.hall_scene_hero as hh
        for mod in (rt, lc, entry, hh):
            hook_component_init(getattr(mod, "HallSceneComponent", None))
    except Exception:
        pass

    # Try all other common hall component names
    for comp_name in (
        "hall_scene_bottom", "hall_scene_left_bottom", "hall_scene_right_bottom",
        "hall_scene_bottom_left", "hall_scene_bottom_right", "hall_scene_bottom_center",
        "hall_scene_center", "hall_scene_top", "hall_scene_menu", "hall_scene_footer",
        "hall_scene_chat", "hall_scene_activity", "hall_scene_store", "hall_scene_prepare",
        "hall_scene_equip", "hall_scene_battle"
    ):
        try:
            mod = __import__("game_ui.dialog.hall.hs_components." + comp_name, fromlist=["HallSceneComponent"])
            comp = getattr(mod, "HallSceneComponent", None)
            if comp:
                hook_component_init(comp)
        except Exception:
            pass


def patch_hall_util():
    """Hook both.hall_util hero name helper functions safely."""
    try:
        import both.hall_util as hall_util
        for fn_name in ("getHeroName", "GetHeroName", "get_hero_name", "getHeroShortName", "GetHeroShortName"):
            orig_fn = getattr(hall_util, fn_name, None)
            if callable(orig_fn) and not hasattr(orig_fn, "_is_reborn_hooked"):
                def make_wrapper(f):
                    def hooked(*args, **kwargs):
                        res = f(*args, **kwargs)
                        if res:
                            en = _translate(res)
                            if isinstance(res, str):
                                return _to_str(en)
                            return _to_unicode(en)
                        return res
                    hooked._is_reborn_hooked = True
                    return hooked
                setattr(hall_util, fn_name, make_wrapper(orig_fn))
                log("Hooked hall_util." + fn_name)
    except Exception:
        log("patch_hall_util error:", traceback.format_exc())


_gdata_hero_patched = False


def patch_gdata_translations():
    """Patch hero and skin names (show_name, skin_name) across all live gdata tables."""
    global _gdata_hero_patched
    try:
        import game_env
        inst = game_env.GetInstance()
        if not inst:
            return
        gdata = getattr(inst, "game_data", None)
        if not gdata:
            return

        # Collect all available proto tables (do NOT gate on isinstance(dict) — custom
        # proto table objects may not pass that test but still support .items())
        all_tables = {}

        # Step 1: Try internal attribute dicts
        for attr in ("_all_proto", "_protos", "protos", "proto_dict", "_proto_dict", "data", "_data"):
            d = getattr(gdata, attr, None)
            if isinstance(d, dict):
                for k, v in d.items():
                    if k not in all_tables:
                        try:
                            # Just confirm it's iterable like a dict
                            iter(v)
                            all_tables[k] = v
                        except TypeError:
                            pass

        # Step 2: Force-fetch every known proto by name (always do this — don't skip
        # tables already found in step 1 because the step-1 object may be read-only
        # or of a different type than what GetAllProtoByName returns)
        KNOWN_PROTOS = (
            "HeroSkinProto", "SkinProto", "HeroProto", "HeroBasicProto",
            "HeroInfoProto", "HeroDataProto", "HeroCardProto", "HeroBaseProto",
            "EquipProto", "EquipSchemeProto", "SkillProto", "SkillDescProto",
            "MatchUIProto", "MapInfoProto", "MapRuleProto", "AIMapProto",
        )
        for name in KNOWN_PROTOS:
            for fn_name in ("GetAllProtoByName", "FindProto"):
                m = getattr(gdata, fn_name, None)
                if callable(m):
                    try:
                        p = m(name)
                        if p is not None:
                            # Prefer the directly-fetched table (likely writable)
                            all_tables[name] = p
                            break
                    except Exception:
                        pass

        fields_to_translate = ("show_name", "skin_name", "name", "hero_name",
                                "title", "short_name", "desc", "skill_name")
        total_translated = 0
        for tname, tbl in all_tables.items():
            t_count = 0
            t_err = None
            try:
                rows = list(tbl.items())
            except Exception as ex:
                # This table doesn't behave like a dict — skip it
                continue
            try:
                for row_id, row in rows:
                    if row is None:
                        continue
                    for f in fields_to_translate:
                        # Fetch the field value
                        val = None
                        try:
                            val = row[f]
                        except (KeyError, TypeError):
                            pass
                        if val is None:
                            try:
                                val = getattr(row, f, None)
                            except Exception:
                                pass
                        if not val:
                            continue
                        # Accept both str (Python 2 bytes) and unicode
                        if not isinstance(val, (_UNICODE_TYPE, bytes if _PY2 else str)):
                            continue
                        en = _translate(val)
                        # Compare decoded so bytes vs unicode mismatch doesn't cause
                        # false equality (en is always unicode or the original)
                        en_u = _to_unicode(en)
                        val_u = _to_unicode(val)
                        if en_u == val_u:
                            continue
                        # Write back — try both str and unicode, dict and attr
                        en_s = _to_str(en_u)
                        wrote = False
                        for cand in (en_s, en_u):
                            if wrote:
                                break
                            for setter in ("item_set", "dict_set", "attr_set"):
                                try:
                                    if setter == "item_set":
                                        row[f] = cand
                                    elif setter == "attr_set":
                                        setattr(row, f, cand)
                                    t_count += 1
                                    wrote = True
                                    break
                                except Exception:
                                    pass
            except Exception as ex:
                t_err = ex
            if t_count > 0 or t_err:
                msg = "Proto %s: translated %d fields" % (tname, t_count)
                if t_err:
                    msg += " (err: %s)" % repr(t_err)
                log(msg)
                total_translated += t_count


        if total_translated > 0:
            _gdata_hero_patched = True
            log("Total gdata fields translated:", total_translated)
    except Exception:
        log("patch_gdata_translations error:", traceback.format_exc())




def auto_translate_sweep():
    """Periodic background sweep to translate dynamically created UI elements."""
    global _gdata_hero_patched
    try:
        if not _gdata_hero_patched:
            patch_gdata_translations()

        # 1. Sweep entire Cocos2d-x running scene graph
        sweep_running_scene()

        # 2. Sweep gui panels
        try:
            import game_ui.gui as gui
            for attr in ("hall_ui", "cur_panel", "top_panel", "current_panel"):
                p = getattr(gui, attr, None)
                if p:
                    try:
                        translate_panel(p)
                    except Exception:
                        pass

            panels_dict = getattr(gui, "panels", None) or getattr(gui, "_panels", None)
            if isinstance(panels_dict, dict):
                for p in panels_dict.values():
                    try:
                        translate_panel(p)
                    except Exception:
                        pass
            elif isinstance(panels_dict, (list, tuple)):
                for p in panels_dict:
                    try:
                        translate_panel(p)
                    except Exception:
                        pass
        except Exception:
            pass

        # 3. Sweep all registered open panels (and safely retain them in alive list)
        global _ACTIVE_PANELS
        alive = []
        for p in _ACTIVE_PANELS:
            try:
                is_running = getattr(p, "isRunning", None)
                if callable(is_running) and not is_running():
                    continue
                translate_panel(p)
            except Exception:
                pass
            alive.append(p)
        _ACTIVE_PANELS = alive[-30:]
    except Exception:
        pass
    # Production: no self-rescheduling — sweep runs once at startup only


def check_command():
    try:
        if os.path.exists(CMD_PATH):
            with open(CMD_PATH, "rb") as f:
                code_str = f.read()
            try:
                os.remove(CMD_PATH)
            except Exception:
                pass
            log("Executing Live REPL cmd...")
            exec(compile(code_str, "cmd.py", "exec"), globals(), globals())
            log("Live REPL cmd executed successfully.")
    except Exception:
        pass
    # Production: not rescheduled (ENABLE_LIVE_REPL=False)




class EmptyData(object):
    def __init__(self):
        self.data = {}

    def get_data(self, *args, **kwargs):
        if args:
            return self.data.get(args[0], {})
        return self.data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def Get(self, key, default=None):
        return self.data.get(key, default)

    def set_data(self, *args, **kwargs):
        if len(args) >= 2:
            self.data[args[0]] = args[1]

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()


def read_player_name():
    if os.path.exists(XML_PREFS_PATH):
        try:
            with open(XML_PREFS_PATH, "rb") as f:
                content = f.read()
            m = re.search(r'<string name="player_name">([^<]+)</string>', content)
            if m:
                val = m.group(1).strip()
                if val:
                    log("Read player name from XML:", val)
                    return val.decode("utf-8")
        except Exception:
            pass

    if os.path.exists(NAME_PATH):
        try:
            with open(NAME_PATH, "rb") as f:
                raw = f.read().strip()
            if raw:
                log("Read player name from TXT:", raw)
                return raw.decode("utf-8")
        except Exception:
            pass

    return u"Marvel Agent"


def offline_noop_step(self, *args, **kwargs):
    yield None


def get_hero_ids_safe():
    # 1. From HeroSkinProto in game_data (covers all 83+ heroes per diagnostics)
    try:
        import game_env
        inst = game_env.GetInstance()
        if inst and hasattr(inst, "game_data") and inst.game_data:
            gdata = inst.game_data
            for fn in ("GetAllProtoByName", "FindProto"):
                m = getattr(gdata, fn, None)
                if callable(m):
                    try:
                        p = m("HeroSkinProto")
                        if p:
                            keys = [int(k) for k in p.keys() if str(k).isdigit() and int(str(k)) >= 1000]
                            if len(keys) >= 60:
                                log("get_hero_ids_safe: %d heroes from HeroSkinProto" % len(keys))
                                return sorted(keys)
                    except Exception:
                        pass
    except Exception:
        pass

    # 2. hall_util.getHerolistSet
    try:
        import both.hall_util as hall_util
        for arg in (None, True, 0):
            try:
                res = hall_util.getHerolistSet(arg)
                if res:
                    return [int(x) for x in res]
            except Exception:
                pass
    except Exception:
        pass

    # 3. hero_display_skin gdata
    try:
        import game_ui.dialog.hero.hero_display_skin as hds
        gdata = getattr(hds, "gdata", None)
        if gdata:
            for proto_name in ("HeroSkinProto", "HeroBasicProto"):
                proto = gdata.FindProto(proto_name)
                if proto:
                    return sorted([int(x) for x in proto.keys() if str(x).isdigit()])
    except Exception:
        pass

    return range(1001, 1085)


def patch_hero_select_ui():
    try:
        import gcore.systems.hero_select_system as hero_select_system
        cls = hero_select_system.HeroSelectSystem
        if not hasattr(cls, "_reborn_original_GetOwnHeroDict"):
            cls._reborn_original_GetOwnHeroDict = cls.GetOwnHeroDict

        def local_GetOwnHeroDict(self, player_guid, include_exp_hero=True):
            if str(player_guid) == "910001":
                return dict((int(hero_id), 1) for hero_id in self.GetSelectHeroPool())
            return cls._reborn_original_GetOwnHeroDict(self, player_guid, include_exp_hero)

        cls.GetOwnHeroDict = local_GetOwnHeroDict
        log("HeroSelectSystem local ownership patched successfully!")
    except Exception:
        log("patch_hero_select_ui error:", traceback.format_exc())


def patch_equip_shop():
    try:
        import game_ui.dialog.equip_shop.equip_main as equip_main
        if hasattr(equip_main, "Panel"):
            orig_init_panel = equip_main.Panel.init_panel
            def safe_init_panel(self, *args, **kwargs):
                try:
                    return orig_init_panel(self, *args, **kwargs)
                except Exception:
                    log("equip_main.Panel.init_panel safely handled error:", traceback.format_exc())
            equip_main.Panel.init_panel = safe_init_panel
            log("equip_main.Panel.init_panel patched successfully!")
    except Exception:
        log("patch_equip_shop error:", traceback.format_exc())


def normalize_hall_status():
    """Clear stale matchmaking/combat state after a local session."""
    try:
        import game_env
        from both import consts
        player = game_env.GetInstance().player
        if player is None:
            return
        player.statusSet(consts.EPlayerStatus.IN_HALL)
        player.statusSet(consts.EPlayerStatus.MATCH_IDLE)
        log("Hall status normalized:", repr(player.statusGetAllStatus()))
    except Exception:
        log("normalize_hall_status error:", traceback.format_exc())


def force_local_ai_fill(match_id):
    """Enable the engine's native AI filler for a selected local map/rule.

    Online MatchIdProto records such as Vibranium use is_ai_fill=False because
    the retired server used to supply ten real participants. StartLocalGame
    correctly preserves their map and hero-select rules, but only creates the
    local player. Enabling the existing MapRuleProto flag makes the native
    HeroSelectSystem create the remaining slots without changing any UI button.
    """
    try:
        import game_env
        gdata = game_env.GetInstance().game_data
        match_proto = gdata.FindProtoById("MatchIdProto", int(match_id))
        if not match_proto:
            log("force_local_ai_fill: no MatchIdProto for match_id", match_id)
            return
        map_id = match_proto.get("map_id") or match_proto.get("map_name")
        map_proto = gdata.FindProtoById("MapInfoProto", map_id) if map_id else None
        if not map_proto:
            log("force_local_ai_fill: no MapInfoProto for map_id", map_id)
            return
        rule_id = map_proto.get("rule_id")
        rule_proto = gdata.FindProtoById("MapRuleProto", rule_id) if rule_id else None
        if not rule_proto:
            log("force_local_ai_fill: no MapRuleProto for rule_id", rule_id)
            return
        slots = rule_proto.get("faction_slot_num") or ()
        total_slots = sum([int(value) for value in slots]) if isinstance(slots, (list, tuple)) else 0
        if total_slots <= 1:
            log("Single-player mode (no AI fill needed) for match_id:", match_id, "slots:", slots)
            return
        if rule_id not in _offline_rule_overrides:
            _offline_rule_overrides[rule_id] = rule_proto.get("is_ai_fill", False)
        rule_proto["is_ai_fill"] = True
        log("Native AI fill enabled for match_id:", match_id, "rule:", rule_id, "slots:", repr(slots))
    except Exception:
        log("force_local_ai_fill error:", traceback.format_exc())


def start_native_offline_match(match_id):
    try:
        match_id = int(match_id)
        import game_env
        genv = game_env.GetInstance()
        genv.is_offline_mode = True
        log("Set native offline mode for match_id:", match_id)

        normalize_hall_status()
        force_local_ai_fill(match_id)
        patch_mod_comp()
        patch_hero_select_ui()
        patch_equip_shop()

        import gvisual.visual_main as visual_main
        log("Calling native visual_main.StartLocalGame:", match_id)
        visual_main.StartLocalGame(match_id)
        return True
    except Exception:
        log("start_native_offline_match error:", traceback.format_exc())
        return False


def patch_group_proto_offline():
    """Adapt GroupProto so HallUI.CreateGameByMode bypasses retired team creation."""
    try:
        import game_env
        gdata = game_env.GetInstance().game_data
        groups = gdata.GetAllProtoByName("GroupProto")
        if groups:
            for group_id, group_info in groups.items():
                if isinstance(group_info, dict) and group_info.get("faction_count", 0) > 0:
                    group_info["faction_count"] = 0
            log("GroupProto faction_count adapted to 0 for offline match routing")
    except Exception:
        log("patch_group_proto_offline error:", traceback.format_exc())


def patch_offline_match_adapter(player=None):
    """Patch HallUI mode routing, matchmaking, and team creation for offline mode."""
    try:
        import game_ui.hall_ui as hall_ui_mod
        import game_ui.gui as gui
        if not hasattr(hall_ui_mod.HallUI, "_reborn_original_CreateGameByMode"):
            hall_ui_mod.HallUI._reborn_original_CreateGameByMode = hall_ui_mod.HallUI.CreateGameByMode

            def native_offline_create_game_by_mode(self, mode_id, invite_list=None, *args, **kwargs):
                try:
                    import game_env
                    gdata = game_env.GetInstance().game_data
                    mode_proto = gdata.FindProtoById("MatchUIProto", int(mode_id))
                    if mode_proto and mode_proto.get("match_id"):
                        native_match_id = int(mode_proto.get("match_id"))
                        log("Native mode route from HallUI:", mode_id, "-> match_id:", native_match_id)
                        return start_native_offline_match(native_match_id)
                    group_id = mode_proto.get("group_id") if mode_proto else None
                    group_proto = gdata.FindProtoById("GroupProto", group_id) if group_id else None
                    if group_proto and group_proto.get("match_id"):
                        native_match_id = int(group_proto.get("match_id"))
                        log("Native mode route from GroupProto:", group_id, "-> match_id:", native_match_id)
                        return start_native_offline_match(native_match_id)
                except Exception:
                    log("native mode resolution error:", traceback.format_exc())
                return hall_ui_mod.HallUI._reborn_original_CreateGameByMode(
                    self, mode_id, invite_list, *args, **kwargs)

            hall_ui_mod.HallUI.CreateGameByMode = native_offline_create_game_by_mode
            if hasattr(gui, "hall_ui") and gui.hall_ui:
                setattr(gui.hall_ui, "CreateGameByMode", native_offline_create_game_by_mode)
            log("HallUI.CreateGameByMode offline routing installed")

        import mb.components.player_match_logic as player_match_logic
        match_cls = player_match_logic.PlayerLogic

        def native_offline_request_match(self, match_id, match_args=None, *args, **kwargs):
            try:
                log("Native RequestMatch route:", match_id, repr(match_args))
                return start_native_offline_match(int(match_id))
            except Exception:
                log("native RequestMatch route error:", traceback.format_exc())
                original = getattr(match_cls, "_reborn_original_RequestMatch", None)
                if original:
                    return original(self, match_id, match_args, *args, **kwargs)
                return start_native_offline_match(int(match_id))

        def native_offline_do_request_match(self, match_id, match_args=None, *args, **kwargs):
            try:
                log("Native DoRequestMatch route:", match_id, repr(match_args))
                return start_native_offline_match(int(match_id))
            except Exception:
                log("native DoRequestMatch route error:", traceback.format_exc())
                original = getattr(match_cls, "_reborn_original_DoRequestMatch", None)
                if original:
                    return original(self, match_id, match_args, *args, **kwargs)
                return start_native_offline_match(int(match_id))

        if not hasattr(match_cls, "_reborn_original_RequestMatch"):
            match_cls._reborn_original_RequestMatch = getattr(match_cls, "RequestMatch", None)
        match_cls.RequestMatch = native_offline_request_match

        if not hasattr(match_cls, "_reborn_original_DoRequestMatch"):
            match_cls._reborn_original_DoRequestMatch = getattr(match_cls, "DoRequestMatch", None)
        match_cls.DoRequestMatch = native_offline_do_request_match

        import mb.components.player_team_logic as player_team_logic
        team_cls = player_team_logic.PlayerLogic

        def offline_team_CreateTeam(self, group_id, *args, **kwargs):
            try:
                import game_env
                gdata = game_env.GetInstance().game_data
                grp = gdata.FindProtoById("GroupProto", group_id)
                if grp and grp.get("match_id"):
                    native_match_id = int(grp.get("match_id"))
                    log("Offline team_CreateTeam fallback routing to match_id:", native_match_id)
                    return start_native_offline_match(native_match_id)
            except Exception:
                log("offline_team_CreateTeam error:", traceback.format_exc())
            original = getattr(team_cls, "_reborn_original_team_CreateTeam", None)
            if original:
                return original(self, group_id, *args, **kwargs)

        if not hasattr(team_cls, "_reborn_original_team_CreateTeam"):
            team_cls._reborn_original_team_CreateTeam = getattr(team_cls, "team_CreateTeam", None)
        team_cls.team_CreateTeam = offline_team_CreateTeam

        import mb.entities.player_avatar_class as player_avatar_class
        avatar_cls = player_avatar_class.PlayerAvatar
        avatar_cls.DoRequestMatch = native_offline_do_request_match
        avatar_cls.RequestMatch = native_offline_request_match

        if player is not None:
            player.DoRequestMatch = lambda match_id, match_args=None, *a, **k: start_native_offline_match(int(match_id))
            player.RequestMatch = lambda match_id, *a, **k: start_native_offline_match(int(match_id))
            player.team_CreateTeam = offline_team_CreateTeam
        log("Offline matchmaking and team fallback adapters fully installed")
    except Exception:
        log("patch_offline_match_adapter error:", traceback.format_exc())


def patch_local_lifecycle():
    """Return cleanly to hall after native local-game exit."""
    try:
        import gvisual.visual_main as visual_main
        if not hasattr(visual_main, "_reborn_original_LeaveGameOverUI"):
            visual_main._reborn_original_LeaveGameOverUI = visual_main.LeaveGameOverUI

        def local_LeaveGameOverUI(*args, **kwargs):
            try:
                return visual_main._reborn_original_LeaveGameOverUI(*args, **kwargs)
            finally:
                normalize_hall_status()

        visual_main.LeaveGameOverUI = local_LeaveGameOverUI
        log("patch_local_lifecycle installed on LeaveGameOverUI")
    except Exception:
        log("patch_local_lifecycle error:", traceback.format_exc())


def patch_offline_network_change():
    """Ignore physical connectivity transitions only inside an offline session."""
    try:
        import game
        import main_game
        original = main_game.GameOnNetworkChanged
        if not hasattr(main_game, "_reborn_original_GameOnNetworkChanged"):
            main_game._reborn_original_GameOnNetworkChanged = original

        def offline_GameOnNetworkChanged(last_type, cur_type):
            try:
                import game_env
                genv = game_env.GetInstance()
                if getattr(genv, "is_offline_mode", False):
                    genv.network_type = cur_type
                    log("Offline network transition ignored:", last_type, cur_type)
                    return
            except Exception:
                log("offline network transition guard error:", traceback.format_exc())
            return main_game._reborn_original_GameOnNetworkChanged(last_type, cur_type)

        main_game.GameOnNetworkChanged = offline_GameOnNetworkChanged
        game.on_network_changed = offline_GameOnNetworkChanged
    except Exception:
        log("patch_offline_network_change error:", traceback.format_exc())


def set_node_visible(node, visible):
    if not node:
        return
    for name in ("setVisible", "SetVisible", "set_visible", "Set_Visible"):
        fn = getattr(node, name, None)
        if callable(fn):
            try:
                fn(visible)
                return
            except Exception:
                pass


def patch_mod_comp():
    """Safely resolve talent attributes during combat unit initialization without KeyError."""
    try:
        import gcore.components.mod_comp as mod_comp
        import both.talent_info as talent_info
        if not hasattr(mod_comp.ModComponent, "_reborn_orig_modInitAttr"):
            mod_comp.ModComponent._reborn_orig_modInitAttr = mod_comp.ModComponent.modInitAttrFromTalents

            def safe_modInitAttrFromTalents(self, page, *args, **kwargs):
                try:
                    if isinstance(page, (int, long, str, unicode)):
                        import game_env
                        p_inst = getattr(game_env.GetInstance(), "player", None)
                        pages = getattr(p_inst, "talent_pages", {}) if p_inst else {}
                        try:
                            p_key = int(page)
                        except Exception:
                            p_key = 1
                        if p_key not in pages and 1 in pages:
                            p_key = 1
                        page = pages.get(p_key, {})
                    if not isinstance(page, dict):
                        return
                    if "sumary" not in page:
                        talents = page.get("talents", [2, 5, 9, 16])
                        page = talent_info.gen_talent_page_info(talents, "tmp", 60)
                    return mod_comp.ModComponent._reborn_orig_modInitAttr(self, page, *args, **kwargs)
                except Exception:
                    log("safe_modInitAttrFromTalents error:", traceback.format_exc())

            mod_comp.ModComponent.modInitAttrFromTalents = safe_modInitAttrFromTalents
            log("patch_mod_comp installed successfully")
    except Exception:
        log("patch_mod_comp error:", traceback.format_exc())


def patch_energy_core_selection():
    """Keep the native energy-core picker mutually exclusive and refresh it after selection."""
    try:
        import game_ui.dialog.talent.talent_option as talent_option
        panel_cls = talent_option.Panel
        if not hasattr(panel_cls, "_reborn_original_UpdateTalentInfo"):
            panel_cls._reborn_original_UpdateTalentInfo = panel_cls.UpdateTalentInfo

            def reborn_UpdateTalentInfo(self, *args, **kwargs):
                result = panel_cls._reborn_original_UpdateTalentInfo(
                    self, *args, **kwargs)
                try:
                    import game_env
                    selected = int(getattr(
                        game_env.GetInstance().player,
                        "talent_selected_page", 1))
                    # talent_option keeps the four live row widgets in
                    # self.allitem.  The virtual list's GetAllItem() is empty
                    # on this client, so using it silently skipped the real
                    # rows and left the stock lock/level decorations active.
                    live_items = getattr(self, "allitem", ()) or ()
                    if isinstance(live_items, dict):
                        live_items = live_items.values()
                    items = list(live_items)
                    if not items:
                        items = list(self.list_talent.GetAllItem())
                    buttons = [item.btn_select for item in items
                               if getattr(item, "btn_select", None)]
                    # The stock method builds a progressively growing group.  On
                    # this client that leaves every row visually checked.  Give
                    # every checkbox the same final group, then apply one state.
                    for button in buttons:
                        button.SetButtonGroup(buttons)
                    for item in items:
                        page_id = int(getattr(item, "page_id", 0) or 0)
                        is_selected = page_id == selected
                        if getattr(item, "s_lock_1", None):
                            item.s_lock_1.SetVisible(False)
                        if getattr(item, "l_page_num", None):
                            item.l_page_num.SetVisible(False)
                        if getattr(item, "btn_select", None):
                            item.btn_select.SetCheck(is_selected, False)
                        if getattr(item, "l_inuse", None):
                            item.l_inuse.SetVisible(is_selected)
                except Exception:
                    log("energy-core single-select refresh error:",
                        traceback.format_exc())
                return result

            panel_cls.UpdateTalentInfo = reborn_UpdateTalentInfo

        # UIComponent.NotifyUpdateSelectpage calls update_panel.  The shipped
        # implementation is empty, so a successful selection never repaints.
        def reborn_update_panel(self):
            return self.UpdateTalentInfo()

        panel_cls.update_panel = reborn_update_panel

        # Hero-select uses a different native panel for its personal core
        # plans.  Preserve that panel's own OnChecked callback and only remove
        # the obsolete level locks, then put every checkbox in one real group.
        import game_ui.dialog.equip_shop.dashen_equip_talent_config as combat_talent
        combat_cls = combat_talent.Panel
        if not hasattr(combat_cls, "_reborn_original_SetPersonalTalent"):
            combat_cls._reborn_original_SetPersonalTalent = \
                combat_cls.SetPersonalTalent

            def reborn_SetPersonalTalent(self, *args, **kwargs):
                result = combat_cls._reborn_original_SetPersonalTalent(
                    self, *args, **kwargs)
                try:
                    import game_env
                    items = list(self.talent_container.GetAllItem())
                    buttons = [item.btn_select for item in items
                               if getattr(item, "btn_select", None)]
                    for button in buttons:
                        button.SetButtonGroup(buttons)
                        if hasattr(button, "SetEnable"):
                            button.SetEnable(True)
                        if hasattr(button, "SetEnableTouch"):
                            button.SetEnableTouch(True)
                        button.SetVisible(True)
                    for item in items:
                        for name in ("spr_lock", "sLock", "txt_count"):
                            node = getattr(item, name, None)
                            if node:
                                node.SetVisible(False)
                        # The retired purchase/edit/spell-view overlays still
                        # cover the full row and consume the tap even after the
                        # lock icon is hidden.  They are unavailable offline;
                        # disable only their touch layers so the original
                        # btn_select/OnChecked path receives the row tap.
                        for name in ("btn_buy", "btn_exchange", "btn_redact",
                                     "btn_spell_view", "btn_spell_view_s"):
                            overlay = getattr(item, name, None)
                            if overlay and hasattr(overlay, "SetEnableTouch"):
                                overlay.SetEnableTouch(False)
                    # SetPersonalTalent and NotifySelectHeroInfoTalent already
                    # know the native page-id/index mapping.  Do not repaint
                    # check states here: the row widgets intentionally do not
                    # expose page_id, so guessing cleared every selection.
                    fn = getattr(self, "NotifySelectHeroInfoTalent", None)
                    if callable(fn) and getattr(self, "combat_member", None):
                        try:
                            fn(self.combat_member)
                        except Exception:
                            pass
                    log("Combat energy-core picker unlocked:",
                        len(items), "native selection preserved")
                except Exception:
                    log("combat energy-core picker refresh error:",
                        traceback.format_exc())
                return result

            combat_cls.SetPersonalTalent = reborn_SetPersonalTalent

        log("Native energy-core single-selection patch installed")
    except Exception:
        log("patch_energy_core_selection error:", traceback.format_exc())


def patch_ai_core_and_difficulty():
    """Give every native filler bot a real core page and use the complete 5v5 AI rule."""
    try:
        import game_env
        gdata = game_env.GetInstance().game_data

        # Match 13 ships with the reduced 1019 goal set.  It omits base defence,
        # tower defence and several recovery goals, which is why bots can
        # oscillate at a waypoint or remain idle.  1012 is the complete native
        # normal-strength 5v5 goal controller; difficult mode keeps its own 15 /
        # AIMapUBProto path and easy mode keeps match 6 / 1018.
        ai_map = gdata.FindProtoById("AIMapProto", 13)
        if ai_map:
            ai_map["ai_id"] = "1012"

        import gcore.ai.hero_select_subsystem.ai_system_forge as ai_forge
        forge_cls = ai_forge.AIForgeSubsystem
        if not hasattr(forge_cls, "_reborn_original_SelectTalent"):
            forge_cls._reborn_original_SelectTalent = forge_cls.SelectTalent

            def reborn_SelectTalent(self, combat_member, *args, **kwargs):
                result = forge_cls._reborn_original_SelectTalent(
                    self, combat_member, *args, **kwargs)
                try:
                    selected = combat_member.GetSelectedTalentInfo()
                    if isinstance(selected, dict) and selected.get("spells"):
                        return result
                    player = getattr(game_env.GetInstance(), "player", None)
                    pages = getattr(player, "talent_pages", {}) if player else {}
                    if not pages:
                        return result
                    position = int(getattr(combat_member, "position", 1) or 1)
                    page_id = ((position - 1) % len(pages)) + 1
                    if page_id not in pages:
                        page_id = sorted(pages.keys())[0]
                    page = pages[page_id]
                    combat_member.SetTalents(
                        page_id, list(page.get("talents", ())),
                        dict(page.get("sumary", {})),
                        list(page.get("spells", ())))
                    hero_id = int(getattr(combat_member, "select_hero_id", 0) or 0)
                    hero_info = combat_member.avatar_info.setdefault(
                        "heros", {}).setdefault(str(hero_id), {})
                    hero_info["select_tianfu"] = page_id
                    combat_member.UpdateSelectTalentInfo({"type": page_id})
                    log("AI energy-core assigned:",
                        combat_member.player_guid, hero_id, page_id)
                except Exception:
                    log("AI energy-core assignment error:", traceback.format_exc())
                return result

            forge_cls.SelectTalent = reborn_SelectTalent
        log("Native AI core/controller patch installed")
    except Exception:
        log("patch_ai_core_and_difficulty error:", traceback.format_exc())


def patch_visual_runtime_bootstrap():
    """Reinstall combat hooks after VisualEnv loads/rebinds the core modules."""
    try:
        import gvisual.visual_env as visual_env_mod
        env_cls = visual_env_mod.VisualEnv
        if not hasattr(env_cls, "_reborn_original_InitVisuals"):
            env_cls._reborn_original_InitVisuals = env_cls.InitVisuals

            def reborn_InitVisuals(self, *args, **kwargs):
                result = env_cls._reborn_original_InitVisuals(
                    self, *args, **kwargs)
                # InitVisuals imports/rebinds ModComponent.  Installing before
                # StartLocalGame is too early and caused the 100% loading crash.
                # It also reloads the hero-select talent module, so reapply the
                # single-selection picker patch here as well.
                patch_mod_comp()
                patch_ai_core_and_difficulty()
                patch_energy_core_selection()
                patch_offline_network_change()
                return result

            env_cls.InitVisuals = reborn_InitVisuals
        log("Visual runtime bootstrap patch installed")
    except Exception:
        log("patch_visual_runtime_bootstrap error:", traceback.format_exc())


def patch_talent_ui():
    """Unlock and enable full interactive energy-core editing across all preset pages."""
    try:
        import game_ui.dialog.talent.talent_main as talent_main
        if not hasattr(talent_main.Panel, "_reborn_orig_update_items"):
            talent_main.Panel._reborn_orig_update_items = talent_main.Panel.update_items

            def reborn_update_items(self):
                talent_main.Panel._reborn_orig_update_items(self)
                try:
                    for itm in self.list_in.getItems():
                        nod_plan = itm.getChildByName("nod_plan")
                        if nod_plan:
                            set_node_visible(nod_plan.getChildByName("sLock"), False)
                            if not getattr(self, "is_del_mode", False):
                                set_node_visible(nod_plan.getChildByName("btn_change"), True)
                except Exception:
                    pass

            talent_main.Panel.update_items = reborn_update_items

        import game_ui.dialog.talent.talent_edit_3d as talent_edit_3d
        if not hasattr(talent_edit_3d.Panel, "_reborn_orig_HideOrShowAll"):
            talent_edit_3d.Panel._reborn_orig_HideOrShowAll = talent_edit_3d.Panel.HideOrShowAll

            def reborn_HideOrShowAll(self, is_show, is_init=False):
                talent_edit_3d.Panel._reborn_orig_HideOrShowAll(self, is_show, is_init)
                try:
                    if hasattr(self, "btn_rename"):
                        set_node_visible(self.btn_rename, True)
                    if hasattr(self, "nod_descr"):
                        for c in self.nod_descr.getChildren():
                            if c.getName() in ("sLock", "txt_descr", "spr_lock"):
                                set_node_visible(c, False)
                    if hasattr(self, "btn_use"):
                        set_node_visible(self.btn_use, True)
                except Exception:
                    pass

            talent_edit_3d.Panel.HideOrShowAll = reborn_HideOrShowAll

        if not hasattr(talent_edit_3d.Panel, "_reborn_orig_Big_Click"):
            talent_edit_3d.Panel._reborn_orig_Big_Click = talent_edit_3d.Panel.Big_Click

            def reborn_Big_Click(self, *args, **kwargs):
                res = talent_edit_3d.Panel._reborn_orig_Big_Click(self, *args, **kwargs)
                try:
                    if hasattr(self, "btn_use"):
                        set_node_visible(self.btn_use, True)
                except Exception:
                    pass
                return res

            talent_edit_3d.Panel.Big_Click = reborn_Big_Click
        log("Talent UI unlocking patches installed successfully!")
    except Exception:
        log("patch_talent_ui error:", traceback.format_exc())


def patch_hall_ui():
    import ui.basepanel as basepanel
    if not hasattr(basepanel.BasePanel, "_entry_item_dict"):
        basepanel.BasePanel._entry_item_dict = {}
    if not hasattr(basepanel.BasePanel, "_proto_hash"):
        basepanel.BasePanel._proto_hash = None

    import game_ui.dialog.hall.hs_components.hall_scene_right_top as right_top
    right_top.HallSceneComponent.__tick_low_component__ = lambda self: None

    import game_ui.dialog.hall.hs_components.hall_scene_left_center as left_center

    def init_offline_store(self):
        self.store_roll_timer = None

    def offline_store_picture(self, *args, **kwargs):
        yield None

    left_center.HallSceneComponent.InitStoreRollPicture = init_offline_store
    left_center.HallSceneComponent.ChangeStorePicture = offline_store_picture

    import game_ui.dialog.hall.hs_components.hall_scene_hero as hall_hero

    def local_display_hero(self, hero_id):
        hero_id = int(hero_id)
        self.SetDisplayHero(hero_id, None, False, True)

    hall_hero.HallSceneComponent.DisplayHeroGotoStore = local_display_hero

    import game_ui.dialog.hall.hs_components.hall_scene_entry as hall_entry
    if hasattr(hall_entry, "switches"):
        hall_entry.switches.ENABLE_OFFLINE_BATTLE = True

    import mb.components.player_hall_logic as player_hall_logic
    player_hall_logic.PlayerLogic.ActionStep_ActivityShow = offline_noop_step
    player_hall_logic.PlayerLogic.ActionStep_MicroPackage = offline_noop_step

    # Initialize missing subpanel fields on prepare panel without no-oping LoadTalent
    try:
        import game_ui.dialog.prepare.personal_9 as prepare_panel
        panel_cls = prepare_panel.Panel
        sub_panel_fields = (
            "_hero_panel", "_talent_panel", "_equip_panel", "_zhoushu_panel",
            "_peizhi_panel", "_kuaijieyongyu_panel")
        if not hasattr(panel_cls, "_reborn_original_init"):
            panel_cls._reborn_original_init = panel_cls.__init__

            def reborn_prepare_init(self, *args, **kwargs):
                panel_cls._reborn_original_init(self, *args, **kwargs)
                for field in sub_panel_fields:
                    if not hasattr(self, field):
                        setattr(self, field, None)

            panel_cls.__init__ = reborn_prepare_init
        if not hasattr(panel_cls, "_reborn_original_LoadTalent"):
            panel_cls._reborn_original_LoadTalent = panel_cls.LoadTalent

            def reborn_LoadTalent(self, *args, **kwargs):
                for field in sub_panel_fields:
                    if not hasattr(self, field):
                        setattr(self, field, None)
                return panel_cls._reborn_original_LoadTalent(self, *args, **kwargs)

            panel_cls.LoadTalent = reborn_LoadTalent
        log("Native prepare/energy-core panel state restored")
    except Exception:
        log("prepare panel state patch error:", traceback.format_exc())

    patch_talent_ui()
    patch_energy_core_selection()
    patch_mod_comp()
    patch_ai_core_and_difficulty()
    patch_visual_runtime_bootstrap()
    patch_group_proto_offline()
    patch_offline_match_adapter()
    patch_local_lifecycle()
    patch_offline_network_change()
    patch_hero_select_ui()
    patch_equip_shop()


def build_offline_talent_pages(player):
    """Create real native energy-core pages instead of an empty mock object."""
    try:
        import both.talent_info as talent_info
        layouts = (
            (1, [2, 5, 9, 16], u"General Burst"),
            (2, [3, 7, 13, 15], u"Sustained Combat"),
            (3, [1, 8, 10, 18], u"Defense Cooldown"),
            (4, [4, 6, 12, 17], u"Survival Support"),
        )
        pages = {}
        for page_id, talents, name in layouts:
            pages[page_id] = talent_info.gen_talent_page_info(talents, name, 60)
        player.talent_pages = pages
        player.talent_selected_page = 1
        player.talent_slot_state = [True, True, True, True]
        player.talent_count_info = []
        player.talent_time_info = {}
        player.is_get_talent_data = True

        def notify_talent_callback():
            callback = getattr(player, "talent_info_callback", None)
            if callback:
                try:
                    return callback(*getattr(player, "talent_info_callback_args", ()))
                except Exception:
                    log("talent callback error:", traceback.format_exc())

        def local_request_all_talent_info(*args, **kwargs):
            player.is_get_talent_data = True
            notify_talent_callback()
            return True

        def local_select_talent_page(page, *args, **kwargs):
            page = int(page)
            if page in player.talent_pages:
                player.talent_selected_page = page
                # The combat member reads select_tianfu from each hero record,
                # not from talent_selected_page.  Keep both native fields in sync.
                for hero_info in getattr(player, "heros", {}).values():
                    try:
                        hero_info.select_tianfu = page
                    except Exception:
                        try:
                            hero_info["select_tianfu"] = page
                        except Exception:
                            pass
                notify_talent_callback()
                return True
            return False

        def local_update_talent_page(page, pageinfo, *args, **kwargs):
            page = int(page)
            current = dict(player.talent_pages.get(page, {}))
            if isinstance(pageinfo, dict):
                current.update(pageinfo)
            talents = list(current.get("talents", []))
            if len(talents) == 4:
                current = talent_info.gen_talent_page_info(
                    talents, current.get("name", u"Energy Core"), 60)
            player.talent_pages[page] = current
            notify_talent_callback()
            return True

        def local_update_talent_slot(page, slot, talent_id, *args, **kwargs):
            page = int(page)
            slot = int(slot)
            current = dict(player.talent_pages.get(page, {}))
            talents = list(current.get("talents", [2, 5, 9, 16]))
            while len(talents) < 4:
                talents.append(0)
            index = slot - 1 if slot > 0 else slot
            if index < 0 or index >= 4:
                return False
            talents[index] = int(talent_id)
            player.talent_pages[page] = talent_info.gen_talent_page_info(
                talents, current.get("name", u"Energy Core"), 60)
            notify_talent_callback()
            return True

        def local_rename_talent_page(page, name, *args, **kwargs):
            page = int(page)
            if page not in player.talent_pages:
                return False
            player.talent_pages[page]["name"] = name
            notify_talent_callback()
            return True

        def local_clear_talent_pages(page_list, *args, **kwargs):
            for page in page_list or ():
                page = int(page)
                if page in player.talent_pages:
                    old_name = player.talent_pages[page].get("name", u"Energy Core")
                    player.talent_pages[page] = talent_info.gen_talent_page_info(
                        [2, 5, 9, 16], old_name, 60)
            notify_talent_callback()
            return True

        player.RequestTalentAllInfo = local_request_all_talent_info
        player.RequestSelectTalentPage = local_select_talent_page
        player.RequestUpdateTalentPageInfo = local_update_talent_page
        player.RequestUpdateTalentSlot = local_update_talent_slot
        player.RequestTalentPageRename = local_rename_talent_page
        player.RequestClearTalentPage = local_clear_talent_pages
        player.TalentIsOpen = lambda *args, **kwargs: True
        player.GetTalentSlotState = lambda *args, **kwargs: [True, True, True, True]
        player.GetTalentOpenLevel = lambda *args, **kwargs: 1
        log("Native energy-core pages ready:", repr(player.talent_pages))
    except Exception:
        log("build_offline_talent_pages error:", traceback.format_exc())


def patch_frame_rate_ui(quality_setting, allowed):
    """Replace the binary high-frame toggle with six native radio buttons."""
    try:
        import game_ui.dialog.settings.setting_basic as setting_basic

        def install_controls(panel):
            try:
                if not getattr(panel, "xingneng", None) or not getattr(panel, "nod_scene", None):
                    return
                old_row = panel.xingneng
                # Work inside the original high-frame-rate row.  Cloning the
                # scene-quality row and round-tripping its UTF-8 title through
                # GetString/SetString garbled the Chinese label on this Python
                # 2 client.  Retaining the native row preserves its exact text,
                # icon, layout and localisation data.
                row = old_row
                panel.reborn_fps_row = row
                row.SetVisible(True)
                source = row.chk_1
                source.SetVisible(False)

                names = []
                for index, rate in enumerate(allowed):
                    name = "reborn_fps_%d" % index
                    item = getattr(row, name, None)
                    if item is None:
                        item = source.CloneAsBrother(name)
                        setattr(row, name, item)
                    item.SetPosition(305 + index * 132, 44)
                    item.SetContentSize(126, 48)
                    item.SetVisible(True)
                    item.chk.SetContentSize(126, 52)
                    item.chk.lab_on.SetString(str(rate), False)
                    item.chk.lab_off.SetString(str(rate), False)
                    item.chk._checkBoxText.SetString(str(rate), False)
                    item.chk.lab_on.SetPosition(63, 26)
                    item.chk.lab_off.SetPosition(63, 26)
                    item.chk._checkBoxText.SetPosition(63, 26)
                    names.append(name)

                import game_env
                mgr = game_env.GetInstance().setting_mgr
                selected = getattr(mgr, "reborn_frame_rate", 165)
                selected_index = allowed.index(selected) if selected in allowed else 5
                mgr.reborn_frame_rate_index = selected_index

                def choose_rate(index, *args, **kwargs):
                    index = int(index)
                    mgr.reborn_frame_rate_index = index
                    return quality_setting.SetRebornFrameRate(allowed[index])

                panel.CreateAttrGroupCheckBox(
                    "reborn_frame_rate_index", row, names, choose_rate,
                    None, False, selected_index, True)
                panel._reborn_fps_rate_values = allowed
                log("Native frame-rate selector ready:", allowed, "selected:", selected)
            except Exception:
                log("install frame-rate controls error:", traceback.format_exc())

        if not hasattr(setting_basic.Panel, "_reborn_original_InitSettingBtn"):
            setting_basic.Panel._reborn_original_InitSettingBtn = setting_basic.Panel._InitSettingBtn

            def reborn_InitSettingBtn(self, *args, **kwargs):
                result = setting_basic.Panel._reborn_original_InitSettingBtn(self, *args, **kwargs)
                install_controls(self)
                return result

            setting_basic.Panel._InitSettingBtn = reborn_InitSettingBtn

        if not hasattr(setting_basic.Panel, "_reborn_original_RefreshHighFrameShow"):
            setting_basic.Panel._reborn_original_RefreshHighFrameShow = \
                setting_basic.Panel.RefreshHighFrameShow

            def reborn_RefreshHighFrameShow(self, *args, **kwargs):
                result = setting_basic.Panel._reborn_original_RefreshHighFrameShow(
                    self, *args, **kwargs)
                row = getattr(self, "reborn_fps_row", None)
                if row:
                    try:
                        import game_env
                        selected = getattr(
                            game_env.GetInstance().setting_mgr,
                            "reborn_frame_rate", 165)
                        index = allowed.index(selected) if selected in allowed else 5
                        buttons = [getattr(row, "reborn_fps_%d" % i).chk
                                   for i in xrange(len(allowed))]
                        for i, button in enumerate(buttons):
                            button.SetCheck(i == index, False)
                    except Exception:
                        pass
                return result

            setting_basic.Panel.RefreshHighFrameShow = reborn_RefreshHighFrameShow
    except Exception:
        log("patch_frame_rate_ui error:", traceback.format_exc())


def install_frame_rate_support():
    """Remove the 30/60 engine clamp and expose a persistent six-level setter."""
    try:
        import game3d
        import game_share.quality_setting as quality_setting
        allowed = (30, 60, 90, 120, 144, 165)

        def read_saved_rate():
            try:
                if os.path.exists(FPS_PATH):
                    with open(FPS_PATH, "rb") as saved:
                        value = int(saved.read().strip())
                    if value in allowed:
                        return value
            except Exception:
                log("read saved frame rate error:", traceback.format_exc())
            return 165

        def save_rate(value):
            try:
                tmp_path = FPS_PATH + ".tmp"
                with open(tmp_path, "wb") as saved:
                    saved.write(str(int(value)))
                    saved.flush()
                if os.path.exists(FPS_PATH):
                    os.remove(FPS_PATH)
                os.rename(tmp_path, FPS_PATH)
            except Exception:
                log("save frame rate error:", traceback.format_exc())

        def SetRebornFrameRate(value):
            value = int(value)
            if value not in allowed:
                value = 60
            game3d.set_frame_rate(value)
            save_rate(value)
            try:
                import game_env
                game_env.GetInstance().setting_mgr.reborn_frame_rate = value
                game_env.GetInstance().setting_mgr.reborn_frame_rate_index = allowed.index(value)
            except Exception:
                pass
            log("Frame rate selected:", value, "engine:", game3d.get_frame_rate())
            return value

        quality_setting.REBORN_FRAME_RATES = allowed
        quality_setting.SetRebornFrameRate = SetRebornFrameRate
        if not hasattr(quality_setting, "_reborn_original_SetHighFrameRateMode"):
            quality_setting._reborn_original_SetHighFrameRateMode = \
                quality_setting.SetHighFrameRateMode

        def SetHighFrameRateMode(enable):
            if not enable:
                return SetRebornFrameRate(30)
            try:
                import game_env
                selected = getattr(
                    game_env.GetInstance().setting_mgr,
                    "reborn_frame_rate", 165)
            except Exception:
                selected = 165
            if selected not in allowed or selected == 30:
                selected = 165
            return SetRebornFrameRate(selected)

        quality_setting.SetHighFrameRateMode = SetHighFrameRateMode
        patch_frame_rate_ui(quality_setting, allowed)
        SetRebornFrameRate(read_saved_rate())
    except Exception:
        log("install_frame_rate_support error:", traceback.format_exc())


def build_offline_profile(player_name):
    global _player, _account

    import game_env
    import game_hall.hall_env as hall_env
    import mb.entities.player_avatar_class as player_avatar_class
    import mb.entities.account_avatar_class as account_avatar_class
    import both.hall_util as hall_util

    player_avatar_class.PlayerAvatar.ActionStep_ActivityShow = offline_noop_step
    player_avatar_class.PlayerAvatar.ActionStep_MicroPackage = offline_noop_step

    _player = player_avatar_class.PlayerAvatar(910001)
    _account = account_avatar_class.AccountAvatar(910002)

    env = game_env.GetInstance()
    env.player = _player
    env.account = _account
    env.is_offline_mode = True

    hall = hall_env.HallEnv()
    hall.player_guid = 910001
    hall.selected_role_guid = 910001

    _player.user_name = player_name
    _player.name = player_name
    _player.level = 60
    _player.role_id = 910001
    _player.mail_data = EmptyData()
    _player.local_data = EmptyData()
    _player.func_ctrl_mgr = EmptyData()
    _player.equip_data = EmptyData()
    _player.equip_scheme = EmptyData()
    _player.equip_plan = EmptyData()
    _account.login_in_combat = False

    build_offline_talent_pages(_player)

    all_heroes = get_hero_ids_safe()
    log("Initializing all heroes count:", len(all_heroes))
    
    hero_dict = {}
    for hid in all_heroes:
        try:
            info = _player.HeroGetHeroInfoByHeroId(int(hid))
            info.is_unlock = True
            info.level = 1
            info.select_tianfu = 1
            info.select_skin = hall_util.SkinNormalizeSkinId(int(hid), int(hid) * 100 + 1)
            hero_dict[int(hid)] = info
        except Exception:
            pass

    _player.heros = hero_dict
    _player.hero_list = all_heroes
    _player.own_heroes = all_heroes
    _player.all_heroes = all_heroes
    _player.combat_hero_list = all_heroes

    # Unlock all heroes in combat and hall
    for method_name in ("is_hero_unlock", "has_hero", "is_skin_unlock", "has_skin",
                        "IsHadHero", "IsHadHeroInfo", "IsHadSkin",
                        "HeroIsUnlock", "HeroIsHad"):
        setattr(_player, method_name, lambda *args, **kwargs: True)

    _player.GetHeroOwnType4Combat = lambda *args, **kwargs: 1
    _player.GetHeroState4Combat = lambda *args, **kwargs: 1
    _player.GetHeroList = lambda *args, **kwargs: all_heroes
    _player.GetAllHeros = lambda *args, **kwargs: all_heroes
    _player.GetOwnHeros = lambda *args, **kwargs: all_heroes
    _player.HeroGetAllHeroInfo = lambda *args, **kwargs: hero_dict
    _player.HeroGetHeroInfo = lambda *args, **kwargs: hero_dict
    _player.HeroGetHeroDict = lambda *args, **kwargs: hero_dict
    _player.GetOwnHeroesCount = lambda *args, **kwargs: len(all_heroes)
    _player.xinshou_all_unlock = True
    _player.xinshou_small_unlock = True

    # Status guards
    _player.team_InGroupMatchCombat = lambda *args, **kwargs: False
    _player.is_in_match = lambda *args, **kwargs: False
    _player.is_in_team = lambda *args, **kwargs: False
    _player.is_matching = lambda *args, **kwargs: False

    patch_group_proto_offline()
    patch_offline_match_adapter(_player)

    def local_set_hall_display(hero_id):
        hero_id = int(hero_id)
        _player.prop_display_hero_id = hero_id
        _player.equip_heroid = hero_id
        try:
            _player.HeroGetHeroInfoByHeroId(hero_id)
        except Exception:
            pass
        return True

    def local_modify_equip_hero(hero_id):
        _player.equip_heroid = int(hero_id)
        return True

    def local_use_skin(skin_id):
        skin_id = int(skin_id)
        try:
            hero_id = skin_id // 100
            hero_info = _player.HeroGetHeroInfoByHeroId(int(hero_id))
            normalized = hall_util.SkinNormalizeSkinId(int(hero_id), skin_id)
            hero_info.select_skin = normalized
            _player.prop_display_skin_id = normalized
            log("local skin selected", hero_id, skin_id, normalized)
            for obj in gc.get_objects():
                if type(obj).__name__ == "HeroDisplaySkin" or hasattr(obj, "UpdateBottomInfo"):
                    try:
                        if hasattr(obj, "UpdateBottomInfo"):
                            obj.UpdateBottomInfo()
                        if hasattr(obj, "UpdateModelShow"):
                            obj.UpdateModelShow()
                    except Exception:
                        pass
            return True
        except Exception:
            log("local skin error", traceback.format_exc())
            return False

    _player.SetHallDisplayHero = local_set_hall_display
    _player.ModifyHallEquipUIHeroId = local_modify_equip_hero
    _player.UseSkin = local_use_skin

    from both import consts
    _player.statusSet(consts.EPlayerStatus.IN_HALL)
    _player.statusSet(consts.EPlayerStatus.MATCH_IDLE)
    log("profile ready", repr(player_name), repr(_player.statusGetAllStatus()))


def do_enter_hall():
    global _running
    if _running:
        return
    _running = True
    log("Executing do_enter_hall...")
    try:
        player_name = read_player_name()
        try:
            load_external_translations()
        except Exception:
            log("load_external_translations error:", traceback.format_exc())

        # Attempt string dump early in case tables are already in memory
        try:
            dump_all_game_strings()
        except Exception:
            log("early dump error:", traceback.format_exc())

        try:
            patch_hall_ui()
        except Exception:
            log("patch_hall_ui error:", traceback.format_exc())

        try:
            patch_ui_localization()
        except Exception:
            log("patch_ui_localization error:", traceback.format_exc())

        try:
            patch_hall_util()
        except Exception:
            log("patch_hall_util error:", traceback.format_exc())

        try:
            build_offline_profile(player_name)
        except Exception:
            log("build_offline_profile error:", traceback.format_exc())

        try:
            install_frame_rate_support()
        except Exception:
            log("install_frame_rate_support error:", traceback.format_exc())

        try:
            patch_gdata_translations()
        except Exception:
            log("patch_gdata_translations error:", traceback.format_exc())

        import game_hall.hall_main as hall_main
        hall_main.Start()
        log("hall started successfully")

        try:
            patch_gdata_translations()
            auto_translate_sweep()
        except Exception:
            pass

        try:
            import mbengine.common.Timer as Timer
            Timer.addTimer(0.5, dump_all_game_strings)
            Timer.addTimer(1.0, auto_translate_sweep)
            Timer.addTimer(1.5, dump_all_game_strings)
            Timer.addTimer(2.0, auto_translate_sweep)
            Timer.addTimer(2.5, dump_all_game_strings)
            Timer.addTimer(3.5, auto_translate_sweep)
            Timer.addTimer(5.0, dump_all_game_strings)
            Timer.addTimer(7.5, dump_all_game_strings)
            Timer.addTimer(10.0, dump_all_game_strings)
            Timer.addTimer(1.5, patch_gdata_translations)
            Timer.addTimer(3.0, patch_gdata_translations)
            log("Timers registered for periodic auto_translate and string dump.")
        except Exception:
            log("Timer registration error:", traceback.format_exc())

        if ENABLE_LIVE_REPL:
            try:
                import mbengine.common.Timer as Timer
                Timer.addTimer(0.5, check_command)
                log("Live REPL timer loop started!")
            except Exception:
                pass
    except Exception:
        _running = False
        log("hall startup fatal error:", traceback.format_exc())


def enter_offline():
    log("enter_offline called")
    try:
        import mbengine.common.Timer as Timer
        Timer.addTimer(0.1, do_enter_hall)
        log("Timer scheduled for do_enter_hall")
    except Exception:
        log("Timer import or addTimer failed, executing do_enter_hall directly:", traceback.format_exc())
        do_enter_hall()


enter_offline()
