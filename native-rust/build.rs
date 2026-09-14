fn find_ndk() -> Option<std::path::PathBuf> {
    for var in &["ANDROID_NDK_HOME", "NDK", "ANDROID_NDK_ROOT", "NDK_ROOT"] {
        if let Ok(val) = std::env::var(var) {
            let p = std::path::PathBuf::from(val);
            if p.is_dir() {
                return Some(p);
            }
        }
    }
    // Check standard Android SDK locations
    let mut sdk_candidates = Vec::new();
    if let Ok(sdk) = std::env::var("ANDROID_HOME").or_else(|_| std::env::var("ANDROID_SDK_ROOT")) {
        sdk_candidates.push(std::path::PathBuf::from(sdk));
    }
    if let Ok(home) = std::env::var("HOME") {
        sdk_candidates.push(std::path::Path::new(&home).join("Android/Sdk"));
        sdk_candidates.push(std::path::Path::new(&home).join("Android/sdk"));
        sdk_candidates.push(std::path::Path::new(&home).join(".android/ndk"));
    }
    for sdk in sdk_candidates {
        let ndk_dir = sdk.join("ndk");
        if let Ok(entries) = std::fs::read_dir(&ndk_dir) {
            let mut versions: Vec<_> = entries.filter_map(|e| e.ok().map(|e| e.path())).collect();
            versions.sort();
            if let Some(latest) = versions.pop() {
                return Some(latest);
            }
        }
    }
    None
}

fn main() {
    let mut build = cc::Build::new();
    build.cpp(true);
    build.flag("-std=c++17");
    build.flag("-O3");
    build.flag("-fPIC");
    build.file("src/cpp_bridge.cpp");

    if let Some(ndk) = find_ndk() {
        for host in &["linux-x86_64", "darwin-x86_64", "darwin-arm64", "windows-x86_64"] {
            let clang = ndk.join(format!("toolchains/llvm/prebuilt/{host}/bin/aarch64-linux-android21-clang++"));
            if clang.is_file() {
                build.compiler(clang);
                break;
            }
        }
    } else {
        // Fall back to compiler from PATH
        build.compiler("aarch64-linux-android21-clang++");
    }

    build.compile("cpp_bridge");

    println!("cargo:rustc-link-lib=log");
    println!("cargo:rerun-if-changed=src/cpp_bridge.cpp");
}
