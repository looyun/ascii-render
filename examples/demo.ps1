param(
    [string]$Img = ""
)

$ErrorActionPreference = "Stop"

$repo = "looyun/ascii-render"
$binary = "ascii-render-windows.exe"
$originalDir = Get-Location

$tempDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

try {
    Set-Location $tempDir

    $binaryUrl = "https://github.com/$repo/releases/latest/download/$binary"
    Write-Host "Downloading $binary ..."

    try {
        Invoke-WebRequest -Uri $binaryUrl -OutFile $binary -UseBasicParsing
    } catch {
        Write-Error "Failed to download binary from $binaryUrl`: $_"
        exit 1
    }

    if ([string]::IsNullOrEmpty($Img)) {
        $Img = "https://raw.githubusercontent.com/$repo/master/assets/gif/%E7%88%B1%E4%BD%A0.gif"
    }

    Write-Host "Rendering: $Img"
    & ".\$binary" $Img
}
finally {
    Set-Location $originalDir
    Write-Host "Cleaning up..."
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
}

Write-Host "Done!"
