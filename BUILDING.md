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

## Build for IOS

Install Xcode command line tools

```console
xcode-select --install
```

Install toolchain

```console
# IOS
rustup target add aarch64-apple-ios
# Intel chip emulator
rustup target add x86_64-apple-ios
# Apple chip emulator
rustup target add aarch64-apple-ios-sim
```

Build

```console
cargo build --release --target aarch64-apple-ios
```
