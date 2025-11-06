# IRCTC Pro Tatkal Booking Assistant

IRCTC Pro is a comprehensive, Windows-based application designed to automate the IRCTC Tatkal ticket booking process with high precision and reliability. It combines a user-friendly PySide6 GUI with a powerful Playwright automation engine.

## Key Features

- **Real-time Monitoring**: Live log console with slot status and color-coded entries.
- **Millisecond Precision**: NTP-synchronized timing for exact Tatkal opening execution.
- **One-Click Booking**: Pre-configured tickets for instant execution.
- **Parallel Processing**: Up to 3 simultaneous booking attempts with isolated browser profiles.
- **Portable Design**: No installation required, works on any Windows system.
- **Visual Interface**: Clean dashboard with status indicators and slot management.
- **Complete Station List**: Full IRCTC station database for autocomplete.
- **Payment Flexibility**: Support for both UPI and card payment methods.
- **Security**: Secure credential storage using Windows Credential Manager and DPAPI.
- **Decoupled CAPTCHA Solving**: Uses an external, separately compiled CAPTCHA solver for security and modularity.

## Build and Deployment

This project has a two-part build process: one for the main application and one for the CAPTCHA solver. The target platform is Windows 10/11 with Python 3.11.

### 1. Build the CAPTCHA Solver

First, build the standalone CAPTCHA solver executable. This tool requires its own API credentials, which must be set in a `.env` file.

1.  Navigate to `tools/captcha_solver/`.
2.  Create a `.env` file by copying the `.env.example` and filling in your `TRUECAPTCHA_USERID` and `TRUECAPTCHA_APIKEY`.
3.  From the project root, run the build script:
    ```bash
    .\\scripts\\build_captcha_solver.bat
    ```
This will create `dist/captcha_solver/captcha_solver.exe`.

### 2. Build the Main Application

Next, build the main IRCTC Pro application:

1.  From the project root, run the main build script:
    ```bash
    .\\scripts\\build_windows.bat
    ```
This will create the main application bundle in `dist/irctc_pro/`.

### 3. Final Configuration

After building, you must perform one manual step for the application to function correctly:

1.  **Copy the solver**: Copy the `captcha_solver.exe` from `dist/captcha_solver/` into the main application directory, `dist/irctc_pro/`.
2.  **Configure the path**: After running the main application for the first time, it will create a `data` directory. Open the file `data/config.json` inside the `dist/irctc_pro/` folder and set the `CAPTCHA_SOLVER_PATH` to point to the executable. For example:
    ```json
    {
        "CAPTCHA_SOLVER_PATH": "captcha_solver.exe",
        "LOG_LEVEL": "INFO",
        "MAX_RETRIES": 3
    }
    ```
The application is now ready to use.
