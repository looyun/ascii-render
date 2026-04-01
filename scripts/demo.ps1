param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

$repo = "looyun/ascii-render"
$binary = "ascii-render-windows.exe"

Write-Host "Downloading ascii-render binary..."

$binaryUrl = "https://github.com/$repo/releases/download/$Version/$binary"
$gifUrl = "https://github.com/$repo/releases/download/$Version/example.gif"

$tempDir = "temp_ascii_render"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

try {
    Write-Host "Downloading binary..."
    Invoke-WebRequest -Uri $binaryUrl -OutFile $binary -UseBasicParsing

    Write-Host "Rendering GIF from URL..."
    & .\$binary $gifUrl
}
finally {
    Set-Location ..
    Write-Host "Cleaning up..."
    Remove-Item -Recurse -Force $tempDir
}

Write-Host "Done!"