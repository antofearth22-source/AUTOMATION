# IRCTC Pro - Windows Build Instructions

This document provides instructions for setting up the environment and building the `IRCTC_Pro.exe` application on a Windows 10/11 machine.

## Prerequisites

- **Python 3.11**: Ensure you have Python 3.11 installed. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3110/). Make sure to check the box "Add Python to PATH" during installation.
- **Git**: Ensure you have Git installed for cloning the repository.

## Setup and Build Process

1.  **Clone the Repository**:
    Open a Command Prompt (`cmd.exe`) or PowerShell and clone the repository:
    ```bash
    git clone <repository_url>
    cd Aether
    ```

2.  **Run the Build Script**:
    The repository includes a batch script that automates the entire build process. Simply run it from the project root:
    ```bash
    scripts\\build_windows.bat
    ```

    This script will perform the following actions:
    - **Clean**: Remove any previous `build` or `dist` directories.
    - **Install Dependencies**: Install all required Python packages from `requirements.txt`.
    - **Run PyInstaller**: Use the `build/windows/app.spec` file to package the application.

3.  **Locate the Executable**:
    If the build is successful, the final application will be located in the `dist/irctc_pro_final_build` directory. You can run `IRCTC_Pro.exe` from there.

## First-Time Run (Playwright)

The very first time you run `IRCTC_Pro.exe`, it may seem to take a moment to start. The application needs to download the Playwright browser binaries if they are not found. This is a one-time setup step. Please be patient and allow the download to complete.

## Troubleshooting Common PyInstaller Issues

- **`UPX is not available`**:
  - The build script uses UPX to compress the executable. If you see this warning, the build will still succeed, but the final files will be larger.
  - To fix this, download the latest UPX release for Windows from the [UPX GitHub page](https://github.com/upx/upx/releases) and place `upx.exe` in a directory included in your system's PATH.

- **`ModuleNotFoundError` on Execution**:
  - If the `.exe` runs but immediately crashes with a `ModuleNotFoundError`, it's likely a `hiddenimport` is missing from the `build/windows/app.spec` file.
  - Common libraries that need to be explicitly added include `tzdata` (for `pytz`) and `certifi`. These have already been included, but custom or new dependencies might also need to be added.

- **File Not Found Errors**:
  - If the application runs but cannot find `stationlist.json` or other assets, it means the `datas` section in the `.spec` file is incorrect or a file path is not being resolved correctly.
  - All file access in the code must use the `resource_path` helper from `src/utils/paths.py` to ensure paths work in both development and the packaged application.
