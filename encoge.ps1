param(
    [Parameter(Mandatory=$true)]
    [string]$param_InputFile,

    [int]$param_TargetSizeMB = 10,
    [string]$param_FileSuffix = "__COMP",
    [float]$param_OverheadPercent = 0.03
)

Write-Output "=== ENCOGE - BY MOXWEL ==="
Write-Output "Params:"
Write-Output "    Input file: ${param_InputFile}"
Write-Output "    Target size: ${param_TargetSizeMB} MB"
Write-Output "    File suffix: ${param_FileSuffix}"
Write-Output "    Overhead percent: ${param_OverheadPercent}"

# Check ffmpeg and ffprobe
Write-Output "Checking for ffmpeg and ffprobe..."
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "    [!] ffmpeg is not installed or not in PATH. Please install ffmpeg."
    exit 1
}
if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
    Write-Error "    [!] ffprobe is not installed or not in PATH. Please install ffmpeg."
    exit 1
}

# Get input file info
Write-Output "Getting video information..."

$videoDurationCmd = ffprobe -loglevel error -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$param_InputFile"
$videoDurationSec = [double]($videoDurationCmd | Out-String)
if ($videoDurationSec -le 0) {
    Write-Error "    [!] Could not determine video duration."
    exit 1
}

$videoBitrateCmd = ffprobe -loglevel error -v error -select_streams v:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$param_InputFile"
$videoBitrate = [int]($videoBitrateCmd | Out-String)
if ($videoBitrate -le 0) {
    Write-Error "    [!] Could not determine video bitrate."
    exit 1
}
$videoBitrateKbps = [math]::Floor($videoBitrate / 1000) # Convert to kbps

$audioBitrateCmd = ffprobe -loglevel error -v error -select_streams a:0 -show_entries stream=bit_rate -of default=noprint_wrappers=1:nokey=1 "$param_InputFile"
$audioBitrate = [int]($audioBitrateCmd | Out-String)
if ($audioBitrate -le 0) {
    Write-Warning "    [!] Could not determine audio bitrate. Using default value of 96 kbps."
    $audioBitrateKbps = 96
} else {
    $audioBitrateKbps = [math]::Floor($audioBitrate / 1000) # Convert to kbps
}

Write-Output "    Video duration: ${videoDurationSec} seconds"
Write-Output "    Video bitrate: ${videoBitrateKbps} kbps"
Write-Output "    Audio bitrate: ${audioBitrateKbps} kbps"

# Calculate target video bitrate
Write-Output "Calculating target bitrate..."

$targetSizeKbits = ($param_TargetSizeMB * (1 - $param_OverheadPercent)) * 8192
$targetFileBitrateKbps = [math]::Floor($targetSizeKbits / $videoDurationSec)
$targetVideoBitrate = $targetFileBitrateKbps - $audioBitrateKbps

if ($targetVideoBitrate -le 0) {
    Write-Error "    [!] Target size too small for given duration. Increase size or reduce duration."
    exit 1
}

Write-Output "    Target video bitrate: ${targetVideoBitrate} kbps"
if ($targetVideoBitrate -le $videoBitrateKbps * 0.5) {
    Write-Warning "    [!] Target video bitrate is significantly lower than current video bitrate. Quality may be affected."
}

# Output file name
$folder = [System.IO.Path]::GetDirectoryName($param_InputFile)
$fileBase = [System.IO.Path]::GetFileNameWithoutExtension($param_InputFile)
$extension = [System.IO.Path]::GetExtension($param_InputFile)
$outputFile = Join-Path $folder ("{0}{1}{2}" -f $fileBase, $param_FileSuffix, $extension)

Write-Output "Output file: ${outputFile}"
if (Test-Path $outputFile) {
    Write-Error "    [!] Output file already exists."
    exit 1
}

# Encoding job
Write-Output "    PASS 1: analyzing video..."
ffmpeg -loglevel error -y -i "${param_InputFile}" -c:v libx264 -b:v ${targetVideoBitrate}k -pass 1 -an -f mp4 NUL

Write-Output "    PASS 2: compressing..."
ffmpeg -loglevel error -y -i "${param_InputFile}" -c:v libx264 -b:v ${targetVideoBitrate}k -pass 2 -c:a aac -b:a ${audioBitrateKbps}k "${outputFile}"

Write-Output "Cleaning up temporary files..."
Remove-Item ffmpeg2pass-0.log* -ErrorAction SilentlyContinue

Write-Output "Done."
exit 0
