#include <jni.h>
#include <android/log.h>
#include <unistd.h>
#include <sys/mman.h>
#include <dlfcn.h>
#include <errno.h>
#include <string.h>

#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>

#include "dictionary_data.h"

#define TAG "LocHookNative"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,  TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN,  TAG, __VA_ARGS__)

static uintptr_t g_libclient_base = 0;
static std::unordered_map<std::string, std::string> g_dict;
static std::vector<std::pair<std::string, std::string>> g_sorted_pairs;

// Function pointer signatures for Cocos2d-x UI setters
// Target: void cocos2d::ui::Text::setString(const std::string& text)
typedef void (*Text_setString_t)(void* self, const std::string& text);
// Target: void cocos2d::ui::Button::setTitleText(const std::string& text)
typedef void (*Button_setTitleText_t)(void* self, const std::string& text);

static Text_setString_t orig_Text_setString = nullptr;
static Button_setTitleText_t orig_Button_setTitleText = nullptr;

// Set memory protection handling 4KB and 16KB page sizes
static bool set_memory_prot(void* addr, size_t len, int prot) {
    uintptr_t page_size = sysconf(_SC_PAGESIZE);
    if (page_size == 0) page_size = 4096;
    uintptr_t page_start = (uintptr_t)addr & ~(page_size - 1);
    uintptr_t page_end = ((uintptr_t)addr + len + page_size - 1) & ~(page_size - 1);
    int ret = mprotect((void*)page_start, page_end - page_start, prot);
    if (ret != 0) {
        LOGE("mprotect failed at %p (size %zu) with prot %d: %s",
             (void*)page_start, (size_t)(page_end - page_start), prot, strerror(errno));
        return false;
    }
    return true;
}

// Find base address of libclient.so from /proc/self/maps
static uintptr_t get_libclient_base() {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (!fp) {
        LOGE("Cannot open /proc/self/maps: %s", strerror(errno));
        return 0;
    }
    char line[1024];
    uintptr_t base = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "libclient.so")) {
            uintptr_t start = 0, end = 0;
            unsigned long long offset = 0;
            if (sscanf(line, "%lx-%lx %*s %llx", &start, &end, &offset) >= 2) {
                if (offset == 0) {
                    base = start;
                    LOGI("Found libclient.so base in maps: 0x%lx (line: %s)", (unsigned long)base, line);
                    break;
                }
            }
        }
    }
    fclose(fp);

    // Fallback if offset 0 wasn't caught
    if (!base) {
        fp = fopen("/proc/self/maps", "r");
        if (fp) {
            while (fgets(line, sizeof(line), fp)) {
                if (strstr(line, "libclient.so") && strstr(line, "r-xp")) {
                    uintptr_t start = 0, end = 0;
                    if (sscanf(line, "%lx-%lx", &start, &end) == 2) {
                        base = start;
                        LOGW("Fallback to r-xp segment for libclient.so: 0x%lx", (unsigned long)base);
                        break;
                    }
                }
            }
            fclose(fp);
        }
    }

    return base;
}

// Install ARM64 inline hook
// Returns pointer to trampoline callable as original function
static void* install_arm64_hook(void* target, void* hook) {
    if (!target || !hook) return nullptr;

    uintptr_t page_size = sysconf(_SC_PAGESIZE);
    if (page_size == 0) page_size = 4096;

    // Allocate writable page for trampoline
    uint8_t* tramp = (uint8_t*)mmap(NULL, page_size,
        PROT_READ | PROT_WRITE,
        MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);

    if (tramp == MAP_FAILED) {
        LOGE("Failed to allocate trampoline page: %s", strerror(errno));
        return nullptr;
    }

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

    // Make trampoline executable (W^X compliant)
    if (!set_memory_prot(tramp, 32, PROT_READ | PROT_EXEC)) {
        LOGE("Failed to set trampoline executable");
        munmap(tramp, page_size);
        return nullptr;
    }
    __builtin___clear_cache((char*)tramp, (char*)tramp + 32);

    // 3. Patch target function with jump to hook function
    if (!set_memory_prot(target, 16, PROT_READ | PROT_WRITE | PROT_EXEC)) {
        LOGE("Failed to make target writable at %p", target);
        munmap(tramp, page_size);
        return nullptr;
    }

    uint64_t hook_addr = (uint64_t)hook;
    uint8_t patch[16];
    memcpy(patch, &ldr_x16_pc8, 4);
    memcpy(patch + 4, &br_x16, 4);
    memcpy(patch + 8, &hook_addr, 8);

    memcpy(target, patch, 16);

    // Restore read+exec and flush instruction cache
    set_memory_prot(target, 16, PROT_READ | PROT_EXEC);
    __builtin___clear_cache((char*)target, (char*)target + 16);

    LOGI("Successfully hooked %p -> %p (tramp: %p)", target, hook, tramp);
    return (void*)tramp;
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
    LOGI("=== Initializing Marvel Super War Native Localization Hook (Android Bionic) ===");

    init_dictionary();

    g_libclient_base = get_libclient_base();
    if (!g_libclient_base) {
        LOGE("Could not find libclient.so base address! Aborting hook to prevent crash.");
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
        LOGW("Partial hook installation (Text: %p, Button: %p)",
             orig_Text_setString, orig_Button_setTitleText);
    }
}
