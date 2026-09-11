# REPRODUCTION AND BUILD GUIDE: MARVEL SUPER WAR (漫威超级战争)

This document contains step-by-step instructions to reproduce the localization build pipeline, verify the proof of concept, and generate signed, installable APKs.

---

## 1. Prerequisites & Environment

Install the required re-engineering and signing toolchain:
```bash
sudo apt-get update
sudo apt-get install -y aapt aapt2 apktool zipalign apksigner openjdk-21-jdk zip python3
```

Ensure a debug keystore exists (created automatically if missing):
```bash
if [ ! -f ~/.android/debug.keystore ]; then
    mkdir -p ~/.android
    keytool -genkey -v -keystore ~/.android/debug.keystore         -alias androiddebugkey -storepass android -keypass android         -keyalg RSA -keysize 2048 -validity 10000         -dname "CN=Android Debug,O=Android,C=US"
fi
```

---

## 2. Fast Resource Decoding (Skipping 3GB Assets)

To avoid decompressing 3.1 GB of asset packages and decompiling 6 DEX files, invoke `apktool` with `--no-assets` and `-s`:
```bash
apktool d -s --no-assets marvel_by_sfys.apk -o apk_res_out
```

---

## 3. Applying String Modifications

Modify string entries in `apk_res_out/res/values*/strings.xml`.
For example, to translate the application label and exit dialog:
```python
# Replace in apk_res_out/res/values/strings.xml and values-zh-rCN/strings.xml
# app_name -> Marvel Super War
# neox_exit_game_title -> Exit Game
# neox_exit_game_tip -> Confirm to exit?
```

---

## 4. Rebuilding Resources with AAPT2

Recompile the resource table:
```bash
apktool b --use-aapt2 apk_res_out -o test_rebuild.apk
```

Extract the newly compiled binary resource table (`resources.arsc`):
```bash
unzip -p test_rebuild.apk resources.arsc > resources.arsc
```

---

## 5. In-Place Update, Alignment, and Signing

Update `resources.arsc` inside a copy of the original APK without recompressing assets:
```bash
# 1. Duplicate original APK
cp marvel_by_sfys.apk marvel_poc.apk

# 2. Update resources.arsc as uncompressed (stored)
zip -0 -u marvel_poc.apk resources.arsc

# 3. Strip previous signature blocks
zip -d marvel_poc.apk "META-INF/*.RSA" "META-INF/*.SF" "META-INF/*.MF"

# 4. 4-byte page align the APK archive
zipalign -p -f 4 marvel_poc.apk marvel_poc_aligned.apk

# 5. Sign with apksigner (v1, v2, v3 schemes)
apksigner sign --ks ~/.android/debug.keystore     --ks-key-alias androiddebugkey     --ks-pass pass:android     --key-pass pass:android     --out marvel_poc_signed.apk     marvel_poc_aligned.apk

# 6. Verify signature and alignment
apksigner verify --verbose marvel_poc_signed.apk
```

---

## 6. Installation & Verification

When a physical Android device or emulator is connected via ADB:
```bash
adb install -r marvel_poc_signed.apk
```
Launch the game:
- Confirm application icon displays **Marvel Super War**
- Launch game and press back to verify exit prompt displays **Confirm to exit?**
