# Installation Guide

> Marvel Super War — English Localization Mod (`reborn_offline.py`)

🇮🇩 Versi Bahasa Indonesia → [INSTALL_ID.md](INSTALL_ID.md)

---

## Requirements

| Requirement | Details |
|-------------|---------|
| Game | Marvel Super War (CN) offline/modded build |
| Runtime | Python 2.7.3 embedded in NeoX engine |
| Access | Read/write permission to the game's Documents folder |
| Not required | Root, APK repacking, or internet connection |

---

## Installation Steps

**1. Download the script**

Download `reborn_offline.py` from the latest **[Releases](../../releases)** page.

**2. Copy to device**

Move the file to this exact path on your device:

```
/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py
```

> **⚠️ Important — Anti-Overwrite Trick:**  
> The game may automatically overwrite the mod if the `reborn_offline.py.tmp` folder is missing. Follow the steps below to create it if it doesn't already exist.

### 🛡️ How to Create the Anti-Overwrite Folder (`.tmp`)

The NetEase game engine attempts to re-download the original file to a temporary file named `reborn_offline.py.tmp` before overwriting the mod. By creating a **FOLDER** (directory) named exactly `reborn_offline.py.tmp`, the filesystem blocks the temporary file creation, preventing the game from overwriting the mod!

**Steps using any File Manager (ZArchiver / MT Manager / Stock File Manager):**
1. Navigate to the game folder:  
   `/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/`
2. Check if a folder named `reborn_offline.py.tmp` already exists.
3. **If it does not exist:**
   - Tap the **+** (Add) button or the three-dot menu.
   - Choose **New Folder**.
   - Name it exactly:  
     `reborn_offline.py.tmp`
   - Save. Make sure it is created as a **FOLDER / Directory**, not a regular text file.

**Or via Terminal / Termux / ADB:**
```bash
mkdir -p "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py.tmp"
```

Final folder structure inside `Documents/`:
```text
Documents/
├── reborn_offline.py       ← Mod script file
└── reborn_offline.py.tmp/  ← Empty folder (blocks auto-overwrite)
```

---

**3. Launch the game**

Open Marvel Super War. The script runs automatically when the lobby loads.

**4. Verify**

The mod is active when lobby tabs read:  
**Heroes · Equipment · Preparation · Store · Events**

---

## Translated Content

- ✅ All hero names (83 heroes)
- ✅ Main lobby tabs (Heroes, Equipment, Preparation, Store, Events)
- ✅ Hero skin names
- ✅ Game modes (VS A.I., Tutorial, etc.)
- ✅ Energy-core presets (General Burst, Sustained Combat, Defense Cooldown, Survival Support)
- ✅ Hero select screen
- ✅ Item stats (HP, Physical Def, HP Regen, etc.)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Text still Chinese after load | Exit to lobby and re-enter |
| Script not running | Verify the file path is correct and the file is readable |
| Game crashes on start | Check if your game build version is compatible |

---

## File Structure

```
Documents/
└── reborn_offline.py    ← mod script (this file only)
```

The script is self-contained — no additional files needed.

---

## Screenshots

<table>
<tr>
<td align="center"><img src="docs/screenshots/01_hero_profile_thor.jpg" width="320"/><br/><b>Hero Profile — Thor</b></td>
<td align="center"><img src="docs/screenshots/02_game_mode_select.jpg" width="320"/><br/><b>Game Mode Select</b></td>
</tr>
<tr>
<td align="center"><img src="docs/screenshots/03_hero_select_spiderman.jpg" width="320"/><br/><b>Hero Select — Spider-Man</b></td>
<td align="center"><img src="docs/screenshots/04_equipment_plan.jpg" width="320"/><br/><b>Equipment Plan Panel</b></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="docs/screenshots/05_match_loading_heroes.jpg" width="660"/><br/><b>Match Loading — 10 Heroes Named in English</b></td>
</tr>
</table>

> All screenshots → [docs/screenshots/](docs/screenshots/)

---

## Credits

- Localization data sourced from Marvel Super War's own English string tables and community-sourced hero name mappings.
- Developed for offline/custom server builds only. Not affiliated with NetEase or Marvel.
