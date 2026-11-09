$ErrorActionPreference = 'Stop'
$repo = 'zuc7/Audio_router'
$release = Invoke-RestMethod "https://api.github.com/repos/$repo/releases/latest"
$installer = $release.assets | Where-Object name -eq 'AudioRouter-Setup.exe' | Select-Object -First 1
$sumsAsset = $release.assets | Where-Object name -eq 'SHA256SUMS.txt' | Select-Object -First 1
if (-not $installer -or -not $sumsAsset) { throw 'The latest release does not include the installer and checksum yet.' }
$temp = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $temp | Out-Null
try {
    $exe = Join-Path $temp 'AudioRouter-Setup.exe'
    $sums = Join-Path $temp 'SHA256SUMS.txt'
    Invoke-WebRequest $installer.browser_download_url -OutFile $exe
    Invoke-WebRequest $sumsAsset.browser_download_url -OutFile $sums
    $expected = ((Get-Content $sums | Where-Object { $_ -match '\sAudioRouter-Setup\.exe$' } | Select-Object -First 1) -split '\s+')[0]
    if (-not $expected -or (Get-FileHash $exe -Algorithm SHA256).Hash -ne $expected.ToUpperInvariant()) { throw 'Installer checksum verification failed.' }
    Start-Process -FilePath $exe -Wait
} finally {
    Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
}
