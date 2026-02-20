@echo off
setlocal enabledelayedexpansion

REM Pasta do projeto (onde está este .bat)
cd /d "%~dp0"

echo [1/4] Parando Flask (python app.py)...
for /f "tokens=2 delims=," %%P in ('tasklist /fo csv ^| findstr /i "python.exe"') do (
  REM tenta matar qualquer python rodando o app.py
)

REM Mata python que esteja rodando app.py (mais certeiro via WMIC nem sempre existe)
REM Fallback: mata processos python (se vc só usa isso pro projeto, ok)
taskkill /F /IM python.exe >nul 2>&1

echo [2/4] Limpando cache do Python...
for /d /r %%D in (__pycache__) do (
  rmdir /s /q "%%D" >nul 2>&1
)
del /s /q *.pyc >nul 2>&1

echo [3/4] Iniciando Flask...
if exist ".venv\Scripts\python.exe" (
  start "Flask" /min ".venv\Scripts\python.exe" app.py
) else (
  start "Flask" /min python app.py
)

echo [4/4] Abrindo no Chrome sem cache (perfil temporario)...
set "TMPPROFILE=%TEMP%\flask_nocache_profile"
if exist "%TMPPROFILE%" rmdir /s /q "%TMPPROFILE%" >nul 2>&1

REM Tenta abrir Chrome (ajuste o caminho se necessário)
set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if exist "%CHROME%" (
  start "" "%CHROME%" --user-data-dir="%TMPPROFILE%" --disable-application-cache --disk-cache-size=1 "http://127.0.0.1:5000/?v=%RANDOM%%RANDOM%"
) else (
  start "" "http://127.0.0.1:5000/?v=%RANDOM%%RANDOM%"
)

echo OK.
exit /b