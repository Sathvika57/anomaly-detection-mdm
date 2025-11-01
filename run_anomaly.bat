@echo off
echo ==============================================
echo     MDM ANOMALY DETECTION AUTOMATION
echo ==============================================

:: Ask user for optional start and end date/time filters
echo - Leave empty to process all logs.
set /p start_date=Start date (YYYYMMDD) :
set /p start_time=Start time (HHMM, optional) :
set /p end_date=End date (YYYYMMDD, optional) :
set /p end_time=End time (HHMM, optional) :

echo.
echo [1] Parsing logs...
python src\parse_logs.py %start_date% %start_time% %end_date% %end_time%

if %ERRORLEVEL% NEQ 0 (
  echo ❌ Error during parsing logs.
  pause
  exit /b
)

echo.
echo [2] Detecting anomalies...
python src\detect_isoforest.py

if %ERRORLEVEL% NEQ 0 (
  echo ❌ Error during anomaly detection.
  pause
  exit /b
)

echo.
echo [3] Generating reports...
python src\generate_report.py

if %ERRORLEVEL% NEQ 0 (
  echo ❌ Error during report generation.
  pause
  exit /b
)

echo.
echo [4] Launching dashboard...
start "" streamlit run src\dashboard.py

echo.
echo ==============================================
echo ✅ Process completed successfully!
echo ==============================================
pause
