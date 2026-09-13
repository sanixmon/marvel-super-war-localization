#!/usr/bin/env bash
# ==============================================================================
# Marvel Super War - English Standalone Patch Script for Termux / Linux
# ==============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}    Marvel Super War - Standalone English Patch     ${NC}"
echo -e "${BLUE}====================================================${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check tools
echo -e "\n${YELLOW}[1/4] Memeriksa tools (zip, zipalign, apksigner)...${NC}"
MISSING_TOOLS=()
for tool in zip zipalign apksigner; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo -e "${YELLOW}Tools belum lengkap: ${MISSING_TOOLS[*]}.${NC}"
    if command -v pkg &> /dev/null; then
        echo -e "${YELLOW}Menginstall via pkg (Termux)...${NC}"
        pkg update -y && pkg install -y zip zipalign apksigner
    else
        echo -e "${RED}Error: Harap install ${MISSING_TOOLS[*]} terlebih dahulu.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}[✓] Semua tools siap.${NC}"

# 2. Locate original APK
echo -e "\n${YELLOW}[2/4] Mencari file original APK...${NC}"
SRC_APK="$1"

if [ -z "$SRC_APK" ]; then
    # Cari di folder sekarang atau folder Download HP
    SEARCH_PATHS=(
        "./marvel_by_sfys.apk"
        "$HOME/storage/shared/Download/marvel_by_sfys.apk"
        "/sdcard/Download/marvel_by_sfys.apk"
        "/storage/emulated/0/Download/marvel_by_sfys.apk"
    )
    for p in "${SEARCH_PATHS[@]}"; do
        if [ -f "$p" ]; then
            SRC_APK="$p"
            break
        fi
    done
fi

if [ -z "$SRC_APK" ] || [ ! -f "$SRC_APK" ]; then
    echo -e "${YELLOW}Masukkan path file APK original (misal: /sdcard/Download/marvel_by_sfys.apk):${NC}"
    read -r -p "Path APK: " USER_INPUT_APK
    SRC_APK="$USER_INPUT_APK"
fi

if [ ! -f "$SRC_APK" ]; then
    echo -e "${RED}[!] Error: File APK tidak ditemukan di: $SRC_APK${NC}"
    exit 1
fi
echo -e "${GREEN}[✓] APK sumber ditemukan: $SRC_APK${NC}"

# Tentukan direktori output
DIRNAME="$(dirname "$SRC_APK")"
OUT_APK="$DIRNAME/marvel_english_standalone.apk"
TMP_WORK="$DIRNAME/tmp_modding.apk"
TMP_ALIGNED="$DIRNAME/tmp_aligned.apk"

echo -e "\n${YELLOW}[3/4] Menginjeksi file translasi & patch native...${NC}"
echo "Menyalin APK sumber..."
cp "$SRC_APK" "$TMP_WORK"

echo "Menginjeksi lib/ dan assets/ (uncompressed)..."
zip -0 -u "$TMP_WORK" \
    assets/neox.xml \
    assets/script/init.py \
    assets/script/translator.py \
    assets/script/locale_en.py \
    lib/arm64-v8a/libclient.so \
    lib/arm64-v8a/liblocnative.so

echo "Menghapus sertifikat lama (META-INF)..."
zip -d "$TMP_WORK" "META-INF/*" 2>/dev/null || true

echo -e "\n${YELLOW}[4/4] Zipalign & Penandatanganan APK (v1+v2+v3)...${NC}"
echo "Menyelaraskan memori (4-byte zipalign)..."
zipalign -p -f 4 "$TMP_WORK" "$TMP_ALIGNED"

echo "Menandatangani APK dengan debug keystore..."
KEYSTORE="$SCRIPT_DIR/debug.keystore"
if [ ! -f "$KEYSTORE" ]; then
    echo "Membuat debug keystore baru..."
    keytool -genkey -v -keystore "$KEYSTORE" -alias androiddebugkey \
        -storepass android -keypass android -keyalg RSA -keysize 2048 \
        -validity 10000 -dname "CN=Android Debug,O=Android,C=US"
fi

apksigner sign \
    --ks "$KEYSTORE" \
    --ks-key-alias androiddebugkey \
    --ks-pass pass:android \
    --key-pass pass:android \
    --out "$OUT_APK" \
    "$TMP_ALIGNED"

rm -f "$TMP_WORK" "$TMP_ALIGNED"

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}[✓] SUKSES! File APK modifikasi berhasil dibuat:${NC}"
echo -e "${GREEN}    $OUT_APK${NC}"
echo -e "${GREEN}====================================================${NC}"
echo -e "Silakan buka File Manager di HP Anda di folder Download dan langsung install APK tersebut!"
