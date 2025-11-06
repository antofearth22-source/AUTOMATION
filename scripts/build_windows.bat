@echo off
echo --- IRCTC Pro Build Script ---

echo.
echo [1/3] Cleaning up previous builds...
rmdir /s /q build dist 2>nul

echo.
echo [2/3] Installing dependencies...
py -3.11 -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    exit /b %errorlevel%
)

echo.
echo [3/3] Running PyInstaller...
py -3.11 -m PyInstaller build/windows/app.spec --noconfirm
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed.
    exit /b %errorlevel%
)

echo.
echo --- Build successful! ---
echo Find the application in the 'dist/irctc_pro_final_build' directory.
