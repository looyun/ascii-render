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

mkdir -p temp_ascii_render
cd temp_ascii_render

curl -sL -o ascii-render "https://github.com/${REPO}/releases/download/${VERSION}/${BINARY}"
curl -sL -o example.gif "https://github.com/${REPO}/releases/download/${VERSION}/example.gif"

chmod +x ascii-render

echo "Rendering GIF..."
if [[ "$BINARY" == *"windows"* ]]; then
    ./ascii-render.exe example.gif
else
    ./ascii-render example.gif
fi

echo "Done! Cleanup..."
cd ..
rm -rf temp_ascii_render