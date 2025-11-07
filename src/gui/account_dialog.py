from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox
)

class AccountDialog(QDialog):
    """A dialog for adding or editing an account slot."""
    def __init__(self, slot_data=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New Account" if slot_data is None else "Edit Account")

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.label_input = QLineEdit()
        self.userid_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.totp_input = QLineEdit()

        form_layout.addRow("Label:", self.label_input)
        form_layout.addRow("IRCTC User ID:", self.userid_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("TOTP Secret (Optional):", self.totp_input)

        self.layout.addLayout(form_layout)

        # Add OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

        if slot_data:
            self.label_input.setText(slot_data.get("label", ""))
            self.userid_input.setText(slot_data.get("irctc_userid", ""))
            self.password_input.setPlaceholderText("Leave empty to keep unchanged")

    def get_data(self) -> dict:
        """Returns the data entered in the dialog."""
        return {
            "label": self.label_input.text(),
            "irctc_userid": self.userid_input.text(),
            "password": self.password_input.text(),
            "totp_secret": self.totp_input.text()
        }
