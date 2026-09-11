# RECONNAISSANCE REPORT: MARVEL SUPER WAR (漫威超级战争)

## 1. Application Metadata
- **Package Name**: `com.netease.g104.cn` (NetEase Internal Project Code: `g104`)
- **Version Code**: `135`
- **Version Name**: `3.22.2`
- **Platform Build**: Android SDK Target `28` (Android 9.0 Pie), Min SDK `21` (Android 5.0 Lollipop), Compile SDK `23`
- **Architectures Supported**: `arm64-v8a` (Primary 64-bit), `armeabi-v7a` (32-bit legacy)
- **APK Format**: Monolithic Standalone APK (~3.12 GB / 3,273,795,882 bytes)
- **Split APK**: No (single unified APK)
- **Launchable Activity**: `com.netease.ntunisdk.external.protocol.ProtocolLauncher`
- **Application Label**: `漫威超级战争`

---

## 2. Engine Architecture
- **Detected Engine**: **NetEase NeoX 3D Game Engine** (`ppg3d` / NeoX 3.0)
- **Confidence**: **100%**
- **Core Native Engine**: `lib/arm64-v8a/libclient.so` (48.5 MB)
- **Scripting Runtime**: Embedded **Python 2.7.3** (compiled with Conan, customized bytecode opcodes, `_Py_PackageContext`, `boost::python`)
- **GUI Framework**: NetEase **CocosUI** / Cocos2d-x 2.1 branch (`cocosui` configured in `assets/neox.xml`) + PyGame binding
- **Audio Middleware**: Audiokinetic **Wwise** (`<wwise>` in `neox.xml`) + **FMOD Event** (`libfmodevent.so`, `libfmodex.so`)
- **Video Engine**: Bink / IJKPlayer (`libijkplayer.so`, `libijkffmpeg.so`)
- **Font System**: Default system font specified in `assets/neox.xml`: `ui/cocos21/fonts/heiti.ttf`

---

## 3. APK File Layout & Asset Hierarchy
```
marvel_by_sfys.apk
├── AndroidManifest.xml          # Binary XML (Target SDK 28, permissions, activities)
├── classes.dex - classes6.dex   # 6 DEX files (UniSDK, mpay, push services, Android wrapper)
├── lib/
│   ├── arm64-v8a/libclient.so   # NeoX C++ game engine core & Python 2.7 runtime
│   └── armeabi-v7a/libclient.so
├── assets/
│   ├── neox.xml                 # NeoX engine boot configuration & VFS definitions
│   ├── res.npk                  # 84.24 MB (Core NeoX game resources)
│   ├── script.npk               # 20.02 MB (Compiled game Python scripts)
│   ├── res/
│   │   ├── gui.npk              # 688.41 MB (UI layouts, widgets, textures, HUD)
│   │   ├── fx.npk               # 238.93 MB (Visual effects)
│   │   ├── hero.npk             # 290.17 MB (Hero models & data)
│   │   └── ui_scene.npk         # 171.40 MB (UI 3D scene backgrounds)
│   └── Documents/               # In-app update / dynamic patch staging
│       ├── script.npk           # 3.22 MB (Script patch bundle)
│       ├── res.npk              # 42.19 MB (Resource patch bundle)
│       └── extend/hero_high/    # Hero high-res packages (e.g., 1001_meiguoduizhang.npk)
└── resources.arsc               # Compiled Android string pool & layout tables
```

---

## 4. Virtual File System (VFS) & Mount Hierarchy
Discovered in `assets/neox.xml`:
```xml
<filesystems>
    <filesystem name='res'>
        <loader name='npk' opener='sys' root='%DOC_DIR%es' depth='1'/>
        <loader name='discrete' opener='sys' root='%DOC_DIR%es'/>
        <loader name='npk' opener='asset' root='res' depth='1'/>
        <loader name='discrete' opener='sys' root='%WORK_DIR%es'/>
    </filesystem>
    <filesystem name='script'>
        <loader name='npk' opener='sys' root='%DOC_DIR%\script' depth='0'/>
        <loader name='npk' opener='asset' root='script'/>
    </filesystem>
</filesystems>
```
### Critical Localization Finding:
The NeoX engine supports a **`discrete` (loose file) loader** with higher priority than the APK assets:
1. `%DOC_DIR%es` (Loose files in app documents folder override APK assets without repacking)
2. `assets/res` (Fallback to APK packaged `.npk` files)

---

## 5. Localization Storage & Mechanisms
1. **Android System & SDK UI**:
   - Stored in `resources.arsc` across `res/values/`, `res/values-zh-rCN/`, `res/values-en/`.
   - Contains ~1,579 Chinese strings covering NetEase UniSDK login, payment, permission dialogs, and exit confirmations.
2. **In-Game Text (Heroes, Skills, Items, Quests, HUD)**:
   - Stored inside `assets/res/gui.npk` (CocosUI layouts) and `assets/script.npk` (Python localization dictionaries).
   - Filename lookup in NPK uses **Google CityHash64** truncated to uint32 (`FileUtils::hashFileName` in `libclient.so`).
3. **Typography**:
   - `ui/cocos21/fonts/heiti.ttf` contains full Unicode coverage (CJK + Latin glyphs). Latin characters render natively without font substitution.
