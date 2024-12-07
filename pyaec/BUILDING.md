# Building

Use [uv](https://astral.sh/blog/uv)

```console
cargo build -p libaec --release
mkdir data
cp -rf ../target/release/libaec.dylib data
uv build
```

Publish

```console
export UV_PUBLISH_TOKEN="..."
uv publish
```

Installing once published

```console
uv run --with pyaec --refresh-package pyaec --no-project -- python -c "import pyaec"
```
