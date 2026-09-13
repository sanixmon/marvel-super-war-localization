#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_mod_apk.py — Marvel Super War Standalone English Localization Builder

Injects internal NeoX VFS discrete loader configuration, Python localization
modules, and Level 4 Native C++ Hooking (liblocnative.so) directly into the APK.
Produces a self-contained, 1-click install APK.
"""

import os
import sys
import subprocess
import shutil
import zipfile
import argparse

ORIGINAL_APK = "marvel_by_sfys.apk"
OUTPUT_APK = "marvel_english_standalone.apk"
KEYSTORE = os.path.expanduser("~/.android/debug.keystore")
NATIVE_DIR = "native"


def log(msg):
    print(f"[*] {msg}")


def run(cmd, desc="", check=True):
    if desc:
        log(desc)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"[!] Command failed: {cmd}")
        print(res.stderr)
        sys.exit(1)
    return res.stdout


def ensure_keystore():
    if not os.path.isfile(KEYSTORE):
        log("Generating Android debug.keystore...")
        os.makedirs(os.path.dirname(KEYSTORE), exist_ok=True)
        run(
            f'keytool -genkey -v -keystore {KEYSTORE} -alias androiddebugkey '
            f'-storepass android -keypass android -keyalg RSA -keysize 2048 '
            f'-validity 10000 -dname "CN=Android Debug,O=Android,C=US"',
            check=True
        )


def verify_source_files():
    required = [
        ORIGINAL_APK,
        "assets/neox.xml",
        "assets/script/init.py",
        "assets/script/translator.py",
        "assets/script/locale_en.py"
    ]
    for f in required:
        if not os.path.isfile(f):
            print(f"[!] Required file missing: {f}")
            sys.exit(1)
    log("All required localization and engine files verified.")


def build_native_hook():
    log("Compiling native C++ hook library (liblocnative.so)...")
    run("make -C native", "Building native ARM64 companion library...")
    so_path = os.path.join(NATIVE_DIR, "liblocnative.so")
    if not os.path.isfile(so_path):
        print(f"[!] Compilation failed: {so_path} not found.")
        sys.exit(1)
    log(f"Native library compiled successfully: {so_path}")
    return so_path


def inject_native_hook(tmp_apk):
    so_path = build_native_hook()
    work_dir = "/tmp/native_patch_work"
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(os.path.join(work_dir, "lib", "arm64-v8a"), exist_ok=True)

    extracted_client = os.path.join(work_dir, "libclient_orig.so")
    patched_client = os.path.join(work_dir, "lib", "arm64-v8a", "libclient.so")
    copied_locnative = os.path.join(work_dir, "lib", "arm64-v8a", "liblocnative.so")

    # 1. Extract original libclient.so
    run(f"unzip -p {tmp_apk} lib/arm64-v8a/libclient.so > {extracted_client}", "Extracting libclient.so from APK...")

    # 2. Patch DT_NEEDED
    shutil.copyfile(extracted_client, patched_client)
    run(f"patchelf --add-needed liblocnative.so {patched_client}", "Injecting DT_NEEDED liblocnative.so into libclient.so...")

    # 3. Copy liblocnative.so
    shutil.copyfile(so_path, copied_locnative)

    # 4. Update APK archive
    cwd = os.getcwd()
    apk_abs = os.path.abspath(tmp_apk)
    run(
        f"cd {work_dir} && zip -0 -u {apk_abs} lib/arm64-v8a/libclient.so lib/arm64-v8a/liblocnative.so",
        "Updating APK with native hook binaries..."
    )

    shutil.rmtree(work_dir, ignore_errors=True)
    log("Native hook injection completed.")


def patch_arsc_if_requested(decoded_dir="apk_res_out"):
    if not os.path.isdir(decoded_dir):
        run(f"apktool d -s --no-assets {ORIGINAL_APK} -o {decoded_dir}", "Decoding resources with apktool (skipping assets)...")

    log("Patching Android XML string tables...")
    def replace_in_file(path, old, new):
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            if old in c:
                c = c.replace(old, new)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(c)

    replace_in_file(f"{decoded_dir}/res/values/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')
    replace_in_file(f"{decoded_dir}/res/values/strings.xml", '<string name="export_ef_alert_title">退出游戏</string>', '<string name="export_ef_alert_title">Exit Game</string>')
    replace_in_file(f"{decoded_dir}/res/values/strings.xml", '<string name="export_ef_alert_message">你想要结束游戏并退出吗？</string>', '<string name="export_ef_alert_message">Do you want to exit the game?</string>')
    replace_in_file(f"{decoded_dir}/res/values/strings.xml", '<string name="export_ef_alert_confirm">退出</string>', '<string name="export_ef_alert_confirm">Exit</string>')
    replace_in_file(f"{decoded_dir}/res/values/strings.xml", '<string name="export_ef_alert_cancel">取消</string>', '<string name="export_ef_alert_cancel">Cancel</string>')
    replace_in_file(f"{decoded_dir}/res/values-zh-rCN/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')
    replace_in_file(f"{decoded_dir}/res/values-zh-rCN/strings.xml", '<string name="neox_exit_game_tip">是否要立即离开瓦坎达战场？</string>', '<string name="neox_exit_game_tip">Confirm to exit?</string>')
    replace_in_file(f"{decoded_dir}/res/values-zh-rCN/strings.xml", '<string name="neox_exit_game_title">退出游戏</string>', '<string name="neox_exit_game_title">Exit Game</string>')
    replace_in_file(f"{decoded_dir}/res/values-en/strings.xml", '<string name="app_name">漫威超级战争</string>', '<string name="app_name">Marvel Super War</string>')

    run(f"apktool b --use-aapt2 {decoded_dir} -o tmp_rebuild.apk", "Rebuilding resources.arsc with AAPT2...")
    run("unzip -p tmp_rebuild.apk resources.arsc > resources.arsc", "Extracting compiled resources.arsc...")
    run("rm -f tmp_rebuild.apk")
    return True


def main():
    parser = argparse.ArgumentParser(description="Marvel Super War Standalone Mod APK Builder")
    parser.add_argument("--with-arsc", action="store_true", help="Also rebuild and inject patched Android resources.arsc")
    parser.add_argument("--no-native", action="store_true", help="Skip Level 4 native C++ hook injection")
    parser.add_argument("--out", default=OUTPUT_APK, help=f"Output APK path (default: {OUTPUT_APK})")
    args = parser.parse_args()

    out_apk = args.out
    tmp_apk = "tmp_unaligned.apk"
    aligned_apk = "tmp_aligned.apk"

    verify_source_files()
    ensure_keystore()

    log(f"Creating unaligned APK copy from {ORIGINAL_APK}...")
    shutil.copyfile(ORIGINAL_APK, tmp_apk)

    # 1. Patch resources.arsc if requested
    if args.with_arsc:
        patch_arsc_if_requested()
        run(f"zip -0 -u {tmp_apk} resources.arsc", "Injecting patched resources.arsc...")
        if os.path.isfile("resources.arsc"):
            os.remove("resources.arsc")

    # 2. Inject VFS discrete files
    files_to_inject = [
        "assets/neox.xml",
        "assets/script/init.py",
        "assets/script/translator.py",
        "assets/script/locale_en.py"
    ]
    inject_list_str = " ".join(files_to_inject)
    run(f"zip -0 -u {tmp_apk} {inject_list_str}", "Injecting VFS discrete loader and Python localization scripts...")

    # 3. Inject Native C++ Hooks (Level 4) unless disabled
    if not args.no_native:
        inject_native_hook(tmp_apk)

    # 4. Strip old signatures
    run(f'zip -d {tmp_apk} "META-INF/*.RSA" "META-INF/*.SF" "META-INF/*.MF"', "Stripping original signatures...", check=False)

    # 5. Zipalign (4-byte alignment)
    run(f"zipalign -p -f 4 {tmp_apk} {aligned_apk}", "Aligning APK to 4-byte page boundaries...")

    # 6. Apksigner sign
    run(
        f"apksigner sign --ks {KEYSTORE} --ks-key-alias androiddebugkey "
        f"--ks-pass pass:android --key-pass pass:android --out {out_apk} {aligned_apk}",
        "Signing APK with apksigner (v1 + v2 + v3 scheme)..."
    )

    # Clean up intermediate files
    for f in [tmp_apk, aligned_apk]:
        if os.path.isfile(f):
            os.remove(f)

    # 7. Verify signature
    out = run(f"apksigner verify --verbose {out_apk}", "Verifying signed APK signature...")
    print(out)

    log(f"[✓] SUCCESS: Generated standalone localized APK: {out_apk}")
    print(f"\nSize: {os.path.getsize(out_apk) / (1024*1024):.2f} MB")


if __name__ == "__main__":
    main()
