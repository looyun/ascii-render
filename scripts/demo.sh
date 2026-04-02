#!/bin/bash
set -e

VERSION=${1:-latest}
INPUT=${2:-""}
REPO="looyun/ascii-render"

echo "Downloading ascii-render binary..."
case "$(uname -s)" in
    Linux*)     BINARY="ascii-render-linux" ;;
    Darwin*)    BINARY="ascii-render-macos" ;;
    MINGW*|MSYS*|CYGWIN*) BINARY="ascii-render-windows.exe" ;;
    *)          echo "Unsupported OS"; exit 1 ;;
esac

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

cd "$TMPDIR"

curl -fSL -o ascii-render "https://github.com/${REPO}/releases/latest/download/${BINARY}"
chmod +x ascii-render

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
