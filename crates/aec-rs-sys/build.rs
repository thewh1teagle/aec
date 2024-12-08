use std::env;
use std::path::{Path, PathBuf};

use cmake::Config;

fn copy_folder(src: &Path, dst: &Path) {
    std::fs::create_dir_all(dst).expect("Failed to create dst directory");

    let command = if cfg!(windows) { "robocopy.exe" } else { "cp" };
    let args = if cfg!(windows) {
        vec!["/e", src.to_str().unwrap(), dst.to_str().unwrap()]
    } else {
        vec![
            "-rf",
            src.to_str().unwrap(),
            dst.parent().unwrap().to_str().unwrap(),
        ]
    };

    std::process::Command::new(command)
        .args(args)
        .status()
        .expect("Failed to copy folder");
}

fn main() {
    let manifest_dir = env::var("CARGO_MANIFEST_DIR").expect("Failed to get CARGO_MANIFEST_DIR");
    let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());
    let lib_src = Path::new(&manifest_dir).join("speexdsp");
    let lib_dst = out_dir.join("speexdsp");
    let profile = env::var("SPEEXDSP_LIB_PROFILE").unwrap_or("Release".to_string());
    let target = env::var("TARGET").unwrap();

    println!("cargo:rerun-if-changed={}", lib_src.display());

    if !lib_dst.exists() {
        copy_folder(&lib_src, &lib_dst);
    }

    let mut clang_target = target.clone();
    if target.contains("android") {
        clang_target = "armv8-linux-androideabi".to_string();
    }
    if target.contains("riscv64gc-unknown-linux-gnu") {
        // https://github.com/rust-lang/rust-bindgen/issues/2136
        clang_target = "riscv64-unknown-linux-gnu".to_string();
    }

    let mut bindings = bindgen::Builder::default().header("wrapper.h");

    if target.contains("wasm") {
        // See https://github.com/rust-lang/rust-bindgen/issues/2624#issuecomment-1708117271
        bindings = bindings.clang_arg("-fvisibility=default");
    }

    let bindings = bindings
        .clang_arg(format!("-I{}", lib_dst.display()))
        // Explicitly set target in case we are cross-compiling.
        // See https://github.com/rust-lang/rust-bindgen/issues/1780 for context.
        .clang_arg(format!("--target={}", clang_target))
        .parse_callbacks(Box::new(bindgen::CargoCallbacks::new()))
        .generate()
        .expect("Failed to generate bindings");
    let bindings_path = out_dir.join("bindings.rs");
    bindings
        .write_to_file(bindings_path)
        .expect("Failed to write bindings");

    let mut config = Config::new(&lib_dst);

    // Must set when compile for Android
    // Variables comes from cargo-ndk
    if let Ok(abi) = env::var("CARGO_NDK_ANDROID_TARGET") {
        config.define("ANDROID_ABI", abi);
    }
    if let Ok(platform) = env::var("ANDROID_PLATFORM") {
        config.define("ANDROID_PLATFORM", platform);
    }

    let build_dir = config.profile(&profile).build();
    println!(
        "cargo:rustc-link-search={}",
        build_dir.join("lib").display()
    );
    println!("cargo:rustc-link-lib=speexdsp");
}
