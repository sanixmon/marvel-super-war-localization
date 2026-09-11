# Contributing to Marvel Super War Localization

Thank you for your interest in helping translate and maintain this localization project! Community contributions are welcome, whether you are improving translations, maintaining terminology consistency, or updating tooling for newer game versions.

---

## Code of Conduct
This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How to Contribute

### 1. Improving or Adding Translations
All in-game strings and UI resources are tracked in [STRINGS.csv](STRINGS.csv).
When contributing translations:
- **Consult the Glossary**: Check [GLOSSARY.md](GLOSSARY.md) first to ensure consistent terminology for Marvel characters, skill mechanics, roles, and UI buttons.
- **Preserve Formatting & Placeholders**:
  - Keep escape sequences intact (`\n`, `\t`, etc.).
  - Never alter variables or placeholders like `%s`, `%d`, `{0}`, or formatting tags.
  - *Example*: `欢迎来到%s` must translate to `Welcome to %s`.
- **Text Length Awareness**: English strings are typically longer than Chinese characters. Aim for concise, natural phrasing to prevent text clipping in UI dialogs.

### 2. Updating Tooling for New Game Releases
When NetEase releases a new game update:
1. Place the new APK in the directory as `marvel_by_sfys.apk`.
2. Run `python3 patch_poc.py` to verify that resource extraction, AAPT2 rebuilding, and signing still function.
3. If new strings were introduced, diff them and add them to `STRINGS.csv`.
4. Open a Pull Request documenting the new game version code/name tested.

---

## Pull Request Guidelines
Before submitting a Pull Request:
1. **No Binaries**: Ensure your PR contains **ZERO** `.apk`, `.idsig`, `.so`, or other binary files. Any PR containing compiled game packages will be closed immediately.
2. **Clean Diffs**: Keep commits focused and descriptive (e.g., `i18n: translate combat HUD strings` or `feat: update patcher for v3.23`).
3. **Encoding**: Ensure all text files are encoded in standard **UTF-8**.
