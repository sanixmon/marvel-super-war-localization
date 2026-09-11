# Installation Guide · Panduan Pemasangan

> Marvel Super War — English Localization Mod (`reborn_offline.py`)

---

## 🇮🇩 Bahasa Indonesia

### Persyaratan

| Kebutuhan | Detail |
|-----------|--------|
| Game | Marvel Super War (CN) versi offline/modded |
| Runtime | Python 2.7.3 tertanam di engine NeoX |
| Akses | Izin baca/tulis ke folder Documents game |
| Tidak perlu | Root, APK repack, atau koneksi internet |

### Langkah Pemasangan

**1. Unduh script**

Unduh file `reborn_offline.py` dari halaman [Releases](../../releases) terbaru.

**2. Salin ke perangkat**

Pindahkan file ke path berikut di HP kamu:

```
/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py
```

> **Catatan penting:** Folder `.tmp` di dalam direktori `Documents/` harus tetap ada.  
> Jangan hapus atau ubah nama folder `reborn_offline.py.tmp` jika ada.

**3. Jalankan game**

Buka Marvel Super War. Script akan berjalan otomatis saat lobby dimuat.

**4. Verifikasi**

Tanda mod aktif: tab lobby berubah menjadi **Heroes · Equipment · Preparation · Store · Events** (bahasa Inggris).

### Fitur yang Diterjemahkan

- ✅ Nama semua hero (83 hero)
- ✅ Tab utama lobby (Heroes, Equipment, Preparation, Store, Events)
- ✅ Nama skin hero
- ✅ Mode permainan (Custom Match, AI Battle, dll.)
- ✅ Profil energy-core (General Burst, Sustained Combat, Defense Cooldown, Survival Support)
- ✅ Antarmuka pilih hero (Hero Select)
- ✅ UI informasi pertandingan

### Pemecahan Masalah

| Masalah | Solusi |
|---------|--------|
| Teks masih China setelah load | Keluar ke lobby lalu masuk kembali |
| Script tidak berjalan | Pastikan path file sudah tepat, cek izin file |
| Game crash saat start | Periksa apakah versi game kompatibel |

---

## 🇬🇧 English

### Requirements

| Requirement | Details |
|-------------|---------|
| Game | Marvel Super War (CN) offline/modded build |
| Runtime | Python 2.7.3 embedded in NeoX engine |
| Access | Read/write permission to the game's Documents folder |
| Not required | Root, APK repacking, or internet connection |

### Installation Steps

**1. Download the script**

Download `reborn_offline.py` from the latest [Releases](../../releases) page.

**2. Copy to device**

Move the file to the following path on your device:

```
/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py
```

> **Important:** The `.tmp` folder inside the `Documents/` directory must remain intact.  
> Do not delete or rename the `reborn_offline.py.tmp` folder if it exists.

**3. Launch the game**

Open Marvel Super War. The script runs automatically when the lobby loads.

**4. Verify**

The mod is active when lobby tabs read **Heroes · Equipment · Preparation · Store · Events** in English.

### Translated Content

- ✅ All hero names (83 heroes)
- ✅ Main lobby tabs (Heroes, Equipment, Preparation, Store, Events)
- ✅ Hero skin names
- ✅ Game modes (Custom Match, AI Battle, etc.)
- ✅ Energy-core presets (General Burst, Sustained Combat, Defense Cooldown, Survival Support)
- ✅ Hero select screen
- ✅ Match info UI

### Troubleshooting

| Issue | Fix |
|-------|-----|
| Text still Chinese after load | Exit to lobby and re-enter |
| Script not running | Verify the file path is correct and file is readable |
| Game crashes on start | Check if your game build version is compatible |

---

## File Structure · Struktur File

```
Documents/
└── reborn_offline.py        ← mod script (this file)
```

The script is self-contained — no additional files needed.  
Script ini berdiri sendiri — tidak perlu file tambahan.

---

## Credits

- Localization data sourced from Marvel Super War's own English string tables and community-sourced hero name mappings.
- Developed for offline/custom server builds only. Not affiliated with NetEase or Marvel.
