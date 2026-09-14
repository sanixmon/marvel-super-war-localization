# PATCH REPORT: MINIMAL PROOF OF CONCEPT (POC)

## 1. Objective
Modify one harmless user-visible UI string in the application package to verify the build, signing, and execution pipeline without risking destabilization of game logic, networking, or asset decoders.

---

## 2. Modified Target Files
- **Archive Entry**: `resources.arsc` (Stored uncompressed, 4-byte aligned)
- **Source Configs**:
  - `res/values/strings.xml`
  - `res/values-zh-rCN/strings.xml`
  - `res/values-en/strings.xml`

---

## 3. Exact Modifications Performed

| Resource Key | Original (Chinese) | Patched (English) | Target Scope |
| :--- | :--- | :--- | :--- |
| `app_name` | `漫威超级战争` | `Marvel Super War` | Launcher Icon / App Manager |
| `neox_exit_game_title` | `退出游戏` | `Exit Game` | System Exit Dialog Title |
| `neox_exit_game_tip` | `是否要立即离开瓦坎达战场？` | `Confirm to exit?` | In-match Exit Confirmation |
| `export_ef_alert_title` | `退出游戏` | `Exit Game` | Prompt Title |
| `export_ef_alert_message`| `你想要结束游戏并退出吗？` | `Do you want to exit the game?` | Prompt Message |
| `export_ef_alert_confirm`| `退出` | `Exit` | Dialog Confirm Button |
| `export_ef_alert_cancel` | `取消` | `Cancel` | Dialog Cancel Button |

---

## 4. Preservation Invariants Verified
- **Bytecode Integrity**: All 6 DEX files (`classes.dex` through `classes6.dex`) preserved bit-for-bit without modification.
- **Native Binaries**: Audio/video engines (`libfmodex.so`, `libfmodevent.so`, etc.) remain untouched.
- **Asset Integrity**: All 3.1 GB of `.npk` archives (`gui.npk`, `res.npk`, `script.npk`, hero packages) remain 100% intact.
- **Alignment**: 4-byte page boundary alignment preserved via `zipalign -p -f 4`.
- **Signatures**: Re-signed with `apksigner` (v1 + v2 + v3 scheme enabled).

---

## 5. Production Upgrade: Level 4 Native ARM64 Hooking (`liblocnative.so`)

Building upon the initial string POC, the production engine integrates an in-memory ARM64 inline hook written in **Rust** (`native-rust/`):

- **Target Binary**: `lib/arm64-v8a/libclient.so` (version 3.22.2)
- **ELF Header**: Injected `DT_NEEDED liblocnative.so` via `patchelf`.
- **Hook Targets**:
  - `cocos2d::ui::Text::setString(const std::string&)` at `0xe1463c`
  - `cocos2d::ui::Button::setTitleText(const std::string&)` at `0xde7ed4`
- **Trampoline Mechanism**:
  - ARM64 `ldr x16, #8; br x16` absolute register indirect jump.
  - Hardware cache synchronization via `dc cvau`, `ic ivau`, `dsb ish`, and `isb`.
  - Android 15 16KB page-size aligned (`-Wl,-z,max-page-size=16384`).
- **Dictionary**: 5,594+ static entries with single-cycle ASCII bypass and $O(1)$ static hashmap lookup (< 1 µs latency).
- **Physical Verification**: Confirmed functional on POCO F5 (Android 14 / HyperOS) with zero crashes, rendering English strings directly on first draw call.
