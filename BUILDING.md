# Building

```console
git clone https://github.com/thewh1teagle/aec-rs --recursive
cd aec-rs
cargo build
```

Useful website for comparesion:

https://fjiang9.github.io/NKF-AEC/

## Publish crates

```console
cd crates/aec-rs-sys
cargo publish
cd ../../
cargo publish
```

## Build for Android

You must install NDK from Android Studio settings.

```console
rustup target add aarch64-linux-android
cargo install cargo-ndk
export NDK_HOME="$HOME/Library/Android/sdk/ndk/$(ls -1 $HOME/Library/Android/sdk/ndk | sort | tail -n 1)"
export CMAKE_TOOLCHAIN_FILE="$NDK_HOME/build/cmake/android.toolchain.cmake"
cargo ndk -t arm64-v8a build --release -p libaec
```
