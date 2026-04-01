#!/bin/bash
set -e

VERSION=${1:-latest}
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

curl -fSL -o ascii-render "https://github.com/${REPO}/releases/download/${VERSION}/${BINARY}"
chmod +x ascii-render

GIF_URL="https://github.com/${REPO}/releases/download/${VERSION}/example.gif"
echo "Rendering GIF from URL..."
if [[ "$BINARY" == *"windows"* ]]; then
    ./ascii-render.exe "$GIF_URL"
else
    ./ascii-render "$GIF_URL"
fi

echo "Done!"