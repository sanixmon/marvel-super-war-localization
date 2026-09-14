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


# Auto-detect Android SDK build-tools and NDK LLVM toolchains dynamically
def setup_android_environment():
    candidates = []
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if var in os.environ and os.path.isdir(os.environ[var]):
            candidates.append(os.environ[var])
    home = os.path.expanduser("~")
    for sub in ("Android/Sdk", "Android/sdk", ".android"):
        p = os.path.join(home, sub)
        if os.path.isdir(p):
            candidates.append(p)

    # 1. Add build-tools to PATH
    for sdk in candidates:
        bt_dir = os.path.join(sdk, "build-tools")
        if os.path.isdir(bt_dir):
            for v in sorted(os.listdir(bt_dir), reverse=True):
                full_v = os.path.join(bt_dir, v)
                if os.path.isdir(full_v) and full_v not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = f"{full_v}:{os.environ.get('PATH', '')}"

    # 2. Add NDK llvm bin to PATH
    for sdk in candidates:
        ndk_dir = os.path.join(sdk, "ndk")
        if os.path.isdir(ndk_dir):
            for v in sorted(os.listdir(ndk_dir), reverse=True):
                for host in ("linux-x86_64", "darwin-x86_64", "darwin-arm64", "windows-x86_64"):
                    llvm_bin = os.path.join(ndk_dir, v, "toolchains/llvm/prebuilt", host, "bin")
                    if os.path.isdir(llvm_bin) and llvm_bin not in os.environ.get("PATH", ""):
                        os.environ["PATH"] = f"{llvm_bin}:{os.environ.get('PATH', '')}"
                        os.environ.setdefault("ANDROID_NDK_HOME", os.path.join(ndk_dir, v))
                        break


setup_android_environment()


def log(msg):
    print(f"[*] {msg}")


def run(cmd, desc="", check=True, cwd=None):
    if desc:
        log(desc)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
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
    rust_dir = "native-rust"
    if os.path.isdir(rust_dir):
        log("Compiling native ARM64 hook library via Rust (native-rust)...")
        run("cargo build --target aarch64-linux-android --release", "Building Rust locnative library...", cwd=rust_dir)
        rust_so = os.path.join(rust_dir, "target/aarch64-linux-android/release/liblocnative.so")
        if os.path.isfile(rust_so):
            run(f"patchelf --set-soname liblocnative.so {rust_so}")
            os.makedirs(NATIVE_DIR, exist_ok=True)
            shutil.copyfile(rust_so, os.path.join(NATIVE_DIR, "liblocnative.so"))
            log(f"Rust native library compiled successfully: {rust_so}")
            return rust_so

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


def patch_arsc(tmp_apk):
    log("Patching application label in resources.arsc...")
    with zipfile.ZipFile(tmp_apk, "r") as z:
        arsc_data = bytearray(z.read("resources.arsc"))

    # Replace Chinese app name with 'Marvel Super War' in ARSC UTF-8 string pool
    target = b"\x06\x12\xe6\xbc\xab\xe5\xa8\x81\xe8\xb6\x85\xe7\xba\xa7\xe6\x88\x98\xe4\xba\x89\x00"
    replacement = b"\x10\x10Marvel Super War\x00\x00\x00"
    if target in arsc_data:
        idx = arsc_data.find(target)
        arsc_data[idx:idx + len(replacement)] = replacement
        with open("resources.arsc", "wb") as f:
            f.write(arsc_data)
        run(f"zip -0 -u {tmp_apk} resources.arsc", "Updating APK with patched resources.arsc...")
        if os.path.isfile("resources.arsc"):
            os.remove("resources.arsc")
        log("App name successfully changed to 'Marvel Super War' in resources.arsc.")
    else:
        log("Target app name string not found or already patched in resources.arsc.")


def main():
    parser = argparse.ArgumentParser(description="Marvel Super War Standalone Mod APK Builder")
    parser.add_argument("--no-arsc", action="store_true", help="Skip patching Android resources.arsc")
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

    # 1. Patch resources.arsc to change app name to 'Marvel Super War'
    if not args.no_arsc:
        patch_arsc(tmp_apk)

    # 2. Inject VFS discrete files & Documents scripts
    files_to_inject = [
        "assets/neox.xml",
        "assets/script/init.py",
        "assets/script/translator.py",
        "assets/script/locale_en.py"
    ]
    if os.path.isfile("assets/Documents/reborn_offline.py"):
        files_to_inject.append("assets/Documents/reborn_offline.py")
    if os.path.isfile("assets/Documents/loc_en.json"):
        files_to_inject.append("assets/Documents/loc_en.json")
    inject_list_str = " ".join(files_to_inject)
    run(f"zip -0 -u {tmp_apk} {inject_list_str}", "Injecting VFS discrete loader, Python localization scripts, and Documents...")

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
