# -*- coding: utf-8 -*-
"""
Verification and Testing Script for Marvel Super War Localization
Simulates in-game gdata patching against the dumped runtime tables to verify coverage.
"""

import json
import re
import os

LOC_PATH = "assets/Documents/loc_en.json"
DUMP_PATH = "extracted_dump/gdata_dump.json"

def run_tests():
    print("==================================================")
    print("RUNNING MARVEL SUPER WAR LOCALIZATION INTEGRITY TESTS")
    print("==================================================")

    # 1. Test Dictionary Load
    assert os.path.exists(LOC_PATH), f"Missing {LOC_PATH}"
    with open(LOC_PATH, "r", encoding="utf-8") as f:
        loc = json.load(f)
    print(f"[TEST PASS] Loaded {len(loc)} entries from {LOC_PATH}")

    # Build sorted replacement list like NeoX engine
    sorted_zh_keys = sorted(loc.keys(), key=lambda k: -len(k))

    def translate(s):
        if not s:
            return s
        if s in loc:
            return loc[s]
        s_strip = s.strip()
        if s_strip in loc:
            return s.replace(s_strip, loc[s_strip])
        # Substring replacement
        for k in sorted_zh_keys:
            if k in s:
                s = s.replace(k, loc[k])
        return s

    # 2. Test Key Hero Lookups
    heroes_test = [
        ("美国队长", "Captain America"),
        ("钢铁侠", "Iron Man"),
        ("蜘蛛侠", "Spider-Man"),
        ("浩克", "Hulk"),
        ("索尔", "Thor"),
        ("海拉", "Hela"),
        ("灭霸", "Thanos"),
        ("死侍", "Deadpool"),
        ("黑豹", "Black Panther"),
        ("奇异博士", "Doctor Strange"),
    ]
    for zh, en in heroes_test:
        res = translate(zh)
        assert res == en, f"Hero failed: {zh} -> {res} (expected {en})"
    print(f"[TEST PASS] Verified {len(heroes_test)} key heroes match official Marvel names")

    # 3. Test Key Items Lookups
    items_test = [
        ("瓦图姆魔杖", "Wand of Watoomb"),
        ("宇宙立方", "Cosmic Cube"),
        ("美队之盾", "Captain America's Shield"),
        ("风暴战斧", "Stormbreaker"),
        ("雷神之锤", "Mjolnir"),
        ("暗影斗篷", "Shadow Cloak"),
        ("心灵权杖", "Mind Scepter"),
    ]
    for zh, en in items_test:
        res = translate(zh)
        assert res == en, f"Item failed: {zh} -> {res} (expected {en})"
    print(f"[TEST PASS] Verified {len(items_test)} key items match official Marvel names")

    # 4. Test Key Energy Cores
    talents_test = [
        ("抑制粒子", "Suppression Particle"),
        ("强袭粒子", "Assault Particle"),
        ("暗星爆发", "Dark Star Burst"),
        ("灵能印记", "Psionic Mark"),
        ("时空滞缓", "Chrono Dilution"),
    ]
    for zh, en in talents_test:
        res = translate(zh)
        assert res == en, f"Talent failed: {zh} -> {res} (expected {en})"
    print(f"[TEST PASS] Verified {len(talents_test)} key energy cores match official English")

    # 5. Simulate In-Engine GData Patching against gdata_dump.json
    with open(DUMP_PATH, "r", encoding="utf-8") as f:
        gdata = json.load(f)["tables"]

    fields_to_check = (
        "show_name", "skin_name", "name", "hero_name", "title", "short_name",
        "desc", "skill_name", "spl_tips", "simple_spl_tips", "enhanced_spl_tips",
        "nickname", "story_tips", "tips", "display_name", "match_name", "ui_name",
        "achievement_name", "read_tips", "cond_desc", "common_desc", "rule",
        "description", "describe", "intro", "detail", "explain", "ai_name",
        "battle_strategy", "tips_name", "attr_only_3"
    )

    zh_re = re.compile(r"[\u4e00-\u9fff]")

    print("\n--- SIMULATING RUNTIME GDATA PROTO TABLE TRANSLATION ---")
    total_strings_seen = 0
    total_strings_translated = 0

    table_report = {}
    for tname, rows in gdata.items():
        t_total = 0
        t_trans = 0
        samples = []
        for rid, row in rows.items():
            for f in fields_to_check:
                val = row.get(f)
                if isinstance(val, str) and val.strip() and zh_re.search(val):
                    t_total += 1
                    total_strings_seen += 1
                    res = translate(val)
                    if res != val:
                        t_trans += 1
                        total_strings_translated += 1
                        if len(samples) < 2:
                            samples.append((f, val[:35], res[:35]))

        pct = (t_trans / t_total * 100) if t_total > 0 else 0
        table_report[tname] = (t_trans, t_total, pct, samples)

    for tname, (t_trans, t_total, pct, samples) in sorted(table_report.items(), key=lambda x: -x[1][1]):
        print(f"Table {tname:18s}: {t_trans:5d} / {t_total:5d} fields translated ({pct:5.1f}%)")
        for fld, orig_txt, trans_txt in samples:
            print(f"    Sample [{fld}]: {orig_txt} -> {trans_txt}")

    print("\n==================================================")
    total_pct = (total_strings_translated / total_strings_seen * 100) if total_strings_seen > 0 else 0
    print(f"TOTAL RUNTIME COVERAGE: {total_strings_translated} / {total_strings_seen} ({total_pct:.1f}%)")
    print("==================================================")
    assert total_pct > 95.0, f"Coverage too low: {total_pct:.1f}%"
    print("ALL TESTS PASSED WITH FLYING COLORS!")

if __name__ == "__main__":
    run_tests()
