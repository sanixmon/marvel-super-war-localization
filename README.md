# Marvel Super War — English Localization & Reverse-Engineering Toolkit
*(漫威超级战争 本地化与逆向工程工具包)*

[![Game](https://img.shields.io/badge/Game-Marvel%20Super%20War-blue.svg)](https://g104.163.com/)
[![Engine](https://img.shields.io/badge/Engine-NetEase%20NeoX%203.0-orange.svg)](#architecture)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

[English](#english) • [Bahasa Indonesia](#bahasa-indonesia)

---

<a name="english"></a>
## English

### 1. Overview
This repository contains reverse-engineering research, string datasets, terminology glossaries, and automated patch tooling for **Marvel Super War** (`com.netease.g104.cn`), NetEase's MOBA distributed for the Chinese market.

The objective is to produce an English localization patch while preserving:
- Original gameplay logic, networking, and authentication.
- Asset integrity and UI behavior.
- Anti-cheat and account safety (zero logic or DRM bypassing).

> **Note**: APK binaries are **NOT** hosted in this repository due to size (~3.1 GB) and licensing. All patches can be reproduced locally using the provided automated script.

---

### 2. Engine Architecture
- **Engine**: NetEase **NeoX 3D Game Engine** (`ppg3d` / NeoX 3.0).
- **Core Native Library**: `lib/arm64-v8a/libclient.so` (C++).
- **Scripting Runtime**: Embedded **Python 2.7.3** (custom bytecode opcodes).
- **GUI**: NetEase CocosUI / PyGame binding.
- **Archive Format**: NetEase NeoX Packages (`.npk` with Google CityHash64 filename indexing).
- **VFS Overrides**: The engine natively supports loose file overrides via `%DOC_DIR%\res` before falling back to internal APK assets.

---

### 3. How to Update for Future Game Versions (Contributor Guide)

If a new version of the game is released and you want to update the patch yourself, follow these 3 simple steps:

#### Step 1: Install Requirements
```bash
sudo apt-get install -y aapt aapt2 apktool zipalign apksigner openjdk-21-jdk zip python3
```

#### Step 2: Run the Automated Patcher
Place the new official APK as `marvel_by_sfys.apk` in this folder and run:
```bash
python3 patch_poc.py
```
This script automatically:
1. Extracts system resources via AAPT2 (skipping the 3.1 GB assets for speed).
2. Applies all translations from `STRINGS.csv` and XML configs.
3. In-place updates the resource table.
4. Performs 4-byte boundary `zipalign`.
5. Re-signs the APK with v1, v2, and v3 Android signature schemes.

#### Step 3: Translating Newly Added Strings
1. Compare new strings against [STRINGS.csv](./STRINGS.csv).
2. Consult [GLOSSARY.md](./GLOSSARY.md) for character names, items, and combat stats to maintain consistent terminology.
3. Review [CONTRIBUTING.md](./CONTRIBUTING.md) and submit a Pull Request!

---

### 4. Repository Structure
- [RECON.md](./RECON.md) — Detailed reverse-engineering report on NeoX, VFS loaders, and binary structure.
- [STRINGS.csv](./STRINGS.csv) — 1,195 extracted Chinese string entries with IDs and translation contexts.
- [GLOSSARY.md](./GLOSSARY.md) — Standardized character names, abilities, roles, and menu glossary.
- [PATCH.md](./PATCH.md) — Proof of concept diffs and invariant verification log.
- [BUILD.md](./BUILD.md) — Comprehensive manual reproduction and CLI signing guide.
- [patch_poc.py](./patch_poc.py) — Standalone automated patch and build script.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Translation guidelines and PR submission rules.
- [DISCLAIMER.md](./DISCLAIMER.md) — Legal notice, intellectual property, and fair-use policy.
- [LICENSE](./LICENSE) — MIT License.

---

### 5. Legal Notice
This project is an independent educational research and fan translation effort. It is not affiliated with, endorsed by, or sponsored by Marvel Entertainment, The Walt Disney Company, or NetEase, Inc. See [DISCLAIMER.md](./DISCLAIMER.md) for full intellectual property details.

---

<a name="bahasa-indonesia"></a>
## Bahasa Indonesia

### 1. Ringkasan
Repositori ini berisi riset reverse-engineering, dataset teks, glosarium terminologi, serta skrip patch otomatis untuk **Marvel Super War** (`com.netease.g104.cn`), game MOBA besutan NetEase untuk pasar Tiongkok.

Tujuan proyek ini adalah membuat patch translasi Bahasa Inggris yang aman tanpa merusak:
- Logika permainan, sistem jaringan, dan autentikasi akun.
- Kestabilan aset grafis dan tampilan antarmuka (UI).
- Keamanan anti-cheat (tidak membobol proteksi game).

> **Penting**: File biner APK **TIDAK** diunggah ke repositori ini karena ukurannya (~3.1 GB). Seluruh proses modifikasi dapat diproduksi ulang secara otomatis menggunakan skrip yang telah disediakan.

---

### 2. Arsitektur Engine Game
- **Engine**: NetEase **NeoX 3D Game Engine** (`ppg3d` / NeoX 3.0).
- **Core Library**: `lib/arm64-v8a/libclient.so` (C++).
- **Runtime Script**: Embedded **Python 2.7.3** (bytecode khusus NeoX).
- **GUI**: NetEase CocosUI / binding PyGame.
- **Format Paket**: NetEase NeoX Packages (`.npk` dengan hashing nama file Google CityHash64).
- **Sistem VFS**: Mendukung penimpaan aset terurai (loose files) via `%DOC_DIR%\res` tanpa harus mengemas ulang APK 3GB.

---

### 3. Panduan Update untuk Versi Baru (Untuk Kontributor)

Jika game mendapatkan pembaruan (update) resmi dan Anda ingin memperbarui patch sendiri:

#### Langkah 1: Pasang Kebutuhan Tool
```bash
sudo apt-get install -y aapt aapt2 apktool zipalign apksigner openjdk-21-jdk zip python3
```

#### Langkah 2: Jalankan Patcher Otomatis
Letakkan APK versi baru dengan nama `marvel_by_sfys.apk` di folder ini, lalu jalankan:
```bash
python3 patch_poc.py
```
Skrip ini akan otomatis:
1. Mengekstrak resource sistem tanpa membongkar 3.1 GB aset (proses cepat < 1 menit).
2. Memasukkan translasi teks.
3. Mengompilasi ulang tabel resource.
4. Menyelaraskan page memory 4-byte (`zipalign`).
5. Menandatangani APK dengan skema v1, v2, dan v3 (`apksigner`).

#### Langkah 3: Menambahkan Translasi Baru
1. Cek string baru yang belum ada di [STRINGS.csv](./STRINGS.csv).
2. Gunakan panduan nama hero dan istilah di [GLOSSARY.md](./GLOSSARY.md).
3. Baca aturan di [CONTRIBUTING.md](./CONTRIBUTING.md) lalu buat Pull Request (PR) ke repositori ini!

---

### 4. Peta File Repositori
- [RECON.md](./RECON.md) — Laporan teknis reverse-engineering engine NeoX dan VFS.
- [STRINGS.csv](./STRINGS.csv) — 1,195 baris string teks Mandarin terstruktur siap terjemah.
- [GLOSSARY.md](./GLOSSARY.md) — Glosarium resmi hero Marvel, peran, atribut, dan tombol menu.
- [PATCH.md](./PATCH.md) — Rincian modifikasi string POC dan pengujian biner.
- [BUILD.md](./BUILD.md) — Panduan langkah manual perakitan dan penandatanganan APK.
- [patch_poc.py](./patch_poc.py) — Skrip otomasi siap pakai untuk membangun APK hasil patch.
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Pedoman kontribusi terjemahan dan aturan PR.
- [DISCLAIMER.md](./DISCLAIMER.md) — Pernyataan hukum hak cipta, fair-use, dan non-afiliasi.
- [LICENSE](./LICENSE) — Lisensi lisensi terbuka MIT.

---

### 5. Pernyataan Hukum
Proyek ini merupakan inisiatif riset edukasi dan translasi komunitas independen, serta tidak berafiliasi dengan atau didukung oleh Marvel Entertainment, The Walt Disney Company, maupun NetEase, Inc. Rincian lengkap hak cipta dan merek dagang dapat dibaca di [DISCLAIMER.md](./DISCLAIMER.md).
