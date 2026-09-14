# Marvel Super War — English Localization Mod & Toolkit
*(漫威超级战争 英文本地化补丁与工具包)*

[![Game](https://img.shields.io/badge/Game-Marvel%20Super%20War%20(CN)-red.svg)](https://g104.163.com/)
[![Engine: Rust ARM64](https://img.shields.io/badge/Engine-Rust%20ARM64-orange.svg)](native-rust/)
[![Android: 15 Ready](https://img.shields.io/badge/Android%2015-16KB%20Page%20Size-brightgreen.svg)](native-rust/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![No Root Required](https://img.shields.io/badge/Root-Not%20Required-success.svg)](#quick-installation)

Complete English localization and offline combat suite for **Marvel Super War** (`com.netease.g104.cn`).  
Powered by a **Dual-Engine architecture**: **Native ARM64 Rust Trampoline Hooking** for sub-microsecond in-memory UI translation, coupled with a **Python VFS Runtime** for local server and bot match emulation.

---

## 🎮 Installation Methods · Cara Pemasangan

Choose the installation method that best suits your setup:

### 🌟 Option 1: Standalone Mod APK (1-Click Install · Recommended)
*Best for most players. No file manager or `Android/data` access required.*
1. Build or download the pre-patched **`marvel_english_standalone.apk`** (see [BUILD.md](BUILD.md)).
2. Install via ADB or standard Android package installer:
   ```bash
   adb install -r marvel_english_standalone.apk
   ```
3. **Benefits:**
   - App label displays as **`Marvel Super War`** in the launcher (searchable by typing "Marvel").
   - **Level 4 Rust Hook (`liblocnative.so`)** activates automatically at boot.
   - Zero configuration or manual file copying required.

---

### 📂 Option 2: Hot-Drop Documents (No APK Reinstall · 3-Step Setup)
*For players who already have the base game APK installed and do not want to re-download 3 GB.*

| 🇬🇧 English | 🇮🇩 Bahasa Indonesia |
|---|---|
| 📥 **[Download Mod Package (`mod_documents.zip`)](../../releases/latest)** | 📥 **[Unduh Paket Mod (`mod_documents.zip`)](../../releases/latest)** |
| 📖 **[Full Installation Guide (INSTALL_EN.md)](INSTALL_EN.md)** | 📖 **[Panduan Lengkap (INSTALL_ID.md)](INSTALL_ID.md)** |

1. **Download** `mod_documents.zip` from **[Releases](../../releases/latest)**.
2. **Extract** `reborn_offline.py` and `loc_en.json` to:
   ```text
   /sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/
   ```
   > 🛡️ **Anti-Overwrite Trick:** Ensure an empty folder named `reborn_offline.py.tmp` exists inside `Documents/` to prevent the game engine from replacing the mod (guide: [Bahasa Indonesia](INSTALL_ID.md#%EF%B8%8F-cara-membuat-folder-anti-overwrite-tmp) · [English](INSTALL_EN.md#%EF%B8%8F-how-to-create-the-anti-overwrite-folder-tmp)).
3. **Launch the game!** Lobby, shop, heroes, skills, and combat will automatically load in English.

---

## 📸 In-Game Screenshots · Tangkapan Layar

<table>
<tr>
<td align="center" width="50%"><img src="docs/screenshots/01_hero_profile_thor.jpg" alt="Thor Hero Profile"/><br/><b>Hero Profile (Thor)</b></td>
<td align="center" width="50%"><img src="docs/screenshots/03_hero_select_spiderman.jpg" alt="Spider-Man Select"/><br/><b>Hero Select (Spider-Man)</b></td>
</tr>
<tr>
<td align="center" width="50%"><img src="docs/screenshots/04_equipment_plan.jpg" alt="Equipment Plan"/><br/><b>Equipment Plan & Stats</b></td>
<td align="center" width="50%"><img src="docs/screenshots/02_game_mode_select.jpg" alt="Game Mode Select"/><br/><b>Game Mode Selection</b></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="docs/screenshots/05_match_loading_heroes.jpg" alt="Match Loading Heroes" width="100%"/><br/><b>10 Heroes Named in English on Match Loading Screen</b></td>
</tr>
</table>

> View all images & descriptions → [docs/screenshots/](docs/screenshots/)

---

## ✨ Features · Fitur Mod

- ⚡ **Native Rust ARM64 Hooking (`native-rust/`)**: Sub-microsecond $O(1)$ static hashmap lookup across 5,594+ strings, single-cycle ASCII bypass, and inline trampolines on `cocos2d::ui::Text::setString` and `Button::setTitleText`.
- 🛡️ **Android 15+ 16KB Page-Size Compliant**: Built with `-Wl,-z,max-page-size=16384` for modern Android kernels.
- 🏷️ **English App Launcher Label**: Patched binary `resources.arsc` renaming Chinese title `漫威超级战争` to `Marvel Super War`.
- 🦸 **83 Marvel Heroes Translated**: Thor, Iron Man, Spider-Man, Captain America, Thanos, Magneto, Storm, Wolverine, etc.
- 🛒 **Complete In-Game Shop & Mall Translation**: Hero names, skin galleries, purchase confirmation modals, filter tabs.
- 🗺️ **Lobby Navigation Tabs**: *Heroes*, *Equipment*, *Preparation*, *Store*, *Events*.
- ⚔️ **Hero Select & Match Loading Screen**: All 10 hero names translated in loading screens and battle HUD.
- 🧬 **Energy Core & Talent Presets**: *General Burst*, *Sustained Combat*, *Defense Cooldown*, *Survival Support*.
- 🛡️ **Equipment Item Stats**: HP, Physical Defense, Energy Attack, Attack Speed, CDR, etc.
- 🚀 **Multi-Stage Cascade Sweeper**: Scheduled sweeps (0.05s, 0.25s, 0.60s) in Python catching dynamic animated widgets without periodic polling stutters.
- 🔒 **Safe & Non-Destructive**: No root required, fully reversible anytime.

---

## ❓ FAQ · Pertanyaan Umum

<details>
<summary><b>🇮🇩 Bahasa Indonesia</b></summary>

<br/>

**Q: Apa perbedaan memakai APK Standalone (Rust) dibanding copy file ke `Android/data`?**  
> APK Standalone menyertakan engine native Rust ARM64 langsung di dalam game (`liblocnative.so`) dan mengubah nama ikon di HP menjadi "Marvel Super War". Teks diterjemahkan di level memori sebelum sempat digambar ke layar, menghasilkan performa tercepat (0 latency). Metode copy file hanya memakai script Python sebagai fallback.

**Q: Apakah butuh HP yang sudah di-root?**  
> Tidak! Kedua metode sama sekali tidak membutuhkan akses root.

**Q: Apakah game akan lag atau patah-patah?**  
> Tidak. Dengan interseptor Rust ARM64, proses pencarian kata berjalan $O(1)$ (<1 mikrodetik) dengan bypass ASCII instan, menjaga gameplay mulus hingga 165 FPS.

**Q: Bagaimana cara menghapus / uninstall mod?**  
> Untuk APK Standalone: Cukup uninstall game seperti aplikasi biasa.  
> Untuk metode Documents: Hapus file `reborn_offline.py` dari folder `Documents/` game.

</details>

<details>
<summary><b>🇬🇧 English</b></summary>

<br/>

**Q: What is the difference between the Standalone APK (Rust) and the Documents hot-drop?**  
> The Standalone APK embeds the compiled Rust ARM64 engine (`liblocnative.so`) and patches the Android launcher title to "Marvel Super War". Translations happen at the native C++ level before rendering. The Documents hot-drop relies on Python runtime traversal as a non-repacking fallback.

**Q: Does this mod require root?**  
> No! Neither method requires root access.

**Q: Will this cause lag or FPS drops?**  
> No. The Rust engine executes $O(1)$ in-memory lookups (<1 microsecond) with single-cycle ASCII bypass, preserving peak framerates up to 165 FPS.

**Q: How do I uninstall the mod?**  
> Standalone APK: Simply uninstall the application from Android settings.  
> Documents method: Delete `reborn_offline.py` from the `Documents/` folder.

</details>

---

## 🛠️ Developer & Architecture Toolkit

<details>
<summary><b>🔍 Technical Architecture (Click to expand)</b></summary>

### 1. Dual-Engine Breakdown
- **Native C++/Rust Layer (`native-rust/`)**:
  - Compiles to `lib/arm64-v8a/liblocnative.so`.
  - Injected into `libclient.so` ELF header via `patchelf --add-needed liblocnative.so`.
  - Installs inline ARM64 trampolines on `cocos2d::ui::Text::setString` (`0xe1463c`) and `cocos2d::ui::Button::setTitleText` (`0xde7ed4`).
  - Hardware cache flushing via direct ARM64 instructions (`dc cvau`, `ic ivau`, `dsb ish`, `isb`).
- **Python Scripting Layer (`assets/Documents/reborn_offline.py`)**:
  - Embedded Python 2.7.3 inside NetEase NeoX.
  - In-memory `GameData` patching (`HeroSkinProto` with 83 heroes, `SkinProto` with 310 skins).
  - Offline match emulation, AI bot spawning, and energy core presets.

### 2. Repository Documentation
- [BUILD.md](./BUILD.md) — Rust compilation & automated standalone APK builder guide.
- [GLOSSARY.md](./GLOSSARY.md) — Standardized character names, abilities, roles, and menu glossary.
- [STRINGS.csv](./STRINGS.csv) — 1,195 extracted Chinese string entries with IDs and translation contexts.
- [RECON.md](./RECON.md) — Technical reverse-engineering report on NeoX VFS and binary structures.
- [PATCH.md](./PATCH.md) — Proof of concept diffs and invariant verification log.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution and translation guidelines.
- [DISCLAIMER.md](./DISCLAIMER.md) — Legal notice and intellectual property policy.
- [LICENSE](./LICENSE) — MIT License.

</details>

---

## ⚖️ Legal Disclaimer

This project is an independent educational research and fan translation effort. It is not affiliated with, endorsed by, or sponsored by Marvel Entertainment, The Walt Disney Company, or NetEase, Inc. All game assets and trademarks belong to their respective owners. See [DISCLAIMER.md](./DISCLAIMER.md) for full details.

