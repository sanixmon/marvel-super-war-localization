fn main() {
    let ndk = std::env::var("ANDROID_NDK_HOME")
        .or_else(|_| std::env::var("NDK"))
        .unwrap_or_else(|_| "/home/kouzen/Android/Sdk/ndk/27.1.12297006".to_string());

    let cxx = format!(
        "{}/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang++",
        ndk
    );

    cc::Build::new()
        .cpp(true)
        .compiler(&cxx)
        .flag("-std=c++17")
        .flag("-O3")
        .flag("-fPIC")
        .file("src/cpp_bridge.cpp")
        .compile("cpp_bridge");

    println!("cargo:rustc-link-lib=log");
    println!("cargo:rerun-if-changed=src/cpp_bridge.cpp");
}
