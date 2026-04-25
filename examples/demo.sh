#!/bin/bash
set -euo pipefail

INPUT=${1:-""}
REPO="looyun/ascii-render"

# Determine binary name based on OS
case "$(uname -s)" in
    Linux*)     BINARY="ascii-render-linux" ;;
    Darwin*)    BINARY="ascii-render-macos" ;;
    MINGW*|MSYS*|CYGWIN*) BINARY="ascii-render-windows.exe" ;;
    *)          echo "Unsupported OS: $(uname -s)" >&2; exit 1 ;;
esac

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

cd "$TMPDIR"

echo "Downloading ${BINARY}..."
URL="https://github.com/${REPO}/releases/latest/download/${BINARY}"
if ! curl -fSL -o ascii-render "${URL}"; then
    echo "Error: failed to download binary from ${URL}" >&2
    exit 1
fi

if [[ "$BINARY" != *"windows"* ]]; then
    chmod +x ascii-render
fi

if [[ -z "$INPUT" ]]; then
    INPUT="https://raw.githubusercontent.com/${REPO}/master/assets/gif/%E7%88%B1%E4%BD%A0.gif"
fi

echo "Rendering: $INPUT"
if [[ "$BINARY" == *"windows"* ]]; then
    ./ascii-render.exe "$INPUT"
else
    ./ascii-render "$INPUT"
fi

echo "Done!"
