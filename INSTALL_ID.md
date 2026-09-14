# Panduan Pemasangan

> Marvel Super War — Mod Lokalisasi Bahasa Inggris (`reborn_offline.py`)

🇬🇧 English version → [INSTALL_EN.md](INSTALL_EN.md)

---

## Pilihan Metode Pemasangan

Tersedia **2 cara pemasangan**:
1. **[Metode 1: Standalone Mod APK (Paling Mudah · Rekomendasi)](#-metode-1-standalone-mod-apk-rekomendasi-utama)** — Cukup 1x install APK, nama di launcher menjadi *"Marvel Super War"*, dan modul native Rust langsung aktif.
2. **[Metode 2: Manual Documents (Hot-Drop)](#-metode-2-manual-hot-drop-documents)** — Untuk yang sudah punya APK dan tidak ingin mengunduh ulang 3 GB.

---

## 🌟 Metode 1: Standalone Mod APK (Rekomendasi Utama)

Metode ini adalah cara termudah karena **tidak membutuhkan akses ke folder `Android/data`** yang sering diblokir oleh Android 11+.

### Keunggulan:
- ⚡ **Native Rust ARM64 Hook**: Terjemahan berjalan di memori RAM ($O(1)$) dengan kecepatan native C/Rust tanpa lag.
- 🏷️ **Nama Bahasa Inggris di Launcher**: Ikon di HP otomatis bernama **`Marvel Super War`** (bisa dicari di launcher dengan kata kunci *"Marvel"*).
- 🛡️ **Siap untuk Android 15**: Mendukung ukuran halaman memori 16KB.

### Langkah Pasang:
1. Unduh atau bangun file **`marvel_english_standalone.apk`** (lihat [BUILD.md](BUILD.md)).
2. Pasang APK ke perangkat Android Anda:
   - **Lewat Komputer (ADB)**:
     ```bash
     adb install -r marvel_english_standalone.apk
     ```
   - **Lewat HP Langsung**: Salin file APK ke memori HP (via USB/KDE Connect/Google Drive), lalu buka file APK di File Manager untuk memasangnya.
3. Buka game dan langsung mainkan dalam bahasa Inggris!

---

## 📂 Metode 2: Manual Hot-Drop Documents

Gunakan metode ini jika Anda sudah memiliki game versi asli terpasang dan hanya ingin menaruh script mod tanpa menginstal ulang file APK 3 GB.

### Persyaratan
| Kebutuhan | Detail |
|---|---|
| Game | Marvel Super War (CN) versi offline/modded |
| Runtime | Python 2.7.3 tertanam di engine NeoX |
| Akses | Izin baca/tulis ke folder Documents game |
| Tidak perlu | Root atau koneksi internet |

### Langkah Pemasangan:
**1. Unduh paket mod**  
Download file **`mod_documents.zip`** dari halaman **[Releases](../../releases)** terbaru.

**2. Salin ke perangkat**  
Ekstrak kedua file (`reborn_offline.py` dan `loc_en.json`) ke path folder Documents berikut di HP kamu:
```text
/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/
```

> **⚠️ Penting — Trik Anti-Overwrite:**  
> Game dapat otomatis menimpa mod jika folder `reborn_offline.py.tmp` tidak ada. Ikuti langkah di bawah untuk membuatnya jika belum ada.

### 🛡️ Cara Membuat Folder Anti-Overwrite (`.tmp`)

Game NetEase mencoba mendownload ulang file asli ke temporary file bernama `reborn_offline.py.tmp` sebelum menimpa mod. Dengan membuat **FOLDER** (direktori) bernama persis `reborn_offline.py.tmp`, game akan terblokir dan gagal menimpa mod kita!

**Langkah membuat lewat File Manager (ZArchiver / MT Manager / File Manager HP):**
1. Buka folder game:  
   `/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/`
2. Cek apakah folder bernama `reborn_offline.py.tmp` sudah ada.
3. **Jika belum ada:**
   - Tekan tombol **+** (Tambah) atau ikon menu titik tiga.
   - Pilih **Buat Folder Baru** (*New Folder*).
   - Beri nama persis:  
     `reborn_offline.py.tmp`
   - Simpan. Pastikan tipenya adalah **FOLDER / Direktori**, bukan file teks biasa.

**Atau lewat Terminal / Termux:**
```bash
mkdir -p "/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py.tmp"
```

Struktur folder akhir di dalam `Documents/`:
```text
Documents/
├── reborn_offline.py       ← File script mod runtime
├── loc_en.json             ← 5.590+ Kamus master translasi Inggris
└── reborn_offline.py.tmp/  ← Folder kosong (penahan overwrite)
```

---

**3. Jalankan game**

Buka Marvel Super War. Script berjalan otomatis saat lobby dimuat.

**4. Verifikasi**

Mod aktif jika tab lobby berubah menjadi:  
**Heroes · Equipment · Preparation · Store · Events**

---

## Fitur yang Diterjemahkan

- ✅ Nama semua hero (83 hero) & nama lengkap hero di shop
- ✅ Seluruh antarmuka Shop / Mall (kartu hero, skin, tombol beli, dialog konfirmasi)
- ✅ Tab utama lobby (Heroes, Equipment, Preparation, Store, Events)
- ✅ Patch tabel gdata in-memory: skill, pasif, buff, dan deskripsi item
- ✅ Galeri & nama skin hero
- ✅ Mode permainan (VS A.I., Ranked, Tutorial, dll.)
- ✅ Profil energy-core (General Burst, Sustained Combat, Defense Cooldown, Survival Support)
- ✅ Antarmuka pilih hero & match loading (semua 10 hero dalam bahasa Inggris)
- ✅ Stat item combat (HP, Physical Def, Energy Power, Atk Speed, CDR, dll.)

---

## Pemecahan Masalah

| Masalah | Solusi |
|---------|--------|
| Teks masih China setelah load | Keluar ke lobby lalu masuk kembali, atau pastikan `loc_en.json` ada di folder `Documents/` |
| Script tidak berjalan | Pastikan path file sudah benar, cek izin akses folder |
| Game crash saat start | Periksa apakah versi game kompatibel |

---

## Struktur File

```
Documents/
├── reborn_offline.py       ← Script mod
├── loc_en.json             ← Kamus master lokalisasi
└── reborn_offline.py.tmp/  ← Folder anti-overwrite
```

---

## Tangkapan Layar

<table>
<tr>
<td align="center"><img src="docs/screenshots/01_hero_profile_thor.jpg" width="320"/><br/><b>Profil Hero — Thor</b></td>
<td align="center"><img src="docs/screenshots/02_game_mode_select.jpg" width="320"/><br/><b>Pilih Mode Permainan</b></td>
</tr>
<tr>
<td align="center"><img src="docs/screenshots/03_hero_select_spiderman.jpg" width="320"/><br/><b>Pilih Hero — Spider-Man</b></td>
<td align="center"><img src="docs/screenshots/04_equipment_plan.jpg" width="320"/><br/><b>Panel Rencana Equipment</b></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="docs/screenshots/05_match_loading_heroes.jpg" width="660"/><br/><b>Loading Match — 10 Nama Hero Sudah Bahasa Inggris</b></td>
</tr>
</table>

> Semua screenshot → [docs/screenshots/](docs/screenshots/)

---

## Kredit

- Data lokalisasi diambil dari string table bahasa Inggris bawaan Marvel Super War dan pemetaan nama hero dari komunitas.
- Dikembangkan khusus untuk build offline/custom server. Tidak berafiliasi dengan NetEase atau Marvel.
