#include <dlfcn.h>
#include <link.h>
#include <sys/mman.h>
#include <unistd.h>
#include <cstdint>
#include <cstring>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <cstdarg>
#include <cstdio>
#include "dictionary_data.h"

#define LOG_TAG "LOC_NATIVE"

typedef int (*log_print_t)(int prio, const char* tag, const char* fmt, ...);
static log_print_t g_android_log_print = nullptr;

static void log_msg(int prio, const char* fmt, ...) {
    if (!g_android_log_print) {
        g_android_log_print = (log_print_t)dlsym(RTLD_DEFAULT, "__android_log_print");
    }
    char buf[1024];
    va_list args;
    va_start(args, fmt);
    vsnprintf(buf, sizeof(buf), fmt, args);
    va_end(args);

    if (g_android_log_print) {
        g_android_log_print(prio, LOG_TAG, "%s", buf);
    } else {
        fprintf(stderr, "[%s] %s\n", LOG_TAG, buf);
    }
}

#define LOGI(...) log_msg(4, __VA_ARGS__)
#define LOGE(...) log_msg(6, __VA_ARGS__)

static uintptr_t g_libclient_base = 0;
static std::unordered_map<std::string, std::string> g_dict;
static std::vector<std::pair<std::string, std::string>> g_sorted_pairs;

// Function pointer types for original implementations
typedef void (*Text_setString_t)(void* self, const std::string& text);
typedef void (*Button_setTitleText_t)(void* self, const std::string& text);

static Text_setString_t orig_Text_setString = nullptr;
static Button_setTitleText_t orig_Button_setTitleText = nullptr;

// Trampoline storage page
static uint8_t* g_trampoline_page = nullptr;
static size_t g_trampoline_offset = 0;

static void* allocate_trampoline(size_t size) {
    if (!g_trampoline_page || g_trampoline_offset + size > 4096) {
        g_trampoline_page = (uint8_t*)mmap(NULL, 4096,
            PROT_READ | PROT_WRITE | PROT_EXEC,
            MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
        g_trampoline_offset = 0;
        if (g_trampoline_page == MAP_FAILED) {
            LOGE("Failed to allocate trampoline page!");
            return nullptr;
        }
    }
    void* ptr = g_trampoline_page + g_trampoline_offset;
    g_trampoline_offset += (size + 15) & ~15; // 16-byte align
    return ptr;
}

// Find base address of libclient.so from /proc/self/maps
static uintptr_t get_libclient_base() {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (!fp) {
        LOGE("Cannot open /proc/self/maps");
        return 0;
    }
    char line[512];
    uintptr_t base = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "libclient.so") && strstr(line, "r-xp")) {
            uintptr_t start, end;
            if (sscanf(line, "%lx-%lx", &start, &end) == 2) {
                base = start;
                break;
            }
        }
    }
    fclose(fp);
    return base;
}

static bool set_memory_writable(void* addr, size_t len, bool writable) {
    uintptr_t page_start = (uintptr_t)addr & ~(uintptr_t)4095;
    uintptr_t page_end = ((uintptr_t)addr + len + 4095) & ~(uintptr_t)4095;
    int prot = PROT_READ | PROT_EXEC | (writable ? PROT_WRITE : 0);
    return mprotect((void*)page_start, page_end - page_start, prot) == 0;
}

// Install ARM64 inline hook
// Returns pointer to trampoline callable as original function
static void* install_arm64_hook(void* target, void* hook) {
    if (!target || !hook) return nullptr;

    uint8_t* tramp = (uint8_t*)allocate_trampoline(64);
    if (!tramp) return nullptr;

    // 1. Copy first 16 bytes from target to trampoline
    memcpy(tramp, target, 16);

    // 2. Append jump from trampoline back to target + 16
    uint8_t* tramp_jump = tramp + 16;
    uint32_t ldr_x16_pc8 = 0x58000050; // LDR X16, #8
    uint32_t br_x16      = 0xd61f0200; // BR X16
    uint64_t target_cont = (uint64_t)target + 16;

    memcpy(tramp_jump, &ldr_x16_pc8, 4);
    memcpy(tramp_jump + 4, &br_x16, 4);
    memcpy(tramp_jump + 8, &target_cont, 8);

    // 3. Patch target function with jump to hook function
    if (!set_memory_writable(target, 16, true)) {
        LOGE("Failed to set memory writable at %p", target);
        return nullptr;
    }

    uint64_t hook_addr = (uint64_t)hook;
    uint8_t patch[16];
    memcpy(patch, &ldr_x16_pc8, 4);
    memcpy(patch + 4, &br_x16, 4);
    memcpy(patch + 8, &hook_addr, 8);

    memcpy(target, patch, 16);

    // Restore protection and flush CPU instruction caches
    set_memory_writable(target, 16, false);
    __builtin___clear_cache((char*)target, (char*)target + 16);
    __builtin___clear_cache((char*)tramp, (char*)tramp + 32);

    LOGI("Successfully hooked %p -> %p (tramp: %p)", target, hook, tramp);
    return (void*)tramp;
}

// Extract string data from libc++ std::string safely
static std::string get_string_view(const std::string& s) {
    return s;
}

// Fast string translation
static std::string translate_text(const std::string& text) {
    if (text.empty()) return text;

    // Direct match O(1)
    auto it = g_dict.find(text);
    if (it != g_dict.end()) {
        return it->second;
    }

    // Substring replacement for composite text
    std::string res = text;
    bool modified = false;
    for (const auto& pair : g_sorted_pairs) {
        size_t pos = 0;
        while ((pos = res.find(pair.first, pos)) != std::string::npos) {
            res.replace(pos, pair.first.length(), pair.second);
            pos += pair.second.length();
            modified = true;
        }
    }
    return modified ? res : text;
}

// Hooked cocos2d::ui::Text::setString
static void hooked_Text_setString(void* self, const std::string& text) {
    std::string translated = translate_text(text);
    if (orig_Text_setString) {
        orig_Text_setString(self, translated);
    }
}

// Hooked cocos2d::ui::Button::setTitleText
static void hooked_Button_setTitleText(void* self, const std::string& text) {
    std::string translated = translate_text(text);
    if (orig_Button_setTitleText) {
        orig_Button_setTitleText(self, translated);
    }
}

static void init_dictionary() {
    g_dict.clear();
    g_sorted_pairs.clear();

    // Load initial 534 pairs
    for (const auto& p : g_initial_translations) {
        g_dict[p.first] = p.second;
        g_sorted_pairs.push_back(p);
    }

    // Sort by key length descending for accurate substring replacement
    std::sort(g_sorted_pairs.begin(), g_sorted_pairs.end(),
        [](const auto& a, const auto& b) {
            return a.first.length() > b.first.length();
        });

    LOGI("Loaded %zu translation entries into native dictionary.", g_dict.size());
}

// Constructor runs automatically when the shared library is loaded
__attribute__((constructor)) static void native_init() {
    LOGI("=== Initializing Marvel Super War Native Localization Hook ===");

    init_dictionary();

    g_libclient_base = get_libclient_base();
    if (!g_libclient_base) {
        LOGE("Could not find libclient.so base address!");
        return;
    }

    LOGI("Found libclient.so at base: 0x%lx", (unsigned long)g_libclient_base);

    // Target 1: cocos2d::ui::Text::setString at offset 0xe1463c
    void* target_Text_setString = (void*)(g_libclient_base + 0xe1463c);
    orig_Text_setString = (Text_setString_t)install_arm64_hook(
        target_Text_setString, (void*)hooked_Text_setString);

    // Target 2: cocos2d::ui::Button::setTitleText at offset 0xde7ed4
    void* target_Button_setTitleText = (void*)(g_libclient_base + 0xde7ed4);
    orig_Button_setTitleText = (Button_setTitleText_t)install_arm64_hook(
        target_Button_setTitleText, (void*)hooked_Button_setTitleText);

    if (orig_Text_setString && orig_Button_setTitleText) {
        LOGI("=== All Native C++ Hooks successfully installed! ===");
    } else {
        LOGE("Failed to install one or more native hooks.");
    }
}
