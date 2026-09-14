# REPRODUCTION AND BUILD GUIDE: MARVEL SUPER WAR (漫威超级战争)

This document contains step-by-step instructions to compile the high-performance **Rust ARM64 Native Hooking Engine (`native-rust/`)**, inject it into the game's native binary (`libclient.so`), and produce signed, standalone localized APKs using the automated build pipeline.

---

## 1. Architecture Overview: Dual-Engine Localization

The localization mod employs a hybrid high-performance architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Marvel Super War Client                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
┌─────────────────────────────────┐   ┌──────────────────────────────────┐
│  Level 4: Native Rust Hooking   │   │     Python VFS Offline Engine    │
│       (`liblocnative.so`)       │   │      (`reborn_offline.py`)       │
├─────────────────────────────────┤   ├──────────────────────────────────┤
│ • ARM64 Trampoline In-Memory    │   │ • Offline Game Server Emulation  │
│ • Intercepts Text::setString    │   │ • 83 Hero Unlocks & Energy Core  │
│ • Intercepts Button::setTitle   │   │ • Multi-Stage Cascade Sweeper    │
│ • O(1) Hashmap (5,594+ Strings) │   │ • Local Bot AI Matchmaking       │
│ • Single-Cycle ASCII Fast-Path  │   │ • Discrete VFS Asset Redirection │
│ • Sub-microsecond (<1µs) Exec   │   │ • Fallback Dialog Traversal      │
└─────────────────────────────────┘   └──────────────────────────────────┘
```

---

## 2. Prerequisites & Toolchain Setup

### A. Android SDK & Native Tools
Install the required platform and signing tools:
```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y zipalign apksigner openjdk-21-jdk zip patchelf python3

# Arch Linux
sudo pacman -S android-tools zipalign apksigner patchelf jdk21-openjdk zip python
```

Ensure Android build-tools (`zipalign`, `apksigner`, `aapt2`) and NDK `r27b` (or `r25`+) are installed and present in `$PATH`:
```bash
export ANDROID_NDK_HOME="/path/to/android-sdk/ndk/27.1.12297006"
export PATH="$PATH:$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin"
```

### B. Rust Toolchain (aarch64 Target)
Install the Rust toolchain with the Android 64-bit ARM target:
```bash
rustup target add aarch64-linux-android
```

Ensure `.cargo/config.toml` inside `native-rust/` specifies the NDK Clang linker and 16KB page-size compliance:
```toml
[target.aarch64-linux-android]
linker = "aarch64-linux-android21-clang"
rustflags = ["-C", "link-arg=-Wl,-z,max-page-size=16384"]
```

### C. Android Debug Keystore
```bash
if [ ! -f ~/.android/debug.keystore ]; then
    mkdir -p ~/.android
    keytool -genkey -v -keystore ~/.android/debug.keystore \
        -alias androiddebugkey -storepass android -keypass android \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -dname "CN=Android Debug,O=Android,C=US"
fi
```

---

## 3. The Native Rust Engine (`native-rust/`)

The native companion library (`liblocnative.so`) intercepts UI string assignments at the C++ level before geometry tessellation or GPU submission.

### Hook Offsets (libclient.so - aarch64)
Based on binary reverse engineering of `libclient.so` (version 3.22.2):
- `cocos2d::ui::Text::setString(const std::string&)`: `0xe1463c`
- `cocos2d::ui::Button::setTitleText(const std::string&)`: `0xde7ed4`

### ARM64 Trampoline Hook Mechanism
For each target function:
1. Change memory protection of the 16-byte prologue using `mprotect(PROT_READ | PROT_WRITE | PROT_EXEC)`.
2. Allocate an executable trampoline page (`mmap(PROT_READ | PROT_WRITE | PROT_EXEC)`).
3. Copy original overwritten instructions into the trampoline followed by an unconditional branch back to `target + 16`.
4. Overwrite target function prologue with an ARM64 register indirect jump:
   ```arm64
   ldr x16, #8     ; Load 64-bit absolute hook address from literal pool
   br  x16         ; Jump to hooked Rust handler
   .quad <hook_address>
   ```
5. **Hardware Cache Invalidation**: Invalidate Instruction Cache and flush Data Cache to Point of Unification (PoU) without relying on external compiler-rt symbols:
   ```cpp
   asm volatile("dc cvau, %0" : : "r"(addr) : "memory");
   asm volatile("dsb ish" : : : "memory");
   asm volatile("ic ivau, %0" : : "r"(addr) : "memory");
   asm volatile("dsb ish" : : : "memory");
   asm volatile("isb" : : : "memory");
   ```

### High-Performance Dictionary Architecture
- **Fast ASCII Bypass**: Checks text encoding; pure ASCII strings (numbers, identifiers, already-translated strings) bypass dictionary lookups in 1 CPU cycle.
- **Static Hashmap**: 5,594+ pre-compiled key-value pairs stored in static read-only memory. Direct exact lookups execute in $O(1)$ time (< 1 microsecond).
- **Sub-string Replacement**: Complex composite strings with variable parameters are split and matched greedily.

### Compiling native-rust Manually
```bash
cd native-rust
cargo build --target aarch64-linux-android --release
```
Compiled output: `native-rust/target/aarch64-linux-android/release/liblocnative.so`.

---

## 4. Automated 1-Click APK Builder (`build_mod_apk.py`)

The automated script handles native compilation, ELF header patching, binary resource table modification, asset injection, memory alignment, and cryptographic signing in a single command.

### Usage
Place the base game APK in the project directory as `marvel_by_sfys.apk` and run:
```bash
python3 build_mod_apk.py
```

### Build Pipeline Steps
1. **Source Verification**: Validates `marvel_by_sfys.apk`, `assets/neox.xml` (exact 3,135 bytes), and Python modules.
2. **Binary Resource Table Patch (`resources.arsc`)**:
   - Locates `application-label` UTF-8 entry `漫威超级战争` inside `resources.arsc`.
   - Modifies the string in-place to **`Marvel Super War`** (preserving exact byte offsets).
   - This ensures the game displays properly in the Android Launcher under "M" and is searchable by typing "Marvel".
3. **Rust Compilation**: Executes `cargo build --target aarch64-linux-android --release`.
4. **ELF DT_NEEDED Injection**:
   - Extracts `lib/arm64-v8a/libclient.so` from APK.
   - Executes: `patchelf --add-needed liblocnative.so libclient.so`.
   - Injects both `libclient.so` and `liblocnative.so` into the APK archive.
5. **VFS & Localization Injection**:
   - Injects `assets/neox.xml`, `assets/script/init.py`, `translator.py`, `locale_en.py`, `reborn_offline.py`, and `loc_en.json`.
6. **Signature Stripping**: Removes stale NetEase `META-INF/*.RSA` certificates.
7. **Zipalign**: Enforces 4-byte boundary page alignment (`zipalign -p -f 4`).
8. **Cryptographic Signing**: Signs using `apksigner` with v1 (JAR), v2 (APK Signature Scheme), and v3 schemes.

Generated file: **`marvel_english_standalone.apk`** (~3.1 GB).

---

## 5. Device Installation & Live Verification

Deploy to an Android device (e.g. POCO F5) via Wireless ADB or USB:
```bash
adb install -r marvel_english_standalone.apk
```

Launch the game and inspect logcat:
```bash
adb logcat -c
adb shell am start -n com.netease.g104.cn/com.netease.ntunisdk.external.protocol.ProtocolLauncher
adb logcat | grep -E "LocHookRust|RebornAssets"
```

### Expected Log Output:
```text
I LocHookRust: === Initializing Marvel Super War Rust Localization Hook (aarch64 Android) ===
I LocHookRust: Rust dictionary initialized (5594+ master entries).
I LocHookRust: Found libclient.so at base address: 0x7208e82000
I LocHookRust: Installed Text::setString hook at 0x7209c9663c
I LocHookRust: Installed Button::setTitleText hook at 0x7209c69ed4
I LocHookRust: === All Rust Native ARM64 Hooks Successfully Installed! ===
I RebornAssets: complete payload already installed
D nativeloader: Load libclient.so using class loader: ok
```
