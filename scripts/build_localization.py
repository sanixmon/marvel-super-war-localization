# -*- coding: utf-8 -*-
"""Master localization builder for Marvel Super War."""

import json
import os
import re

DUMP_PATH = "extracted_dump/gdata_dump.json"
LOC_JSON_PATH = "assets/Documents/loc_en.json"

with open(DUMP_PATH, "r", encoding="utf-8") as f:
    gdata = json.load(f)["tables"]

trans = {}

def add(zh, en):
    if zh and en:
        zh = zh.strip()
        en = en.strip()
        if zh and en and zh != en:
            trans[zh] = en

# ==========================================
# 1. CORE MOBA TERMS & STATS
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
    "对目标造成": "Deals to target ",
    "对范围内敌人造成": "Deals to enemies in area ",
    "造成": "Deals ",
    "点": " ",
    "获得": "Grants ",
    "提升": "Increases ",
    "降低": "Reduces ",
    "减少": "Decreases ",
    "额外": "Bonus ",
    "基础": "Base ",
    "不可选中": "Untargetable",
    "位移": "Dash",
    "闪现": "Blink",
    "击败": "Defeat",
    "击杀": "Kill",
    "助攻": "Assist",
    "连杀": "Kill Streak",
    "超神": "Legendary",
}
for k, v in CORE_TERMS.items():
    add(k, v)

# ==========================================
# 2. HEROES (83 HEROES)
# ==========================================
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
}
for k, v in HEROES.items():
    add(k, v)

# ==========================================
# 3. ALL 103 EQUIPMENT ITEMS & NICKNAMES
# ==========================================
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
for k, v in EQUIP_ITEMS.items():
    add(k, v)

# Item Categories / Nicknames
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
for k, v in EQUIP_NICKS.items():
    add(k, v)

# ==========================================
# 4. ENERGY CORES / TALENTS (18 CORES)
# ==========================================
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
for k, v in TALENTS.items():
    add(k, v)

# ==========================================
# 5. BATTLE TACTICS (SUMMONER SPELLS)
# ==========================================
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
for k, v in TACTICS.items():
    add(k, v)

# ==========================================
# 6. MATCH UI & MAPS
# ==========================================
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
for k, v in MATCH_MAPS.items():
    add(k, v)

# ==========================================
# 7. POPULAR HERO SKILL NAMES
# ==========================================
SKILLS = {
    # Captain America
    "星盾飞掷": "Shield Throw",
    "正义制裁": "Justice's Strike",
    "复仇者先锋": "Avenger's Vanguard",
    "自由之星": "Star of Freedom",

    # Iron Man
    "追踪导弹": "Micro-Missiles",
    "电弧脉冲炮": "Arc Blast",
    "等离子推进": "Flight Propulsion",
    "天才工程师": "Genius Engineer",
    "反装甲导弹": "Anti-Armor Missiles",
    "方舟质子炮": "Proton Cannon",

    # Spider-Man
    "蛛网发射": "Web-Shooter",
    "蜘蛛飞荡": "Spidey Swing",
    "蛛丝惩戒": "Web Retribution",
    "蜘蛛力量": "Spidey Power",

    # Hulk
    "怒气冲顶": "Hulk Smash",
    "重拳裂地": "Ground Slam",
    "无敌陷阵": "Unstoppable Charge",
    "暴怒": "Rage",

    # Thor
    "神锤冲击": "Hammer Shock",
    "雷厉风驰": "Lightning Surge",
    "雷霆万钧": "Rolling Thunder",
    "雷电之神": "God of Thunder",
    "神锤轰雷": "Hammer Boom",

    # Loki
    "伪装幻术": "Illusion Disguise",
    "冰霜血统": "Frost Lineage",
    "魔法光束": "Magic Beam",
    "幻象神域": "Hall of Illusions",
    "欺诈之神": "God of Mischief",

    # Deadpool
    "你打不到": "Can't Touch This!",
    "你追不上": "Catch Me If You Can",
    "白费力气": "Can't Hit Me",
    "生人勿近": "Ya Can't Hide!",
    "丢个飞镖": "Bang! Bang! Bang!",

    # Hawkeye
    "爆裂箭": "Explosive Arrow",
    "声波箭": "Sonic Arrow",
    "贯穿箭": "Piercing Arrow",
    "精准瞄准": "Eagle Eye",

    # Black Widow
    "寡妇飞踢": "Widow's Kick",
    "寡妇螫针": "Widow's Bite",
    "特工潜伏": "Agent Stealth",
    "致命一击": "Lethal Strike",

    # Thanos
    "泰坦之力": "Titan Power",
    "力量宝石": "Power Stone",
    "空间宝石": "Space Stone",
    "时间宝石": "Time Stone",
    "现实宝石": "Reality Stone",
    "心灵宝石": "Mind Stone",
    "无限响指": "Infinite Snap",

    # Doctor Strange
    "时间倒流": "Time Reversal",
    "塞拉芬之盾": "Shield of the Seraphim",
    "维山帝之火": "Flames of the Faltine",
    "多玛姆的凝视": "Gaze of Dormammu",

    # Scarlet Witch
    "混沌魔法": "Chaos Magic",
    "心灵扭曲": "Mind Distortion",
    "混沌力场": "Chaos Field",
    "现实重塑": "Reality Wipe",

    # Corvus Glaive
    "亡命之战": "Desperate Battle",
    "灵魂战刃": "Soul Glaive",
    "血光之影": "Shadow of Blood",
    "绝命之刃": "Fatal Blade",

    # Proxima Midnight
    "贯日之枪": "Sun Piercer",
    "星夜猎杀": "Star Night Hunt",
    "黑曜长矛": "Obsidian Spear",

    # Ebony Maw
    "灵魂寄生": "Soul Parasite",
    "恶语喉舌": "Deceptive Tongue",
    "摄魂夺魄": "Soul Rend",
    "灵魂收集": "Soul Harvest",
    "蛊惑": "Bewilderment",

    # Cull Obsidian
    "黑曜重锤": "Obsidian Hammer",
    "巨锁回旋": "Chain Whirlwind",
    "霸者咆哮": "Tyrant Roar",

    # Star-Lord
    "元素枪": "Element Gun",
    "曙光号出击": "Milano Airstrike",
    "摇滚派": "Rock 'n' Roll",

    # Groot
    "枝干蔓延": "Branch Surge",
    "藤蔓缠绕": "Vine Entangle",
    "生生不息": "Endless Growth",
    "小格鲁特": "Baby Groot",

    # Rocket Raccoon
    "战术地雷": "Tactical Mine",
    "高能火炮": "Heavy Cannon",
    "量子脉冲": "Quantum Pulse",

    # Ant-Man
    "量子之光": "Quantum Light",
    "飞蚁奇袭": "Flying Ant Surprise",
    "蚁人突击": "Ant-Man Assault",
    "巨型战士": "Giant-Man",
    "微型战士": "Micro-Man",

    # Magneto
    "磁能屏障": "Magnetic Barrier",
    "金属风暴": "Metal Storm",
    "磁力压制": "Magnetic Suppression",
    "万象天引": "Magnetic Pull",

    # Storm
    "暴风狂涌": "Gale Surge",
    "闪电风暴": "Lightning Storm",
    "极光守护": "Aurora Guard",

    # Black Panther
    "黑豹突击": "Panther Strike",
    "振金重爪": "Vibranium Claws",
    "瓦坎达万岁": "Wakanda Forever",
    "豹灵庇护": "Bast's Protection",
}
for k, v in SKILLS.items():
    add(k, v)

# ==========================================
# 8. PROCESS DUMP DATA FOR AUTOMATIC EXPANSION
# ==========================================
# From EquipProto
for eid, eq in gdata.get("EquipProto", {}).items():
    sname = eq.get("show_name")
    if sname and sname in EQUIP_ITEMS:
        add(sname, EQUIP_ITEMS[sname])
    nick = eq.get("nickname")
    if nick and nick in EQUIP_NICKS:
        add(nick, EQUIP_NICKS[nick])

# From HeroSkinProto
for hid, h in gdata.get("HeroSkinProto", {}).items():
    sname = h.get("skin_name")
    if sname and sname in HEROES:
        add(sname, HEROES[sname])

# From TalentProto
for tid, t in gdata.get("TalentProto", {}).items():
    sname = t.get("show_name")
    if sname and sname in TALENTS:
        add(sname, TALENTS[sname])

# From MatchUIProto
for mid, m in gdata.get("MatchUIProto", {}).items():
    for f in ("ui_name", "name"):
        val = m.get(f)
        if val and val in MATCH_MAPS:
            add(val, MATCH_MAPS[val])

# From SpellProto
for sid, s in gdata.get("SpellProto", {}).items():
    sname = s.get("show_name")
    if sname and sname in SKILLS:
        add(sname, SKILLS[sname])

# Sort keys by length descending
sorted_keys = sorted(trans.keys(), key=lambda k: -len(k))
print(f"Total compiled dictionary entries: {len(trans)}")

# Save to assets/Documents/loc_en.json
os.makedirs(os.path.dirname(LOC_JSON_PATH), exist_ok=True)
with open(LOC_JSON_PATH, "w", encoding="utf-8") as out:
    json.dump(trans, out, ensure_ascii=False, indent=2)

print(f"Saved {len(trans)} translations to {LOC_JSON_PATH}")
