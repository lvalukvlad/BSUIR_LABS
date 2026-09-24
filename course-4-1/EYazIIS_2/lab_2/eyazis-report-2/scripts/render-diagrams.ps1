<#
    Рендер диаграмм PlantUML в PNG.
#>

$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$reportDir = Split-Path -Parent $scriptDir
$sourceDir = Join-Path $reportDir 'plantuml'
$targetDir = Join-Path $reportDir 'png'
$jarPath = Join-Path $scriptDir 'plantuml.jar'
$jarUrl = 'https://github.com/plantuml/plantuml/releases/download/v1.2025.4/plantuml-1.2025.4.jar'

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    throw 'Java не найдена в PATH.'
}

if (-not (Test-Path $jarPath)) {
    Write-Host "Загрузка plantuml.jar..."
    Invoke-WebRequest -Uri $jarUrl -OutFile $jarPath
}

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir | Out-Null
}

$sources = Get-ChildItem -Path $sourceDir -Filter '*.puml'
Write-Host "Рендер $($sources.Count) диаграмм в $targetDir"
java -jar $jarPath -charset UTF-8 -tpng -o $targetDir $sourceDir\*.puml

Get-ChildItem -Path $targetDir -Filter '*.png' | ForEach-Object {
    Write-Host ("  {0} ({1:N0} байт)" -f $_.Name, $_.Length)
}