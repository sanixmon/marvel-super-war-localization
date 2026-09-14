use std::ffi::CString;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::ptr::{null_mut, copy_nonoverlapping};

pub mod dict_data;
mod dict;

#[link(name = "log")]
extern "C" {
    fn __android_log_print(
        prio: libc::c_int,
        tag: *const libc::c_char,
        fmt: *const libc::c_char,
        ...
    ) -> libc::c_int;
}

extern "C" {
    fn std_string_get_data(s: *const libc::c_void) -> *const libc::c_char;
    fn std_string_get_size(s: *const libc::c_void) -> libc::size_t;
    fn std_string_call_trampoline(
        orig_fn: *const libc::c_void,
        this: *mut libc::c_void,
        text_ptr: *const libc::c_char,
        text_len: libc::size_t,
    );
    fn flush_instruction_cache(addr: *mut libc::c_void, size: libc::size_t);
}

const ANDROID_LOG_INFO: libc::c_int = 4;
const ANDROID_LOG_WARN: libc::c_int = 5;
const LOG_TAG: &[u8] = b"LocHookRust\0";

fn log_info_impl(msg: &str) {
    if let Ok(c_msg) = CString::new(msg) {
        unsafe {
            __android_log_print(
                ANDROID_LOG_INFO,
                LOG_TAG.as_ptr() as *const libc::c_char,
                b"%s\0".as_ptr() as *const libc::c_char,
                c_msg.as_ptr(),
            );
        }
    }
}

fn log_warn_impl(msg: &str) {
    if let Ok(c_msg) = CString::new(msg) {
        unsafe {
            __android_log_print(
                ANDROID_LOG_WARN,
                LOG_TAG.as_ptr() as *const libc::c_char,
                b"%s\0".as_ptr() as *const libc::c_char,
                c_msg.as_ptr(),
            );
        }
    }
}

macro_rules! log_info {
    ($($arg:tt)*) => {
        log_info_impl(&format!($($arg)*))
    };
}

macro_rules! log_warn {
    ($($arg:tt)*) => {
        log_warn_impl(&format!($($arg)*))
    };
}

static mut ORIG_TEXT_SET_STRING: *const libc::c_void = std::ptr::null();
static mut ORIG_BUTTON_SET_TITLE_TEXT: *const libc::c_void = std::ptr::null();

unsafe fn set_memory_prot(addr: *mut libc::c_void, len: usize, prot: libc::c_int) -> bool {
    let mut page_size = libc::sysconf(libc::_SC_PAGESIZE) as usize;
    if page_size == 0 {
        page_size = 4096;
    }
    let page_start = (addr as usize) & !(page_size - 1);
    let page_end = ((addr as usize) + len + page_size - 1) & !(page_size - 1);
    let ret = libc::mprotect(page_start as *mut libc::c_void, page_end - page_start, prot);
    ret == 0
}

fn get_libclient_base() -> usize {
    let file = match File::open("/proc/self/maps") {
        Ok(f) => f,
        Err(_) => return 0,
    };
    let reader = BufReader::new(file);

    for line in reader.lines().flatten() {
        if line.contains("libclient.so") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 3 {
                let addr_range: Vec<&str> = parts[0].split('-').collect();
                if addr_range.len() == 2 {
                    if let (Ok(start), Ok(offset)) = (
                        usize::from_str_radix(addr_range[0], 16),
                        u64::from_str_radix(parts[2], 16),
                    ) {
                        if offset == 0 {
                            unsafe {
                                // Validate ELF magic: \x7fELF (0x464c457f)
                                let magic = *(start as *const u32);
                                if magic == 0x464c457f {
                                    return start;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    0
}

unsafe fn install_arm64_hook(target: *mut libc::c_void, hook: *const libc::c_void) -> *const libc::c_void {
    if target.is_null() || hook.is_null() {
        return std::ptr::null();
    }

    let mut page_size = libc::sysconf(libc::_SC_PAGESIZE) as usize;
    if page_size == 0 {
        page_size = 4096;
    }

    // Allocate writable page for trampoline
    let tramp = libc::mmap(
        null_mut(),
        page_size,
        libc::PROT_READ | libc::PROT_WRITE,
        libc::MAP_ANONYMOUS | libc::MAP_PRIVATE,
        -1,
        0,
    ) as *mut u8;

    if tramp == libc::MAP_FAILED as *mut u8 {
        return std::ptr::null();
    }

    // 1. Copy first 16 bytes from target to trampoline
    copy_nonoverlapping(target as *const u8, tramp, 16);

    // 2. Append jump from trampoline back to target + 16
    let ldr_x16_pc8: u32 = 0x58000050; // LDR X16, #8
    let br_x16: u32 = 0xd61f0200;      // BR X16
    let target_cont = (target as u64) + 16;

    copy_nonoverlapping(&ldr_x16_pc8 as *const u32 as *const u8, tramp.add(16), 4);
    copy_nonoverlapping(&br_x16 as *const u32 as *const u8, tramp.add(20), 4);
    copy_nonoverlapping(&target_cont as *const u64 as *const u8, tramp.add(24), 8);

    // Make trampoline executable
    if !set_memory_prot(tramp as *mut libc::c_void, 32, libc::PROT_READ | libc::PROT_EXEC) {
        libc::munmap(tramp as *mut libc::c_void, page_size);
        return std::ptr::null();
    }
    flush_instruction_cache(tramp as *mut libc::c_void, 32);

    // 3. Patch target function with jump to hook function
    if !set_memory_prot(target, 16, libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC) {
        libc::munmap(tramp as *mut libc::c_void, page_size);
        return std::ptr::null();
    }

    let hook_addr = hook as u64;
    copy_nonoverlapping(&ldr_x16_pc8 as *const u32 as *const u8, target as *mut u8, 4);
    copy_nonoverlapping(&br_x16 as *const u32 as *const u8, (target as *mut u8).add(4), 4);
    copy_nonoverlapping(&hook_addr as *const u64 as *const u8, (target as *mut u8).add(8), 8);

    set_memory_prot(target, 16, libc::PROT_READ | libc::PROT_EXEC);
    flush_instruction_cache(target, 16);

    tramp as *const libc::c_void
}

extern "C" fn hooked_text_set_string(this: *mut libc::c_void, text_ref: *const libc::c_void) {
    if this.is_null() || text_ref.is_null() {
        return;
    }
    unsafe {
        if ORIG_TEXT_SET_STRING.is_null() {
            return;
        }

        let data_ptr = std_string_get_data(text_ref);
        let size = std_string_get_size(text_ref);
        if size == 0 || data_ptr.is_null() {
            std_string_call_trampoline(ORIG_TEXT_SET_STRING, this, data_ptr, size);
            return;
        }

        let slice = std::slice::from_raw_parts(data_ptr as *const u8, size);
        match std::str::from_utf8(slice) {
            Ok(s) => {
                let translated = dict::translate(s);
                std_string_call_trampoline(
                    ORIG_TEXT_SET_STRING,
                    this,
                    translated.as_ptr() as *const libc::c_char,
                    translated.len(),
                );
            }
            Err(_) => {
                std_string_call_trampoline(ORIG_TEXT_SET_STRING, this, data_ptr, size);
            }
        }
    }
}

extern "C" fn hooked_button_set_title_text(this: *mut libc::c_void, text_ref: *const libc::c_void) {
    if this.is_null() || text_ref.is_null() {
        return;
    }
    unsafe {
        if ORIG_BUTTON_SET_TITLE_TEXT.is_null() {
            return;
        }

        let data_ptr = std_string_get_data(text_ref);
        let size = std_string_get_size(text_ref);
        if size == 0 || data_ptr.is_null() {
            std_string_call_trampoline(ORIG_BUTTON_SET_TITLE_TEXT, this, data_ptr, size);
            return;
        }

        let slice = std::slice::from_raw_parts(data_ptr as *const u8, size);
        match std::str::from_utf8(slice) {
            Ok(s) => {
                let translated = dict::translate(s);
                std_string_call_trampoline(
                    ORIG_BUTTON_SET_TITLE_TEXT,
                    this,
                    translated.as_ptr() as *const libc::c_char,
                    translated.len(),
                );
            }
            Err(_) => {
                std_string_call_trampoline(ORIG_BUTTON_SET_TITLE_TEXT, this, data_ptr, size);
            }
        }
    }
}

#[used]
#[link_section = ".init_array"]
static INIT_ARRAY: extern "C" fn() = native_init;

#[no_mangle]
pub extern "C" fn native_init() {
    log_info!("=== Initializing Marvel Super War Rust Localization Hook (aarch64 Android) ===");

    dict::init();
    log_info!("Rust dictionary initialized (5594+ master entries).");

    let libclient_base = get_libclient_base();
    if libclient_base == 0 {
        log_warn!("Could not find libclient.so ELF base address. Skipping hooks safely.");
        return;
    }
    log_info!("Found libclient.so at base address: 0x{:x}", libclient_base);

    unsafe {
        // Target 1: cocos2d::ui::Text::setString at offset 0xe1463c
        let target_text = (libclient_base + 0xe1463c) as *mut libc::c_void;
        let expected_text_op: u32 = 0xa9be4ff4; // stp x20, x19, [sp, #-32]!
        let current_text_op = *(target_text as *const u32);

        if current_text_op == expected_text_op {
            ORIG_TEXT_SET_STRING = install_arm64_hook(
                target_text,
                hooked_text_set_string as *const libc::c_void,
            );
            log_info!("Installed Text::setString hook at 0x{:x}", target_text as usize);
        } else {
            log_warn!(
                "Text::setString opcode mismatch: expected 0x{:08x}, got 0x{:08x}",
                expected_text_op,
                current_text_op
            );
        }

        // Target 2: cocos2d::ui::Button::setTitleText at offset 0xde7ed4
        let target_button = (libclient_base + 0xde7ed4) as *mut libc::c_void;
        let expected_button_op: u32 = 0xd10103ff; // sub sp, sp, #0x40
        let current_button_op = *(target_button as *const u32);

        if current_button_op == expected_button_op {
            ORIG_BUTTON_SET_TITLE_TEXT = install_arm64_hook(
                target_button,
                hooked_button_set_title_text as *const libc::c_void,
            );
            log_info!("Installed Button::setTitleText hook at 0x{:x}", target_button as usize);
        } else {
            log_warn!(
                "Button::setTitleText opcode mismatch: expected 0x{:08x}, got 0x{:08x}",
                expected_button_op,
                current_button_op
            );
        }

        if !ORIG_TEXT_SET_STRING.is_null() && !ORIG_BUTTON_SET_TITLE_TEXT.is_null() {
            log_info!("=== All Rust Native ARM64 Hooks Successfully Installed! ===");
        }
    }
}
