@echo off
echo ============================
echo Running anomaly detection...
echo ============================

if exist src\generate_synthetic_logs_with_anomalies.py call python src\generate_synthetic_logs_with_anomalies.py
if not exist src\generate_synthetic_logs_with_anomalies.py echo Skipping synthetic log generation (file not found)...

call python src\parse_normalize.py
call python src\features.py
call python src\detect_isoforest.py
call python src\report.py
call python src\plots.py

echo ============================
echo Demo complete. Check data\reports\ for reports and plots
echo ============================
pause
