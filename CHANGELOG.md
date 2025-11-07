# Changelog

## [Unreleased] - 2025-11-06

### Added
- **Secure Credential Vault**: Implemented a new system for securely storing multiple IRCTC accounts, called "slots".
  - Secrets are stored in the Windows Credential Manager via the `keyring` library.
  - Account metadata is stored in `%APPDATA%\\IrctcPro\\config\\vault_index.json`.
- **GUI for Account Management**: Added a new "Accounts" tab in the Settings screen to add, edit, and delete credential slots.
- **Quick Account Switching**: Added a dropdown in the main window to quickly switch between active accounts, which clears the session for security.
- **Vault CLI Tool**: Created `scripts/vault_tools.py` for command-line management of the credential vault.

### Changed
- Overhauled the Settings screen to a tabbed interface to support the new Accounts section.
- Updated the PyInstaller build spec (`app.spec`) to include hidden imports for `keyring` and `pywin32`.

### Fixed
- The application is now fully compliant with `ruff` and `mypy` static analysis.
- Corrected numerous import and type-hinting errors.
