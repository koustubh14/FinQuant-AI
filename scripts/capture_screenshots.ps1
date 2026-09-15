param(
    [Parameter(Mandatory=$true)][string]$AaplId,
    [Parameter(Mandatory=$true)][string]$RelianceId
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$outputDirectory = Join-Path $projectRoot 'docs\screenshots'
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
Push-Location (Join-Path $projectRoot 'frontend')
function Capture([string]$name, [string]$selector = '') {
    if ($selector) {
        npx agent-browser eval "document.querySelector('$selector').scrollIntoView({block:'start'})" | Out-Null
    } else {
        npx agent-browser eval 'window.scrollTo(0,0)' | Out-Null
    }
    $capture = npx agent-browser screenshot --json | ConvertFrom-Json
    if (-not $capture.success) { throw 'Browser screenshot failed' }
    Copy-Item -LiteralPath $capture.data.path -Destination (Join-Path $outputDirectory $name)
    Write-Output "Captured $name from the running UI"
}
try {
    npx agent-browser set viewport 1440 1000 | Out-Null
    npx agent-browser open ('http://127.0.0.1:5173/?analysis=' + [Uri]::EscapeDataString($AaplId)) | Out-Null
    npx agent-browser wait --load networkidle | Out-Null
    Capture 'aapl-dashboard.png'
    Capture 'aapl-risk.png' '#risk'
    Capture 'aapl-forecast.png' '#forecast'
    Capture 'aapl-recommendation.png' '#recommendation'
    npx agent-browser open ('http://127.0.0.1:5173/?analysis=' + [Uri]::EscapeDataString($RelianceId)) | Out-Null
    npx agent-browser wait --load networkidle | Out-Null
    Capture 'reliance-dashboard.png'
    npx agent-browser eval 'document.querySelector("details.notice").open=true' | Out-Null
    Capture 'data-quality.png'
    npx agent-browser set viewport 390 844 | Out-Null
    Capture 'mobile-dashboard.png'
    npx agent-browser errors
} finally {
    Pop-Location
}
