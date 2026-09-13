# -*- coding: utf-8 -*-
"""
translator.py — Internal Localization Engine for Marvel Super War
Designed for embedded NeoX Python 2.7 runtime.
Self-contained, decoupled from external mods.
"""

import sys
import re
import traceback

try:
    from locale_en import DICTIONARY as _ZH_TO_EN
except Exception:
    _ZH_TO_EN = {}

_SORTED_ZH_KEYS = tuple(sorted(_ZH_TO_EN.keys(), key=lambda k: -len(k)))

try:
    _UNICODE_TYPE = unicode
    _PY2 = True
except NameError:
    _UNICODE_TYPE = str
    _PY2 = False

_ACTIVE_PANELS = []
_gdata_patched = False


def log(*args):
    msg = "[NEOX_TRANSLATOR] " + " ".join([str(v) for v in args])
    try:
        print(msg)
    except Exception:
        pass


def _to_unicode(val):
    if val is None:
        return u""
    if isinstance(val, _UNICODE_TYPE):
        return val
    if hasattr(val, "decode"):
        for enc in ("utf-8", "gbk", "latin1"):
            try:
                return val.decode(enc)
            except Exception:
                pass
    try:
        return _UNICODE_TYPE(val)
    except Exception:
        return u""


def _to_str(val):
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if hasattr(val, "encode"):
        try:
            res = val.encode("utf-8")
            if isinstance(res, str):
                return res
        except Exception:
            pass
    if hasattr(val, "decode"):
        try:
            return val.decode("utf-8")
        except Exception:
            pass
    try:
        return str(val)
    except Exception:
        return ""


def translate(s):
    """Translate a Chinese string to its English equivalent."""
    if not s:
        return s
    uni_s = _to_unicode(s)
    if not uni_s:
        return s

    # Instant C-level ASCII check: if no characters >= 0x2e80, cannot match any Chinese entry
    if ord(max(uni_s)) < 0x2e80:
        return s

    if uni_s in _ZH_TO_EN:
        return _ZH_TO_EN[uni_s]

    stripped = uni_s.strip()
    if stripped in _ZH_TO_EN:
        rep = _ZH_TO_EN[stripped]
        return uni_s.replace(stripped, rep)

    # Whitespace-tolerant match for spaced button labels
    no_space = re.sub(r'[\s\u3000\u00a0\r\n]+', '', uni_s)
    if no_space in _ZH_TO_EN:
        return _ZH_TO_EN[no_space]

    has_cjk = any((0x3000 <= ord(c) <= 0x9fff) or (0xf900 <= ord(c) <= 0xffff) for c in uni_s)
    if not has_cjk:
        return s

    modified = False
    for zh in _SORTED_ZH_KEYS:
        if zh in uni_s:
            uni_s = uni_s.replace(zh, _ZH_TO_EN[zh])
            modified = True
            if ord(max(uni_s)) < 0x2e80:
                break

    return uni_s if modified else s


def safe_set_text(node, setter_name, en_text):
    """Set text on a node trying UTF-8 str and unicode, single and dual-arg."""
    setter = getattr(node, setter_name, None)
    if not callable(setter):
        return False
    en_s = _to_str(en_text)
    en_u = _to_unicode(en_text)
    for cand in (en_s, en_u):
        try:
            setter(cand)
            return True
        except TypeError:
            try:
                setter(cand, False)
                return True
            except Exception:
                pass
        except Exception:
            pass
    return False


def translate_node(node):
    """Translate text content of an individual UI node or widget."""
    if not node:
        return
    for get_fn, set_fn in (
        ("getString", "setString"),
        ("GetString", "SetString"),
        ("getText", "setText"),
        ("GetText", "SetText"),
        ("getStringValue", "setText"),
        ("getStringValue", "setString"),
        ("getTitleText", "setTitleText"),
        ("GetTitleText", "SetTitleText"),
        ("getTitle", "setTitle"),
        ("GetTitle", "SetTitle"),
        ("get_text", "set_text"),
        ("get_string", "set_string"),
        ("get_title", "set_title"),
        ("getPlaceHolder", "setPlaceHolder"),
        ("getDescription", "setDescription"),
    ):
        g = getattr(node, get_fn, None)
        if callable(g):
            try:
                txt = g()
                if txt:
                    en = translate(txt)
                    if en != txt:
                        safe_set_text(node, set_fn, en)
            except Exception:
                pass


def translate_tree(node, depth=0, max_depth=15, visited=None):
    """Recursively traverse and translate a UI node hierarchy."""
    if not node or depth > max_depth:
        return
    if visited is None:
        visited = set()
    node_id = id(node)
    if node_id in visited:
        return
    visited.add(node_id)

    try:
        translate_node(node)
    except Exception:
        pass

    # 1. Inner container for Cocos2d-x ScrollView / ListView / TableView
    for inner_fn in ("getInnerContainer", "GetInnerContainer", "get_inner_container"):
        ifn = getattr(node, inner_fn, None)
        if callable(ifn):
            try:
                inner = ifn()
                if inner:
                    translate_tree(inner, depth + 1, max_depth, visited)
                    break
            except Exception:
                pass

    # 2. Child collections (getChildren, getItems, getPages, getCells)
    for get_ch in ("getChildren", "GetChildren", "getItems", "GetItems", "getPages", "GetPages", "getCells", "GetCells"):
        cfn = getattr(node, get_ch, None)
        if callable(cfn):
            try:
                ch_list = cfn()
                if ch_list:
                    found_any = False
                    for child in ch_list:
                        found_any = True
                        try:
                            if child:
                                translate_tree(child, depth + 1, max_depth, visited)
                        except Exception:
                            pass
                    if found_any:
                        break
            except Exception:
                pass


def translate_panel(panel):
    """Translate all widgets on a panel or component instance."""
    if not panel:
        return
    visited = set()
    for attr in (
        "panel", "_panel", "root_node", "_root_node", "nod_root",
        "node", "_node", "ui_node", "_ui_node", "widget", "_widget",
        "main_node", "_main_node", "view", "_view", "table_view", "_table_view",
        "list_view", "_list_view", "scroll_view", "_scroll_view",
        "content_node", "_content_node", "cell_list", "_cell_list"
    ):
        root = getattr(panel, attr, None)
        if root:
            try:
                translate_tree(root, visited=visited)
            except Exception:
                pass

    try:
        translate_tree(panel, visited=visited)
    except Exception:
        pass

    try:
        for k in dir(panel):
            if k.startswith("_"):
                continue
            val = getattr(panel, k, None)
            if val is not None and val is not panel:
                translate_node(val)
                for sub_attr in ("panel", "_panel", "root_node", "node"):
                    sub_root = getattr(val, sub_attr, None)
                    if sub_root:
                        try:
                            translate_tree(sub_root, visited=visited)
                        except Exception:
                            pass
    except Exception:
        pass


def hook_component_init(comp_cls):
    """Safely hook __init__ on a component class."""
    if not comp_cls or not hasattr(comp_cls, "__init__") or hasattr(comp_cls, "_loc_orig_init"):
        return
    orig_init = comp_cls.__init__
    comp_cls._loc_orig_init = orig_init

    def localized_comp_init(self, *args, **kwargs):
        res = orig_init(self, *args, **kwargs)
        try:
            if self not in _ACTIVE_PANELS:
                _ACTIVE_PANELS.append(self)
            translate_panel(self)
        except Exception:
            pass
        return res

    comp_cls.__init__ = localized_comp_init


def patch_ui_localization():
    """Hook BasePanel and HallSceneComponent to auto-translate UI across all panels."""
    try:
        import ui.basepanel as basepanel
        cls = basepanel.BasePanel

        if hasattr(cls, "__init__") and not hasattr(cls, "_loc_orig_init"):
            cls._loc_orig_init = cls.__init__
            def localized_base_init(self, *args, **kwargs):
                res = cls._loc_orig_init(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.__init__ = localized_base_init

        if hasattr(cls, "init_panel") and not hasattr(cls, "_loc_orig_init_panel"):
            cls._loc_orig_init_panel = cls.init_panel
            def localized_init_panel(self, *args, **kwargs):
                res = cls._loc_orig_init_panel(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.init_panel = localized_init_panel

        if hasattr(cls, "show") and not hasattr(cls, "_loc_orig_show"):
            cls._loc_orig_show = cls.show
            def localized_show(self, *args, **kwargs):
                res = cls._loc_orig_show(self, *args, **kwargs)
                try:
                    if self not in _ACTIVE_PANELS:
                        _ACTIVE_PANELS.append(self)
                    translate_panel(self)
                except Exception:
                    pass
                return res
            cls.show = localized_show
        log("Hooked BasePanel lifecycle.")
    except Exception:
        pass

    # Hook known Hall components
    for comp_name in (
        "hall_scene_right_top", "hall_scene_left_center", "hall_scene_entry", "hall_scene_hero",
        "hall_scene_bottom", "hall_scene_left_bottom", "hall_scene_right_bottom",
        "hall_scene_bottom_left", "hall_scene_bottom_right", "hall_scene_bottom_center",
        "hall_scene_center", "hall_scene_top", "hall_scene_menu", "hall_scene_footer",
        "hall_scene_chat", "hall_scene_activity", "hall_scene_store", "hall_scene_prepare",
        "hall_scene_equip", "hall_scene_battle"
    ):
        try:
            mod = __import__("game_ui.dialog.hall.hs_components." + comp_name, fromlist=["HallSceneComponent"])
            comp = getattr(mod, "HallSceneComponent", None)
            if comp:
                hook_component_init(comp)
        except Exception:
            pass


def patch_hall_util():
    """Hook both.hall_util hero name helper functions safely."""
    try:
        import both.hall_util as hall_util
        for fn_name in ("getHeroName", "GetHeroName", "get_hero_name", "getHeroShortName", "GetHeroShortName"):
            orig_fn = getattr(hall_util, fn_name, None)
            if callable(orig_fn) and not hasattr(orig_fn, "_is_loc_hooked"):
                def make_wrapper(f):
                    def hooked(*args, **kwargs):
                        res = f(*args, **kwargs)
                        if res:
                            en = translate(res)
                            if isinstance(res, str):
                                return _to_str(en)
                            return _to_unicode(en)
                        return res
                    hooked._is_loc_hooked = True
                    return hooked
                setattr(hall_util, fn_name, make_wrapper(orig_fn))
                log("Hooked hall_util." + fn_name)
    except Exception:
        pass


def patch_gdata_translations():
    """Patch hero, skin, skill, and equip names across live gdata proto tables."""
    global _gdata_patched
    try:
        import game_env
        inst = game_env.GetInstance()
        if not inst:
            return False
        gdata = getattr(inst, "game_data", None)
        if not gdata:
            return False

        all_tables = {}
        for attr in ("_all_proto", "_protos", "protos", "proto_dict", "_proto_dict", "data", "_data"):
            d = getattr(gdata, attr, None)
            if isinstance(d, dict):
                for k, v in d.items():
                    if k not in all_tables:
                        try:
                            iter(v)
                            all_tables[k] = v
                        except TypeError:
                            pass

        KNOWN_PROTOS = (
            "HeroSkinProto", "SkinProto", "HeroProto", "HeroBasicProto",
            "HeroInfoProto", "HeroDataProto", "HeroCardProto", "HeroBaseProto",
            "EquipProto", "EquipSchemeProto", "SkillProto", "SkillDescProto",
            "MatchUIProto", "MapInfoProto", "MapRuleProto", "AIMapProto",
        )
        for name in KNOWN_PROTOS:
            for fn_name in ("GetAllProtoByName", "FindProto"):
                m = getattr(gdata, fn_name, None)
                if callable(m):
                    try:
                        p = m(name)
                        if p is not None:
                            all_tables[name] = p
                            break
                    except Exception:
                        pass

        fields = ("show_name", "skin_name", "name", "hero_name", "title", "short_name", "desc", "skill_name")
        total_translated = 0

        for tname, tbl in all_tables.items():
            try:
                rows = list(tbl.items())
            except Exception:
                continue

            for row_id, row in rows:
                if row is None:
                    continue
                for f in fields:
                    val = None
                    try:
                        val = row[f]
                    except (KeyError, TypeError):
                        pass
                    if val is None:
                        try:
                            val = getattr(row, f, None)
                        except Exception:
                            pass
                    if not val:
                        continue
                    if not isinstance(val, (_UNICODE_TYPE, bytes if _PY2 else str)):
                        continue
                    en = translate(val)
                    en_u = _to_unicode(en)
                    val_u = _to_unicode(val)
                    if en_u == val_u:
                        continue
                    en_s = _to_str(en_u)
                    wrote = False
                    for cand in (en_s, en_u):
                        if wrote:
                            break
                        for setter in ("item_set", "dict_set", "attr_set"):
                            try:
                                if setter == "item_set":
                                    row[f] = cand
                                elif setter == "attr_set":
                                    setattr(row, f, cand)
                                wrote = True
                                total_translated += 1
                                break
                            except Exception:
                                pass

        if total_translated > 0:
            _gdata_patched = True
            log("Translated %d fields across gdata proto tables." % total_translated)
            return True
    except Exception:
        log("patch_gdata_translations error:", traceback.format_exc())
    return False


def setup():
    """Main initialization hook called by assets/script/init.py."""
    log("Initializing NeoX Internal Translator...")
    try:
        patch_ui_localization()
        patch_hall_util()
    except Exception:
        log("Error setting UI hooks:", traceback.format_exc())

    # Try patching gdata immediately
    if not patch_gdata_translations():
        # If gdata is not ready yet, schedule deferred checks via Timer
        try:
            import Timer
            for delay in (1.0, 2.5, 5.0, 8.0, 12.0):
                Timer.addTimer(delay, patch_gdata_translations)
            log("Registered deferred gdata translation timers.")
        except Exception:
            pass

    log("NeoX Internal Translator initialized successfully.")
