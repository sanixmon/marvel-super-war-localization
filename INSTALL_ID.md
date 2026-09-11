# Panduan Pemasangan

> Marvel Super War — Mod Lokalisasi Bahasa Inggris (`reborn_offline.py`)

🇬🇧 English version → [INSTALL_EN.md](INSTALL_EN.md)

---

## Persyaratan

| Kebutuhan | Detail |
|-----------|--------|
| Game | Marvel Super War (CN) versi offline/modded |
| Runtime | Python 2.7.3 tertanam di engine NeoX |
| Akses | Izin baca/tulis ke folder Documents game |
| Tidak perlu | Root, APK repack, atau koneksi internet |

---

## Langkah Pemasangan

**1. Unduh script**

Download file `reborn_offline.py` dari halaman **[Releases](../../releases)** terbaru.

**2. Salin ke perangkat**

Pindahkan file ke path berikut di HP kamu:

```
/sdcard/Android/data/com.netease.g104.cn/files/Netease/g104/Documents/reborn_offline.py
```

> **⚠️ Penting:** Folder `.tmp` di dalam direktori `Documents/` harus tetap ada.  
> Jangan hapus atau ubah nama folder `reborn_offline.py.tmp` jika ada.

**3. Jalankan game**

Buka Marvel Super War. Script berjalan otomatis saat lobby dimuat.

**4. Verifikasi**

Mod aktif jika tab lobby berubah menjadi:  
**Heroes · Equipment · Preparation · Store · Events**

---

## Fitur yang Diterjemahkan

- ✅ Nama semua hero (83 hero)
- ✅ Tab utama lobby (Heroes, Equipment, Preparation, Store, Events)
- ✅ Nama skin hero
- ✅ Mode permainan (VS A.I., Tutorial, dll.)
- ✅ Profil energy-core (General Burst, Sustained Combat, Defense Cooldown, Survival Support)
- ✅ Antarmuka pilih hero (Hero Select)
- ✅ Stat item (HP, Physical Def, HP Regen, dll.)

---

## Pemecahan Masalah

| Masalah | Solusi |
|---------|--------|
| Teks masih China setelah load | Keluar ke lobby lalu masuk kembali |
| Script tidak berjalan | Pastikan path file sudah benar, cek izin file |
| Game crash saat start | Periksa apakah versi game kompatibel |

---

## Struktur File

```
Documents/
└── reborn_offline.py    ← script mod (file ini saja)
```

Script ini berdiri sendiri — tidak perlu file tambahan.

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
