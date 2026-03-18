@echo off
echo ==========================================
echo Build Claude Transport Meter en .exe
echo ==========================================
echo.

python -m venv .venv
if errorlevel 1 goto end

.venv\Scripts\python -m pip install --upgrade pip
if errorlevel 1 goto end

.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 goto end

.venv\Scripts\python -m pip install pyinstaller
if errorlevel 1 goto end

.venv\Scripts\python -m PyInstaller --noconfirm --windowed --onefile --name ClaudeTransportMeter --hidden-import matplotlib --hidden-import matplotlib.backends.backend_tkagg app.py

echo.
echo Build termine. Executable dans dist\
goto done

:end
echo.
echo Une erreur s'est produite pendant le build.

:done
pause