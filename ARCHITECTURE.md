# PROX Application Architecture

This document outlines the software architecture for the PROX IRCTC booking helper application, designed for Windows 10+ using Python 3.11+, PySide6, and Selenium.

## 1. Project Folder Structure

The project is organized to separate the core source code (`src/`) from user-generated data (`config/`), runtime logs (`logs/`), and project-level files. This structure facilitates clean packaging with PyInstaller.

```
prox/
├── .gitignore                  # Specifies files for Git to ignore (e.g., logs, __pycache__).
├── README.md                   # Project documentation.
├── requirements.txt            # Lists all Python package dependencies (PySide6, Selenium, etc.).
├── main.py                     # The main entry point to launch the PySide6 application.
├── build.spec                  # The PyInstaller specification file for creating the final EXE.
│
├── config/                     # User-specific data, created on first run and stored outside the EXE.
│   ├── settings.json           # General application settings (e.g., window size, selected browser).
│   ├── accounts.json           # Metadata for stored IRCTC accounts (label, username). Passwords are NOT stored here.
│   └── tickets.json            # All saved ticket templates.
│
├── logs/                       # Rotated log files generated during runtime.
│   └── prox_app.log
│
└── src/
    └── prox/
        ├── __init__.py
        │
        ├── assets/             # Static UI assets like icons and stylesheets.
        │   ├── icons/
        │   └── theme.qss
        │
        ├── core/               # Core application services, not specific to UI or automation.
        │   ├── __init__.py
        │   ├── config_manager.py # Handles loading and saving all JSON files from the /config directory.
        │   ├── secret_manager.py # Securely stores and retrieves secrets using the Windows Credential Manager.
        │   └── logging_config.py # Sets up the application-wide logging system.
        │
        ├── models/             # Pydantic data models for type safety and validation.
        │   ├── __init__.py
        │   ├── account.py        # Defines the structure for an IRCTC account.
        │   └── ticket.py         # Defines the structure for a ticket template.
        │
        ├── automation/         # All browser automation logic using Selenium.
        │   ├── __init__.py
        │   ├── driver_factory.py # Creates and configures Selenium WebDriver instances (Chrome/Edge).
        │   ├── irctc_client.py   # The high-level client that orchestrates the booking workflow.
        │   └── selectors.py      # **CRITICAL:** The selector-abstraction layer. All CSS/XPath selectors are defined here.
        │
        └── ui/                 # All PySide6 GUI components.
            ├── __init__.py
            ├── main_window.py    # The main application window shell.
            ├── views/            # Individual screens or panes within the main window.
            │   ├── __init__.py
            │   └── dashboard_view.py
            └── widgets/          # Reusable custom widgets.
                ├── __init__.py
```

## 2. Core Modules and Components

### 2.1. `src/prox/core/` - Core Services
- **`ConfigManager`**: Handles all file I/O for the `/config` directory.
- **`SecretManager`**: Manages secure storage of IRCTC passwords via the Windows Credential Manager.
- **`logging_config`**: Contains a `setup_logging()` function for a global, file-rotating logger.

### 2.2. `src/prox/models/` - Data Models
- **`Account`**: Pydantic model for an IRCTC account (`id`, `label`, `username`).
- **`TicketTemplate`**: Pydantic model for a booking template, including nested `Passenger` models.

### 2.3. `src/prox/automation/` - Browser Automation (Selenium)
- **`DriverFactory`**: Class to create configured Selenium WebDriver instances for Chrome or Edge.
- **`selectors.py`**: The selector-abstraction layer. Centralizes all Selenium element locators (e.g., `(By.ID, 'userId')`) in static classes.
- **`IrctcClient`**: The main automation engine.
    - `__init__(self, driver: WebDriver)`
    - `navigate_to_login()`: Opens the IRCTC login page.
    - `fill_login_credentials(username: str, password: str)`: Fills username and password. **Stops and waits for the user to solve the CAPTCHA manually.**
    - `wait_for_manual_login_completion()`: Waits for the user to successfully solve the CAPTCHA and land on the post-login page before proceeding.
    - `fill_journey_details(ticket: TicketTemplate)`: Fills the main booking form.
    - `fill_passenger_details(ticket: TicketTemplate)`: Fills the passenger details page.
    - `navigate_to_payment_page()`: Proceeds to the payment selection screen and **stops, handing control back to the user.**
    - `close()`: Closes the browser.

### 2.4. `src/prox/ui/` - PySide6 GUI
- **`MainWindow`**: The main application window, responsible for layout, view management, and connecting UI events to the core logic.
- **`DashboardView`**: The main user-facing view containing all the input fields for a booking.

## 3. Data Flow and Validation

1.  **User Interaction (UI)**: User clicks "Book Now".
2.  **Data Collection & Validation (UI -> Models)**: UI data is collected and used to instantiate a `TicketTemplate` Pydantic model. This step enforces all data validation rules (date range, passenger age, etc.). If validation fails, an error is shown to the user, and the process stops.
3.  **Core Logic Invocation (UI -> Automation)**:
    - The `MainWindow` retrieves the selected `Account` and password (via `SecretManager`).
    - A **Selenium WebDriver** is created using the `DriverFactory`.
    - An `IrctcClient` instance is created with the driver.
    - A high-level booking function is called, passing the validated `TicketTemplate` and account details.
4.  **Automation Execution (Automation)**: The `IrctcClient` executes its workflow:
    - Navigates to the login page and fills credentials.
    - **Pauses**, allowing the user to see the browser window and solve the CAPTCHA.
    - After the user logs in, the client detects the page change and proceeds to automatically fill all subsequent forms.
    - The process **stops** at the payment page, leaving the browser open for the user.

## 4. Logging and Error Handling

- **Logging**: A central logger will write to a rotating file in `/logs` and emit signals to the UI for real-time status updates (e.g., "Waiting for manual CAPTCHA solve...").
- **Error Handling**: Custom exceptions (e.g., `ElementNotFoundError`) will be used to handle automation failures, such as when an IRCTC selector changes. These errors will be caught, logged, and displayed to the user with clear messages. A global exception hook will catch any unhandled errors.
