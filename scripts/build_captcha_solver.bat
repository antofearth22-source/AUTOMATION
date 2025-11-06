@echo OFF
echo.
echo ===============================================
echo      Building IRCTC Pro CAPTCHA Solver
echo ===============================================
echo.

REM Set the base directory to the location of the script
set "BASE_DIR=%~dp0.."
set "SOLVER_DIR=%BASE_DIR%\\tools\\captcha_solver"
set "OUTPUT_DIR=%BASE_DIR%\\dist\\captcha_solver"

echo Creating virtual environment...
python -m venv "%SOLVER_DIR%\\.venv"
call "%SOLVER_DIR%\\.venv\\Scripts\\activate.bat"

echo Installing dependencies...
pip install --upgrade pip
pip install -r "%SOLVER_DIR%\\requirements.txt"

echo Building executable with PyInstaller...
pyinstaller --distpath "%OUTPUT_DIR%" --workpath "%SOLVER_DIR%\\build" "%SOLVER_DIR%\\build.spec"

echo.
echo ===============================================
echo      Build Complete
echo ===============================================
echo.
echo Executable is located in: %OUTPUT_DIR%
echo.

deactivate
