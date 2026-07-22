@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

set "INPUT_DIR=%~1"
if "%INPUT_DIR%"=="" set "INPUT_DIR=sample_code"

set "CUSTOM_PATTERNS=%~2"
if "%CUSTOM_PATTERNS%"=="" set "CUSTOM_PATTERNS=%ROOT_DIR%\config/pii/examples/custom-patterns.example.json"

set "OUTPUT_DIR=%~3"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=%ROOT_DIR%\reports"

for %%I in ("%INPUT_DIR%") do set "INPUT_NAME=%%~nxI"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "SUMMARY_JSON=%OUTPUT_DIR%\%INPUT_NAME%_pii_impact-summary_%STAMP%.json"
set "CHANGE_CSV=%OUTPUT_DIR%\%INPUT_NAME%_pii_likely-change-targets_%STAMP%.csv"
set "DBA_SQL=%OUTPUT_DIR%\%INPUT_NAME%_pii_dba-planning_%STAMP%.sql"

python "%ROOT_DIR%\app.py" "%INPUT_DIR%" ^
  --scan pii ^
  --custom-patterns "%CUSTOM_PATTERNS%" ^
  --json-summary-out "%SUMMARY_JSON%" ^
  --csv-out "%CHANGE_CSV%" ^
  --sql-out "%DBA_SQL%"

echo Wrote %SUMMARY_JSON%
echo Wrote %CHANGE_CSV%
echo Wrote %DBA_SQL%
