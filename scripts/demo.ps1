param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "Downloading ascii-render binary..."

$os = "windows"
$binary = "ascii-render-windows.exe"

$binaryUrl = "https://github.com/looyun/ascii-render/releases/download/$Version/$binary"
$gifUrl = "https://github.com/looyun/ascii-render/releases/download/$Version/example.gif"

$tempDir = "temp_ascii_render"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

try {
    Write-Host "Downloading binary..."
    Invoke-WebRequest -Uri $binaryUrl -OutFile $binary -UseBasicParsing

    Write-Host "Downloading example GIF..."
    Invoke-WebRequest -Uri $gifUrl -OutFile example.gif -UseBasicParsing

    Write-Host "Rendering GIF..."
    & .\$binary example.gif
}
finally {
    Set-Location ..
    Write-Host "Cleaning up..."
    Remove-Item -Recurse -Force $tempDir
}

Write-Host "Done!"