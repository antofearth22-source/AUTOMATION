from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget

class SavedTicketsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel("Your saved ticket configurations will appear here.")
        self.tickets_list = QListWidget()

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.tickets_list)

        # In the future, this list will be populated from saved_tickets.json
        self.tickets_list.addItem("Example: Delhi -> Mumbai (3A)")
        self.tickets_list.addItem("Example: Chennai -> Kolkata (SL)")

        self.setLayout(self.layout)
