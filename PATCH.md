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
- **Native Binaries**: `lib/arm64-v8a/libclient.so` and all audio/video `.so` files untouched.
- **Asset Integrity**: All 3.1 GB of `.npk` archives (`gui.npk`, `res.npk`, `script.npk`, hero packages) remain 100% intact.
- **Alignment**: 4-byte page boundary alignment preserved via `zipalign -p -f 4`.
- **Signatures**: Re-signed with `apksigner` (v1 + v2 + v3 scheme enabled).
