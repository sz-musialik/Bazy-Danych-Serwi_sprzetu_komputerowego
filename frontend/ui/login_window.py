from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from frontend.api_client import api


class LoginWindow(QWidget):
    def __init__(self, on_success_callback):
        super().__init__()
        self.on_success_callback = on_success_callback
        self.setWindowTitle("Serwis - Logowanie")
        self.resize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Login")
        self.login_input.setText("admin")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Hasło")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin123")

        self.login_btn = QPushButton("Zaloguj")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addWidget(QLabel("Witaj w systemie Serwis"))
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        success, message = api.login(login, password)

        if success:
            self.on_success_callback()
            self.close()
        else:
            QMessageBox.critical(self, "Błąd", message)
