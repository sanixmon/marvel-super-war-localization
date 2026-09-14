#include <string>
#include <cstddef>

extern "C" {
    // Extract C string and length from Cocos2d-x std::string reference
    const char* std_string_get_data(const void* s) {
        if (!s) return "";
        return ((const std::string*)s)->data();
    }

    size_t std_string_get_size(const void* s) {
        if (!s) return 0;
        return ((const std::string*)s)->size();
    }

    // Invoke original function through trampoline with a newly created std::string
    void std_string_call_trampoline(
        void (*orig_fn)(void*, const std::string&),
        void* self,
        const char* text_ptr,
        size_t text_len
    ) {
        if (!orig_fn || !self) return;
        std::string s(text_ptr, text_len);
        orig_fn(self, s);
    }

    // Direct ARM64 instruction cache flushing to avoid missing __clear_cache symbol on Android
    void __clear_cache(void* start, void* end) {
        if (!start || !end || start >= end) return;
        uint64_t ctr_el0 = 0;
        __asm__ __volatile__("mrs %0, ctr_el0" : "=r"(ctr_el0));
        size_t dcache_line_size = 4 << ((ctr_el0 >> 16) & 0xf);
        size_t icache_line_size = 4 << (ctr_el0 & 0xf);

        uintptr_t a = (uintptr_t)start & ~(dcache_line_size - 1);
        for (; a < (uintptr_t)end; a += dcache_line_size) {
            __asm__ __volatile__("dc cvau, %0" : : "r"(a) : "memory");
        }
        __asm__ __volatile__("dsb ish" : : : "memory");

        a = (uintptr_t)start & ~(icache_line_size - 1);
        for (; a < (uintptr_t)end; a += icache_line_size) {
            __asm__ __volatile__("ic ivau, %0" : : "r"(a) : "memory");
        }
        __asm__ __volatile__("dsb ish" : : : "memory");
        __asm__ __volatile__("isb" : : : "memory");
    }

    // Portable instruction cache flushing for ARM64 trampoline
    void flush_instruction_cache(void* addr, size_t size) {
        __clear_cache((char*)addr, (char*)addr + size);
    }
}
