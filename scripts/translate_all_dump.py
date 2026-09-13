# -*- coding: utf-8 -*-
"""
Automated Batch Localization Builder for Marvel Super War
Extracts, translates, and normalizes all Chinese strings from gdata_dump.json
using curated Marvel MOBA dictionaries and neural batch translation.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

DUMP_JSON_PATH = "extracted_dump/gdata_dump.json"
CACHE_JSON_PATH = "extracted_dump/translation_cache.json"
LOC_JSON_PATH = "assets/Documents/loc_en.json"

# ==========================================
# 1. CURATED MASTER DICTIONARIES
# ==========================================
CORE_TERMS = {
    "能量伤害": "Energy Damage",
    "物理伤害": "Physical Damage",
    "真实伤害": "True Damage",
    "暴击伤害": "Crit Damage",
    "暴击率": "Crit Rate",
    "暴击": "Critical",
    "物理攻击": "Physical Attack",
    "能量强度": "Energy Attack",
    "物理防御": "Physical Defense",
    "能量抗性": "Energy Resistance",
    "生命值": "HP",
    "生命": "Max HP",
    "最大生命值": "Max HP",
    "最大生命": "Max HP",
    "已损生命值": "Missing HP",
    "已损生命": "Missing HP",
    "移动速度": "Movement Speed",
    "移速": "Movement Speed",
    "攻击速度": "Attack Speed",
    "攻速": "Attack Speed",
    "冷却时间": "Cooldown",
    "冷却缩减": "Cooldown Reduction",
    "冷却": "Cooldown",
    "法力值": "Energy",
    "法力": "Energy",
    "护盾": "Shield",
    "普攻": "Basic Attack",
    "强化普攻": "Enhanced Basic Attack",
    "普通攻击": "Basic Attack",
    "特殊普攻": "Special Basic Attack",
    "技能": "Ability",
    "被动": "Passive",
    "主动": "Active",
    "被动-": "Passive - ",
    "主动-": "Active - ",
    "击飞": "Knockup",
    "减速": "Slow",
    "禁锢": "Immobilize",
    "眩晕": "Stun",
    "沉默": "Silence",
    "嘲讽": "Taunt",
    "冰冻": "Freeze",
    "定身": "Root",
    "致盲": "Blind",
    "隐身": "Stealth",
    "潜行": "Camouflage",
    "伪装": "Disguise",
    "霸体": "Control Immunity",
    "免控": "CC Immune",
    "免疫": "Immune",
    "吸血": "Lifesteal",
    "物理吸血": "Physical Lifesteal",
    "能量吸血": "Energy Lifesteal",
    "法术吸血": "Energy Lifesteal",
    "穿透": "Penetration",
    "物理穿透": "Physical Pierce",
    "能量穿透": "Energy Pierce",
    "减治疗": "Healing Reduction",
    "重伤": "Grievous Wounds",
    "回血": "HP Regen",
    "回复": "Recover",
    "恢复": "Restore",
    "友方英雄": "Allied Hero",
    "敌方英雄": "Enemy Hero",
    "友军": "Allies",
    "敌军": "Enemies",
    "目标": "Target",
    "范围": "Area",
    "野怪": "Jungle Monster",
    "小兵": "Minion",
    "士兵": "Minions",
    "防御塔": "Turret",
    "基地": "Base",
    "码": "Yards",
    "秒": "Seconds",
    "秒内": "Seconds",
    "持续": "Lasts ",
    "不可选中": "Untargetable",
    "位移": "Dash",
    "闪现": "Blink",
    "击败": "Defeat",
    "击杀": "Kill",
    "助攻": "Assist",
    "超神": "Legendary",
}

HEROES = {
    "美国队长": "Captain America",
    "钢铁侠": "Iron Man",
    "蜘蛛侠": "Spider-Man",
    "鹰眼": "Hawkeye",
    "黑寡妇": "Black Widow",
    "浩克": "Hulk",
    "索尔": "Thor",
    "雷神": "Thor",
    "猎鹰": "Falcon",
    "惊奇队长": "Captain Marvel",
    "冬兵": "Winter Soldier",
    "冬日战士": "Winter Soldier",
    "蚁人": "Ant-Man",
    "黄蜂女": "Wasp",
    "快银": "Quicksilver",
    "猩红女巫": "Scarlet Witch",
    "幻视": "Vision",
    "黑豹": "Black Panther",
    "黑骑士": "Black Knight",
    "斗篷与匕首": "Cloak & Dagger",
    "亡刃黑鸦": "Corvus Glaive",
    "暗夜比邻星": "Proxima Midnight",
    "黑舌谋士": "Ebony Maw",
    "黑曜霸王": "Cull Obsidian",
    "黑曜五将": "Black Order",
    "洛基": "Loki",
    "海姆达尔": "Heimdall",
    "希芙": "Lady Sif",
    "希芙女士": "Lady Sif",
    "刽子手": "Executioner",
    "镭射眼": "Cyclops",
    "万磁王": "Magneto",
    "暴风女": "Storm",
    "冰人": "Iceman",
    "天使": "Angel",
    "野兽": "Beast",
    "艾玛·弗罗斯特": "Emma Frost",
    "白皇后": "Emma Frost",
    "李千欢": "Jubilee",
    "死侍": "Deadpool",
    "格鲁特": "Groot",
    "星爵": "Star-Lord",
    "卡魔拉": "Gamora",
    "火箭浣熊": "Rocket Raccoon",
    "毁灭者德拉克斯": "Drax",
    "德拉克斯": "Drax",
    "勇度": "Yondu",
    "螳螂女": "Mantis",
    "罗南": "Ronan",
    "指控者罗南": "Ronan the Accuser",
    "隐形女侠": "Invisible Woman",
    "神奇先生": "Mister Fantastic",
    "霹雳火": "Human Torch",
    "黑蝠王": "Black Bolt",
    "黑霹雷": "Black Bolt",
    "水晶": "Crystal",
    "美杜莎": "Medusa",
    "破剑者": "Lockjaw",
    "灭霸": "Thanos",
    "纳摩": "Namor",
    "海王纳摩": "Namor",
    "海拉": "Hela",
    "奇异博士": "Doctor Strange",
    "古一": "Ancient One",
    "莫度男爵": "Baron Mordo",
    "毒液": "Venom",
    "屠杀": "Carnage",
    "幽灵蜘蛛": "Ghost-Spider",
    "格温蜘蛛侠": "Ghost-Spider",
    "战争机器": "War Machine",
    "反浩克装甲": "Hulkbuster",
    "小辣椒": "Rescue",
    "救援装甲": "Rescue",
    "铁心": "Ironheart",
    "夜魔侠": "Daredevil",
    "超胆侠": "Daredevil",
    "刀锋战士": "Blade",
    "铁拳": "Iron Fist",
    "月光骑士": "Moon Knight",
    "幽灵": "Ghost",
    "金刚狼": "Wolverine",
    "钢力士": "Colossus",
    "灵蝶": "Psylocke",
    "夜行者": "Nightcrawler",
    "魔形女": "Mystique",
    "剑齿虎": "Sabretooth",
    "牌皇": "Gambit",
    "小淘气": "Rogue",
    "罗刹女": "Rogue",
    "松鼠女": "Squirrel Girl",
    "恶灵骑士": "Ghost Rider",
    "沙人": "Sandman",
    "沙魔": "Sandman",
    "绿魔": "Green Goblin",
    "章鱼博士": "Doctor Octopus",
    "模仿大师": "Taskmaster",
    "浪": "Wave",
    "雪堆": "Luna Snow",
    "冰雪花": "Luna Snow",
    "虎灵": "War Tiger",
    "战争之虎": "War Tiger",
    "X教授": "Professor X",
    "查尔斯": "Professor X",
    "凤凰女": "Phoenix",
    "琴·葛蕾": "Jean Grey",
    "秘客": "Magik",
    "神秘客": "Mysterio",
    "猎人克莱文": "Kraven",
    "电光人": "Electro",
    "蜥蜴教授": "Lizard",
    "太阳黑子": "Sunspot",
    "电索": "Cable",
    "主教": "Bishop",
    "石头人": "The Thing",
    "皮克西": "Pixie",
    "北极星": "Polaris",
    "月星": "Moonstar",
    "亚当": "Adam Warlock",
    "术士亚当": "Adam Warlock",
}

EQUIP_ITEMS = {
    "治疗组件": "Healing Module",
    "军用佩刀": "Combat Knife",
    "小型手枪": "Handgun",
    "武士锤": "War Hammer",
    "乌木剑": "Ebony Blade",
    "天光匕首": "Daylight Dagger",
    "战神残剑": "Broken Blade of Ares",
    "亚卡箭": "Yaka Arrow",
    "处刑利刃": "Executioner's Blade",
    "深渊阔斧": "Abyss Broadaxe",
    "赤骨短刀": "Crimson Dagger",
    "巨龙之息": "Dragon's Breath",
    "芬里厄之牙": "Fang of Fenris",
    "核电能源": "Nuclear Energy Core",
    "卢恩符文": "Runic Charm",
    "长明宝钻": "Eternal Diamond",
    "分裂炸弹": "Cluster Bomb",
    "金乌法杖": "Sun Staff",
    "守序之盒": "Box of Order",
    "冰霜灵球": "Frost Orb",
    "西索恩残页": "Chthonic Scroll",
    "电磁火炮": "Electromagnetic Cannon",
    "作战服": "Combat Uniform",
    "防护手套": "Protective Gloves",
    "龙血石": "Dragon Bloodstone",
    "无畏水晶": "Fearless Crystal",
    "合金盾牌": "Alloy Shield",
    "隔离目镜": "Insulated Goggles",
    "高分子护手": "Polymer Bracers",
    "烈风肩甲": "Gale Pauldrons",
    "百战护臂": "Veteran Armguards",
    "耀日胸甲": "Sun Chestplate",
    "拂晓指环": "Dawn Ring",
    "便携猎枪": "Portable Shotgun",
    "突击猎枪": "Assault Shotgun",
    "量子步枪": "Quantum Rifle",
    "火神怒焰": "Vulcan's Rage",
    "以太之光": "Aether Light",
    "连珠步枪": "Repeater Rifle",
    "轻便跑鞋": "Agile Boots",
    "行军靴": "Marching Boots",
    "防护靴": "Protective Boots",
    "英灵战靴": "Einherjar Boots",
    "狂猎胫甲": "Wild Hunt Greaves",
    "遥感靴": "Telemetry Boots",
    "火箭靴": "Rocket Boots",
    "神盾局徽章": "S.H.I.E.L.D. Badge",
    "复仇者勋章": "Avengers Medal",
    "医疗箱": "First Aid Kit",
    "暮光神剑": "Twilight Sword",
    "长空叠影": "Sky Mirage",
    "无声猎手": "Silent Hunter",
    "女武神长弓": "Valkyrie Bow",
    "风暴战斧": "Stormbreaker",
    "雷神之锤": "Mjolnir",
    "泰坦荣耀": "Titan's Glory",
    "霍芬德圣剑": "Hofund",
    "永恒之枪": "Gungnir",
    "胜利战刃": "Blade of Victory",
    "永夜主宰": "Lord of Eternal Night",
    "弑神剑": "Godkiller",
    "寒光双刃": "Dual Cold Blades",
    "不朽亡刃": "Immortal Glaive",
    "光辉神铠": "Radiant Armor",
    "碎星战衣": "Star-Cracker Suit",
    "悬浮斗篷": "Cloak of Levitation",
    "妖精假面": "Faerie Mask",
    "梅金腰带": "Megingjord",
    "振金战甲": "Vibranium Suit",
    "美队之盾": "Captain America's Shield",
    "死神幻影": "Death's Phantom",
    "瓦图姆魔杖": "Wand of Watoomb",
    "宇宙立方": "Cosmic Cube",
    "神行飞翼": "Swift Wings",
    "心灵权杖": "Mind Scepter",
    "远古冬棺": "Casket of Ancient Winters",
    "电弧反应堆": "Arc Reactor",
    "绝境病毒": "Extremis Virus",
    "阿戈摩托之眼": "Eye of Agamotto",
    "反物质炮": "Antimatter Cannon",
    "黑暗神书": "Darkhold",
    "宝石棱镜": "Gem Prism",
    "强化血清": "Super-Soldier Serum",
    "再生摇篮": "Cradle of Regeneration",
    "负频手环": "Nega-Band",
    "暗影斗篷": "Shadow Cloak",
    "死侍火箭炮": "Deadpool's Rocket",
    "超智头盔": "A.I.M. Helmet",
    "银槲弯刀": "Mistletoe Scimitar",
    "审判之鹰": "Eagle of Judgment",
    "守门人号角": "Gjallarhorn",
    "脉冲手雷": "Pulse Grenade",
    "不朽烈焰": "Eternal Flame",
    "游猎之眼": "Hunter's Eye",
    "战术准星": "Tactical Crosshair",
    "奥丁之剑": "Sword of Odin",
    "恐惧弯刀": "Scimitar of Fear",
    "黑曜巨斧": "Obsidian Great-Axe",
    "碳纳钢刀": "Carbonadium Katana",
    "石中剑": "Excalibur",
    "圣甲虫": "Scarab",
    "至黑朽刃": "All-Black the Necrosword",
    "装备残骸": "Equipment Wreckage",
}

EQUIP_NICKS = {
    "主动位移": "Active Blink",
    "主动免控": "Active CC Immune",
    "主动免疫": "Active Immunity",
    "共生体": "Symbiote",
    "减治疗": "Anti-Heal",
    "减速减治疗": "Slow & Anti-Heal",
    "双抗": "Dual Resist",
    "反伤": "Damage Reflect",
    "叠层魔抗": "Stacking Energy Resist",
    "吸血护盾": "Lifesteal Shield",
    "强力攻击": "Heavy Attack",
    "恢复道具": "Consumable",
    "打野": "Jungle",
    "技能暴击": "Ability Crit",
    "护甲冷却": "Armor & Cooldown",
    "抵挡技能": "Spell Shield",
    "攻击冷却": "Attack & Cooldown",
    "攻击生命": "Attack & HP",
    "攻击能量抗性": "Attack & Energy Resist",
    "攻速暴击": "Attack Speed & Crit",
    "攻速穿透": "Attack Speed & Pierce",
    "无法出售": "Cannot Sell",
    "普攻吸血": "Basic Attack Lifesteal",
    "普攻增伤": "Basic Attack Damage Boost",
    "普攻强化": "Enhanced Basic Attack",
    "暴击加速": "Crit Speed Boost",
    "暴击转攻速": "Crit to Attack Speed",
    "治疗强化": "Enhanced Healing",
    "物防减伤": "Armor & Damage Reduction",
    "物防反伤": "Armor & Reflect",
    "生命冷却": "HP & Cooldown",
    "生命回复": "HP Regen",
    "生命恢复": "HP Recovery",
    "百分比伤害": "% Max HP Damage",
    "群体强化": "Team Buff",
    "群体护盾": "Team Shield",
    "能量回复": "Energy Regen",
    "能量护盾": "Energy Shield",
    "能量物防": "Energy & Armor",
    "能量萃取": "Energy Leech",
    "脱战加速": "Out-of-Combat Speed",
    "范围伤害": "AoE Damage",
    "触发护盾": "Triggered Shield",
    "辅助": "Support",
    "降低物防": "Armor Reduction",
}

TALENTS = {
    "抑制粒子": "Suppression Particle",
    "强袭粒子": "Assault Particle",
    "狂战粒子": "Berserker Particle",
    "转化粒子": "Conversion Particle",
    "修复组件": "Restoration Module",
    "抗性组件": "Resistance Module",
    "强化组件": "Enhancement Module",
    "防护组件": "Protection Module",
    "暗星爆发": "Dark Star Burst",
    "灵能印记": "Psionic Mark",
    "强心秘术": "Fortified Heart",
    "高能辐射": "High-Energy Radiation",
    "战神降临": "War God's Descent",
    "时空滞缓": "Chrono Dilution",
    "敏捷模块": "Agility Module",
    "活力模块": "Vitality Module",
    "通灵模块": "Psionic Module",
    "冷却模块": "Cooldown Module",
}

TACTICS = {
    "回城": "Recall",
    "制裁": "Smite",
    "绝命制裁": "Lethal Smite",
    "驱散": "Cleanse",
    "瞬移": "Blink",
    "麻痹": "Paralyze",
    "加速": "Sprint",
    "重创": "Ignite",
    "医疗": "Heal",
    "侦察": "Scout",
    "转移": "Teleport",
    "转移取消": "Cancel Teleport",
    "升级回复": "Level Up Recovery",
    "加速刷新": "Speed Refresh",
    "嘲讽": "Taunt",
    "百鬼神力": "Hundred Ghosts Power",
    "离线保护": "Offline Protection",
    "娱乐模式": "Arcade Mode",
    "回复装置": "Recovery Device",
    "反重力爆炸": "Anti-Gravity Blast",
    "反重力跳跃": "Anti-Gravity Leap",
    "回城二段": "Recall Phase 2",
}

MATCH_MAPS = {
    "输入房间码": "Enter Room Code",
    "新手训练": "Rookie Training",
    "英雄大乱斗": "Hero Brawl",
    "对战房间-禁选5v5": "Custom Room - Draft Pick 5v5",
    "对战房间-普通5v5": "Custom Room - Normal 5v5",
    "对战房间": "Custom Room",
    "匹配战": "Matchmaking",
    "地区对抗赛": "Regional Clash",
    "振金争夺战": "Vibranium Battle",
    "英雄特训": "Hero Training",
    "玩法特训": "Gameplay Training",
    "排位战": "Ranked Match",
    "单人排位战": "Solo Ranked",
    "观察者视界": "Spectator Mode",
    "开房间-英雄大乱斗": "Custom - Hero Brawl",
    "开房间-振金争夺战": "Custom - Vibranium Battle",
    "新手练习场": "Rookie Practice Field",
    "序章": "Prologue",
    "娱乐玩法": "Arcade Mode",
    "大乱斗玩法": "Brawl Mode",
    "效用1V9": "Practice 1v9",
    "塔防简单难度": "Tower Defense (Easy)",
}

# Load existing cache if available
cache = {}
if os.path.exists(CACHE_JSON_PATH):
    try:
        with open(CACHE_JSON_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached translations from {CACHE_JSON_PATH}")
    except Exception as e:
        print("Error loading cache:", e)

# Seed cache with curated dictionaries
for d in (CORE_TERMS, HEROES, EQUIP_ITEMS, EQUIP_NICKS, TALENTS, TACTICS, MATCH_MAPS):
    for k, v in d.items():
        if k not in cache:
            cache[k] = v

def save_cache():
    with open(CACHE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ==========================================
# 2. TRANSLATION ENGINE WITH TAG PRESERVATION
# ==========================================
def translate_google_raw(text):
    word = urllib.parse.quote(text)
    url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=zh-CN&tl=en&q={word}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    for attempt in range(4):
        try:
            resp = urllib.request.urlopen(req, timeout=8)
            res = json.loads(resp.read().decode("utf-8"))[0]
            return res
        except Exception as e:
            time.sleep(0.5 * (attempt + 1))
    return None

def post_process_english(en):
    # Standardize MOBA terms
    repls = [
        (r"\bphysical damage\b", "Physical Damage"),
        (r"\benergy damage\b", "Energy Damage"),
        (r"\btrue damage\b", "True Damage"),
        (r"\bcrit damage\b", "Crit Damage"),
        (r"\bcritical damage\b", "Critical Damage"),
        (r"\bphysical attack\b", "Physical Attack"),
        (r"\benergy attack\b", "Energy Attack"),
        (r"\bphysical defense\b", "Physical Defense"),
        (r"\benergy resistance\b", "Energy Resistance"),
        (r"\bmovement speed\b", "Movement Speed"),
        (r"\battack speed\b", "Attack Speed"),
        (r"\bcooldown reduction\b", "Cooldown Reduction"),
        (r"\bcooldown\b", "Cooldown"),
        (r"\bbasic attack\b", "Basic Attack"),
        (r"\benhanced basic attack\b", "Enhanced Basic Attack"),
        (r"\bmax hp\b", "Max HP"),
        (r"\bmissing hp\b", "Missing HP"),
        (r"\blifesteal\b", "Lifesteal"),
        (r"\bimmobilize\b", "Immobilize"),
        (r"\bknockup\b", "Knockup"),
        (r"\bstun\b", "Stun"),
        (r"\bsilence\b", "Silence"),
        (r"\buntargetable\b", "Untargetable"),
        (r"\bcontrol immunity\b", "Control Immunity"),
    ]
    for pat, rep in repls:
        en = re.sub(pat, rep, en, flags=re.IGNORECASE)

    # Standardize hero names in text
    for zh, hero_en in HEROES.items():
        if zh in en:
            en = en.replace(zh, hero_en)

    return en

def translate_desc_with_tags(text):
    tokens = []
    def repl(m):
        tokens.append(m.group(0))
        return f" X{len(tokens)-1}X "

    # Protect {expression} and #[a-zA-Z0-9]+
    protected = re.sub(r"\{[^{}]+\}|#[a-zA-Z0-9]+", repl, text)

    raw_trans = translate_google_raw(protected)
    if not raw_trans:
        return text

    # Restore tokens
    for i, tok in enumerate(tokens):
        raw_trans = re.sub(rf"X\s*{i}\s*X", tok, raw_trans)

    # Clean up formatting around tags
    raw_trans = re.sub(r"\s*(#[a-zA-Z0-9]+)\s*", r"\1", raw_trans)
    raw_trans = re.sub(r"\s*(\{[^{}]+\})\s*", r" \1 ", raw_trans)
    raw_trans = re.sub(r"\s+", " ", raw_trans).strip()

    return post_process_english(raw_trans)

def translate_short_batch(batch_list):
    """Translate a list of short strings (names, terms) in one HTTP call."""
    joined = "\n".join(batch_list)
    raw_trans = translate_google_raw(joined)
    if not raw_trans:
        return None
    lines = raw_trans.split("\n")
    if len(lines) != len(batch_list):
        return None
    return [post_process_english(l.strip()) for l in lines]


# ==========================================
# 3. LOAD ALL DUMP STRINGS
# ==========================================
with open(DUMP_JSON_PATH, "r", encoding="utf-8") as f:
    gdata = json.load(f)["tables"]

zh_re = re.compile(r"[\u4e00-\u9fff]")

all_short = set()
all_long = set()

for tname, rows in gdata.items():
    for rid, r in rows.items():
        for k, v in r.items():
            if isinstance(v, str):
                s = v.strip()
                if s and zh_re.search(s):
                    if len(s) <= 15 and "{" not in s and "#" not in s:
                        all_short.add(s)
                    else:
                        all_long.add(s)

print(f"Total short strings to process: {len(all_short)}")
print(f"Total long/tagged strings to process: {len(all_long)}")

# Filter out already cached
needed_short = [s for s in all_short if s not in cache]
needed_long = [s for s in all_long if s not in cache]

print(f"Uncached short strings: {len(needed_short)}")
print(f"Uncached long/tagged strings: {len(needed_long)}")

# ==========================================
# 4. BATCH TRANSLATE SHORT STRINGS
# ==========================================
BATCH_SIZE = 25
batches = [needed_short[i:i + BATCH_SIZE] for i in range(0, len(needed_short), BATCH_SIZE)]

print(f"\n--- Batch Translating {len(needed_short)} Short Strings in {len(batches)} Batches ---")

def process_batch(b):
    res = translate_short_batch(b)
    if res:
        return list(zip(b, res))
    # Fallback to 1-by-1 if batch failed
    fallback_res = []
    for item in b:
        tr = translate_google_raw(item)
        if tr:
            fallback_res.append((item, post_process_english(tr.strip())))
    return fallback_res

completed_batches = 0
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_batch, b): b for b in batches}
    for fut in as_completed(futures):
        res_list = fut.result()
        for src, dst in res_list:
            cache[src] = dst
        completed_batches += 1
        if completed_batches % 10 == 0 or completed_batches == len(batches):
            print(f"  Processed {completed_batches}/{len(batches)} short batches ({len(cache)} in cache)")
            save_cache()

save_cache()

# ==========================================
# 5. TRANSLATE LONG / TAGGED DESCRIPTIONS
# ==========================================
print(f"\n--- Translating {len(needed_long)} Long / Tagged Descriptions ---")

def process_long(d):
    tr = translate_desc_with_tags(d)
    return d, tr

completed_long = 0
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_long, d): d for d in needed_long}
    for fut in as_completed(futures):
        src, dst = fut.result()
        cache[src] = dst
        completed_long += 1
        if completed_long % 100 == 0 or completed_long == len(needed_long):
            print(f"  Processed {completed_long}/{len(needed_long)} descriptions ({len(cache)} in cache)")
            save_cache()

save_cache()

# ==========================================
# 6. EXPORT MASTER LOCALIZATION JSON
# ==========================================
os.makedirs(os.path.dirname(LOC_JSON_PATH), exist_ok=True)
with open(LOC_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\n==========================================")
print(f"SUCCESS: Compiled {len(cache)} Master Translations into {LOC_JSON_PATH}")
print(f"==========================================")
