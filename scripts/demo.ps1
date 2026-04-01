param(
    [string]$Version = "latest",
    [string]$Input = ""
)

$ErrorActionPreference = "Stop"

$repo = "looyun/ascii-render"
$binary = "ascii-render-windows.exe"

Write-Host "Downloading ascii-render binary..."

$binaryUrl = "https://github.com/$repo/releases/download/$Version/$binary"

$tempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
Set-Location $tempDir

try {
    Write-Host "Downloading binary..."
    Invoke-WebRequest -Uri $binaryUrl -OutFile $binary -UseBasicParsing

    if ([string]::IsNullOrEmpty($Input)) {
        $Input = "https://raw.githubusercontent.com/$repo/master/assets/gif/%E7%88%B1%E4%BD%A0.gif"
    }

    Write-Host "Rendering: $Input"
    & .\$binary $Input
}
finally {
    Set-Location ..
    Write-Host "Cleaning up..."
    Remove-Item -Recurse -Force $tempDir
}

Write-Host "Done!"