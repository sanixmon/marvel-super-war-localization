# Marvel Super War — English Localization Mod & Toolkit
*(漫威超级战争 英文本地化补丁与工具包)*

[![Latest Release](https://img.shields.io/github/v/release/sanixmon/marvel-super-war-localization?color=blue&label=Mod%20Release)](https://github.com/sanixmon/marvel-super-war-localization/releases/latest)
[![Game](https://img.shields.io/badge/Game-Marvel%20Super%20War%20(CN)-red.svg)](https://g104.163.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![No Root Required](https://img.shields.io/badge/Root-Not%20Required-success.svg)](#quick-installation)

English patch for **Marvel Super War** (`com.netease.g104.cn`) offline / custom server builds.  
**No root required. No 3GB APK repacking.** Just copy 1 small script and play in English!

---

## 🎮 Quick Download & Installation · Unduh & Pasang

| 🇬🇧 English | 🇮🇩 Bahasa Indonesia |
|---|---|
| 📥 **[Download Latest Mod (`reborn_offline.py`)](../../releases/latest)** | 📥 **[Unduh Mod Terbaru (`reborn_offline.py`)](../../releases/latest)** |
| 📖 **[Full Installation Guide (INSTALL_EN.md)](INSTALL_EN.md)** | 📖 **[Panduan Lengkap (INSTALL_ID.md)](INSTALL_ID.md)** |

### ⚡ 3-Step Setup (Cara Cepat):

1. **Download** `reborn_offline.py` from the latest [Releases](../../releases/latest).
2. **Copy** the file to this folder on your Android device (salin ke path ini di HP):
   ```text
   /sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py
   ```
   > ⚠️ **Catatan penting / Important:** Pastikan folder `reborn_offline.py.tmp` di dalam folder `Documents` **tetap ada** (jangan dihapus) agar game tidak menimpa script.
3. **Launch the game!** Lobby and heroes will automatically load in English.

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

- ✅ **83 Marvel Heroes Translated**: Thor, Iron Man, Spider-Man, Captain America, Thanos, dll.
- ✅ **Lobby Navigation Tabs**: *Heroes*, *Equipment*, *Preparation*, *Store*, *Events*.
- ✅ **Hero Select & Match Loading Screen**: Semua nama hero di kedua tim dalam bahasa Inggris.
- ✅ **Energy Core & Talent Presets**: *General Burst*, *Sustained Combat*, *Defense Cooldown*, *Survival Support*.
- ✅ **Equipment Item Stats**: HP, Physical Def, HP Regen, Attack, dll.
- ✅ **Smooth Performance (No Stutter)**: Versi rilis bebas polling loop sehingga FPS stabil (30–165 FPS).
- ✅ **Safe & Non-Destructive**: Tidak mengubah APK asli, tidak butuh root, mudah di-uninstall kapan saja (cukup hapus file `.py`).

---

## ❓ FAQ · Pertanyaan Umum

<details>
<summary><b>🇮🇩 Bahasa Indonesia</b></summary>

<br/>

**Q: Apakah butuh HP yang sudah di-root?**  
> Tidak! Kamu hanya butuh aplikasi file manager (seperti ZArchiver, MT Manager, atau bawaan HP) untuk menyalin file ke folder `Android/data`.

**Q: Apakah game akan lag atau patah-patah?**  
> Tidak. Versi rilis terbaru (`v1.0+`) sudah dioptimalkan tanpa background timer berulang, sehingga frame rate tetap mulus (support hingga 165 FPS).

**Q: Bagaimana cara menghapus / uninstall mod?**  
> Cukup hapus file `reborn_offline.py` dari folder `Documents/` game. Game akan kembali seperti semula.

**Q: Kenapa teks kembali bahasa Mandarin setelah update resource game?**  
> Pastikan folder `reborn_offline.py.tmp` di dalam direktori `Documents/` tidak terhapus. Folder ini mencegah engine game mendownload ulang script aslinya.

</details>

<details>
<summary><b>🇬🇧 English</b></summary>

<br/>

**Q: Does this mod require root?**  
> No! You only need a standard file manager (like ZArchiver or MT Manager) to paste the file into `Android/data`.

**Q: Will this cause lag or FPS drops?**  
> No. The production release (`v1.0+`) is fully optimized with zero background polling loops, maintaining smooth gameplay up to 165 FPS.

**Q: How do I uninstall the mod?**  
> Simply delete `reborn_offline.py` from the game's `Documents/` folder.

**Q: Why did text revert to Chinese after game update?**  
> Ensure the folder `reborn_offline.py.tmp` inside `Documents/` is still intact. This folder prevents the game engine from overwriting the modded script.

</details>

---

## 🛠️ Developer & Reverse Engineering Toolkit

> *Bagian ini ditujukan bagi developer, periset reverse engineering, atau kontributor yang ingin memodifikasi script dan resource.*

<details>
<summary><b>🔍 Technical Overview & Engine Architecture (Click to expand)</b></summary>

### 1. Game Architecture
- **Engine**: NetEase **NeoX 3D Engine** (`ppg3d` / NeoX 3.0)
- **Core Library**: `lib/arm64-v8a/libclient.so` (C++)
- **Scripting Runtime**: Embedded **Python 2.7.3** inside NeoX
- **Data Tables**: `both.data.data_main.GameData` (`HeroSkinProto` with 83 heroes, `SkinProto` with 310 skins)
- **UI Framework**: Cocos2d-x / CocosUI Python bindings (`cc.Director`, `cc.Label`, `ccui.Button`)

### 2. How the Mod Works
Instead of modifying the 3.1 GB encrypted APK, the mod hooks into the game's embedded Python runtime at boot:
1. Reads `HeroSkinProto` and `SkinProto` tables in memory and dynamically replaces Chinese name fields with English equivalents.
2. Intercepts CocosUI string setters (`setString`, `setTitleText`) with whitespace-tolerant Chinese dictionary lookup.
3. Automatically unlocks offline matchmaking and AI battle slots without server authentication.

### 3. Repository Documentation
- [GLOSSARY.md](./GLOSSARY.md) — Standardized character names, abilities, roles, and menu glossary.
- [STRINGS.csv](./STRINGS.csv) — 1,195 extracted Chinese string entries with IDs and translation contexts.
- [RECON.md](./RECON.md) — Technical reverse-engineering report on NeoX VFS and binary structures.
- [BUILD.md](./BUILD.md) — APK repacking & signing research guide (legacy method).
- [PATCH.md](./PATCH.md) — Proof of concept diffs and invariant verification log.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution and translation guidelines.
- [DISCLAIMER.md](./DISCLAIMER.md) — Legal notice and intellectual property policy.
- [LICENSE](./LICENSE) — MIT License.

</details>

---

## ⚖️ Legal Disclaimer

This project is an independent educational research and fan translation effort. It is not affiliated with, endorsed by, or sponsored by Marvel Entertainment, The Walt Disney Company, or NetEase, Inc. All game assets and trademarks belong to their respective owners. See [DISCLAIMER.md](./DISCLAIMER.md) for full details.
