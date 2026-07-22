@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

set "INPUT_DIR=%~1"
if "%INPUT_DIR%"=="" set "INPUT_DIR=sample_code"

set "OUTPUT_DIR=%~2"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=%ROOT_DIR%\reports"

set "CBOM_IN=%~3"

for %%I in ("%INPUT_DIR%") do set "INPUT_NAME=%%~nxI"

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "FULL_JSON=%OUTPUT_DIR%\%INPUT_NAME%_pqc_impact-report_%STAMP%.json"
set "SUMMARY_JSON=%OUTPUT_DIR%\%INPUT_NAME%_pqc_impact-summary_%STAMP%.json"
set "FILE_REPORTS_JSON=%OUTPUT_DIR%\%INPUT_NAME%_pqc_file-reports_%STAMP%.json"
set "FILE_REPORTS_CSV=%OUTPUT_DIR%\%INPUT_NAME%_pqc_file-reports_%STAMP%.csv"
set "CHANGE_CSV=%OUTPUT_DIR%\%INPUT_NAME%_pqc_likely-change-targets_%STAMP%.csv"
set "HTML_OUT=%OUTPUT_DIR%\%INPUT_NAME%_pqc-report_%STAMP%.html"
set "CBOM_OUT=%OUTPUT_DIR%\%INPUT_NAME%_pqc_cbom_%STAMP%.json"

if "%CBOM_IN%"=="" (
  python "%ROOT_DIR%\app.py" "%INPUT_DIR%" --scan pqc --json-out "%FULL_JSON%" --json-summary-out "%SUMMARY_JSON%" --json-file-reports-out "%FILE_REPORTS_JSON%" --csv-file-reports-out "%FILE_REPORTS_CSV%" --csv-out "%CHANGE_CSV%" --html-out "%HTML_OUT%" --cbom-out "%CBOM_OUT%" --include-file-reports
) else (
  python "%ROOT_DIR%\app.py" "%INPUT_DIR%" --scan pqc --json-out "%FULL_JSON%" --json-summary-out "%SUMMARY_JSON%" --json-file-reports-out "%FILE_REPORTS_JSON%" --csv-file-reports-out "%FILE_REPORTS_CSV%" --csv-out "%CHANGE_CSV%" --html-out "%HTML_OUT%" --cbom-out "%CBOM_OUT%" --include-file-reports --cbom-in "%CBOM_IN%"
)

echo Wrote %FULL_JSON%
echo Wrote %SUMMARY_JSON%
echo Wrote %FILE_REPORTS_JSON%
echo Wrote %FILE_REPORTS_CSV%
echo Wrote %CHANGE_CSV%
echo Wrote %HTML_OUT%
echo Wrote %CBOM_OUT%
