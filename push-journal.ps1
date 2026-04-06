# push-journal.ps1
# Run this daily on VPS (Task Scheduler) to push CSV journals to GitHub
# Setup: git clone your repo to C:\EA-Journal, then schedule this script

$RepoPath = "C:\EA-Journal"
$MT5FilesPath = "$env:APPDATA\MetaQuotes\Terminal\*\MQL5\Files"
$JournalPattern = "ESTLB_Journal_*.csv"

# Find MT5 Files directory (handles different terminal IDs)
$mt5Files = Get-ChildItem -Path $MT5FilesPath -Filter $JournalPattern -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending

if ($mt5Files.Count -eq 0) {
    Write-Host "No journal files found."
    exit 0
}

# Copy new journals to repo
$journalDir = Join-Path $RepoPath "journals"
if (-not (Test-Path $journalDir)) {
    New-Item -ItemType Directory -Path $journalDir | Out-Null
}

$copied = 0
foreach ($file in $mt5Files) {
    $dest = Join-Path $journalDir $file.Name
    if (-not (Test-Path $dest) -or (Get-Item $dest).LastWriteTime -lt $file.LastWriteTime) {
        Copy-Item $file.FullName $dest -Force
        $copied++
        Write-Host "Copied: $($file.Name)"
    }
}

if ($copied -eq 0) {
    Write-Host "No new journals to push."
    exit 0
}

# Git commit and push
Set-Location $RepoPath
git add journals/
git add dev.md

$today = Get-Date -Format "yyyy-MM-dd"
git commit -m "Daily journal update: $today ($copied files)"
git push origin main

Write-Host "Pushed $copied journal files to GitHub."
