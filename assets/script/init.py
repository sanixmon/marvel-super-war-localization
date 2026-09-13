# -*- coding: utf-8 -*-
"""
init.py — NeoX Bootloader Entry Point with Integrated Localization Hook.
Executed directly by NeoX engine NXDiscreteFileLoader during startup.
"""

import sys
import traceback


def log(*args):
    try:
        print("[BOOT_INIT] " + " ".join([str(v) for v in args]))
    except Exception:
        pass


log("NeoX Custom Bootloader starting...")

# Step 1: Initialize Translator
try:
    import translator
    translator.setup()
    log("Translator setup completed.")
except Exception:
    log("Translator setup failed:", traceback.format_exc())

# Step 2: Chain-load the original init.py from script.npk
orig_code = None
try:
    import package
    # In NeoX, package.npkpackage takes name without .npk extension, fromAsset=True
    pkg = package.npkpackage("script", fromAsset=True)
    orig_code = pkg.get_file("\\init.py")
    if not orig_code:
        orig_code = pkg.get_file("init.py")
    if orig_code:
        log("Successfully retrieved original init.py from script.npk (npkpackage).")
except Exception:
    log("Could not load init.py via package.npkpackage:", traceback.format_exc())

if not orig_code:
    try:
        import package
        nx = package.nxnpk("script", fromAsset=True)
        orig_code = nx.get_file("\\init.py")
        if not orig_code:
            orig_code = nx.get_file("init.py")
        if orig_code:
            log("Successfully retrieved original init.py via package.nxnpk.")
    except Exception:
        log("Could not load init.py via package.nxnpk:", traceback.format_exc())

# Step 3: Execute original init.py to start game engine normal flow
if orig_code:
    log("Executing original init.py...")
    try:
        compiled_init = compile(orig_code, "orig_init.py", "exec")
        exec(compiled_init, globals(), locals())
        log("Original init.py execution finished.")
    except Exception:
        log("Error executing original init.py:", traceback.format_exc())
else:
    log("WARNING: Original init.py not found in script.npk. Engine will proceed with standard import.")
