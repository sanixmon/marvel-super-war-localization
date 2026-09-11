#!/usr/bin/env python3
"""
patch_poc.py — Marvel Super War Automated Localization Patcher (Proof of Concept)

Reproduces the resource extraction, string patch, repack, alignment, and signature verification.
"""

import os
import sys
import subprocess
import shutil

ORIGINAL_APK = "marvel_by_sfys.apk"
DECODED_DIR = "apk_res_out"
OUTPUT_SIGNED_APK = "marvel_poc_signed.apk"
KEYSTORE = os.path.expanduser("~/.android/debug.keystore")

def run(cmd, desc=""):
    if desc:
        print(f"[*] {desc}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error running command: {cmd}")
        print(res.stderr)
        sys.exit(1)
    return res.stdout

def main():
    if not os.path.isfile(ORIGINAL_APK):
        print(f"[!] Target APK {ORIGINAL_APK} not found.")
        sys.exit(1)

    # 1. Ensure keystore exists
    if not os.path.isfile(KEYSTORE):
        print("[*] Generating Android debug.keystore...")
        os.makedirs(os.path.dirname(KEYSTORE), exist_ok=True)
        run(f'keytool -genkey -v -keystore {KEYSTORE} -alias androiddebugkey -storepass android -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US"')

    # 2. Decode resources if not already decoded
    if not os.path.isdir(DECODED_DIR):
        run(f"apktool d -s --no-assets {ORIGINAL_APK} -o {DECODED_DIR}", "Decoding resources with apktool (skipping assets)...")

    # 3. Patch strings
    print("[*] Patching string resources...")
    def replace_in_file(path, old, new):
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            if old in c:
                c = c.replace(old, new)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(c)

    # Values strings
    replace_in_file(f"{DECODED_DIR}/res/values/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')
    replace_in_file(f"{DECODED_DIR}/res/values/strings.xml", '<string name="export_ef_alert_title">退出游戏</string>', '<string name="export_ef_alert_title">Exit Game</string>')
    replace_in_file(f"{DECODED_DIR}/res/values/strings.xml", '<string name="export_ef_alert_message">你想要结束游戏并退出吗？</string>', '<string name="export_ef_alert_message">Do you want to exit the game?</string>')
    replace_in_file(f"{DECODED_DIR}/res/values/strings.xml", '<string name="export_ef_alert_confirm">退出</string>', '<string name="export_ef_alert_confirm">Exit</string>')
    replace_in_file(f"{DECODED_DIR}/res/values/strings.xml", '<string name="export_ef_alert_cancel">取消</string>', '<string name="export_ef_alert_cancel">Cancel</string>')

    # Chinese locale overrides
    replace_in_file(f"{DECODED_DIR}/res/values-zh-rCN/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')
    replace_in_file(f"{DECODED_DIR}/res/values-zh-rCN/strings.xml", '<string name="neox_exit_game_tip">是否要立即离开瓦坎达战场？</string>', '<string name="neox_exit_game_tip">Confirm to exit?</string>')
    replace_in_file(f"{DECODED_DIR}/res/values-zh-rCN/strings.xml", '<string name="neox_exit_game_title">退出游戏</string>', '<string name="neox_exit_game_title">Exit Game</string>')

    # English locale overrides
    replace_in_file(f"{DECODED_DIR}/res/values-en/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')

    # 4. Rebuild resource table with aapt2
    run(f"apktool b --use-aapt2 {DECODED_DIR} -o tmp_rebuild.apk", "Rebuilding resources with AAPT2...")
    run("unzip -p tmp_rebuild.apk resources.arsc > resources.arsc", "Extracting compiled resources.arsc...")
    run("rm -f tmp_rebuild.apk")

    # 5. Inject into APK clone
    tmp_apk = "tmp_unaligned.apk"
    aligned_apk = "tmp_aligned.apk"
    print("[*] Creating patched APK copy...")
    shutil.copyfile(ORIGINAL_APK, tmp_apk)
    run(f"zip -0 -u {tmp_apk} resources.arsc", "Updating resources.arsc in archive...")
    run(f'zip -d {tmp_apk} "META-INF/*.RSA" "META-INF/*.SF" "META-INF/*.MF"', "Stripping old signatures...")
    run(f"zipalign -p -f 4 {tmp_apk} {aligned_apk}", "Aligning APK to 4-byte boundaries...")
    run(f"apksigner sign --ks {KEYSTORE} --ks-key-alias androiddebugkey --ks-pass pass:android --key-pass pass:android --out {OUTPUT_SIGNED_APK} {aligned_apk}", "Signing APK with debug key...")
    
    # Clean temporary files
    run(f"rm -f {tmp_apk} {aligned_apk} resources.arsc")

    # 6. Verify signature
    out = run(f"apksigner verify --verbose {OUTPUT_SIGNED_APK}", "Verifying signature...")
    print(out)
    print(f"[✓] Successfully generated {OUTPUT_SIGNED_APK}")

if __name__ == '__main__':
    main()
