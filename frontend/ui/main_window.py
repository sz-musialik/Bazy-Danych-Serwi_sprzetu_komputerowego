from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QMessageBox,
)
from frontend.api_client import api

from frontend.ui.users_panel import UsersPanel
from frontend.ui.clients_panel import ClientsPanel
from frontend.ui.orders_panel import OrdersPanel
from frontend.ui.parts_panel import PartsPanel
from frontend.ui.parts_orders_panel import PartsOrdersPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Obsługi Serwisu")
        self.resize(1000, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

    def setup_ui(self):
        # Pasek narzedzi (Toolbar)
        self.setup_toolbar()

        # Zakladki (TabWidget)
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Zakladka Zlecenia
        self.orders_tab = OrdersPanel()
        self.tabs.addTab(self.orders_tab, "Zlecenia")

        # Zakladka Klienci
        self.clients_tab = ClientsPanel()
        self.tabs.addTab(self.clients_tab, "Klienci")

        # Zakladka Magazyn
        self.parts_tab = PartsPanel()
        self.tabs.addTab(self.parts_tab, "Magazyn")

        # Zakladka Zamowienia
        self.parts_orders_tab = PartsOrdersPanel()
        self.tabs.addTab(self.parts_orders_tab, "Zamówienia")

        # Logika uprawnien
        role = api.user_data.get("rola", "").lower()

        if role == "administrator":
            self.users_tab = UsersPanel()
            self.tabs.addTab(self.users_tab, "Użytkownicy")

        elif role == "manager":
            self.users_tab = UsersPanel()
            self.tabs.addTab(self.users_tab, "Pracownicy")

    def setup_toolbar(self):
        toolbar = QHBoxLayout()

        self.contrast_btn = QPushButton("Wysoki Kontrast")
        self.contrast_btn.setCheckable(True)
        self.contrast_btn.clicked.connect(self.toggle_contrast)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Polski", "English"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        user_info = (
            f"Zalogowany: {api.user_data.get('login')} ({api.user_data.get('rola')})"
        )
        toolbar.addWidget(QLabel(user_info))
        toolbar.addStretch()
        toolbar.addWidget(self.contrast_btn)
        toolbar.addWidget(self.lang_combo)

        self.layout.insertLayout(0, toolbar)

    def toggle_contrast(self, checked):
        if checked:
            self.setStyleSheet(
                """
                QWidget { background-color: #000; color: #FFF; }
                QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QHeaderView, QSpinBox, QDoubleSpinBox {
                    font-size: 14px;
                }
                QPushButton { background-color: #333; border: 2px solid #FFF; color: #FFF; }
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background-color: #333; color: #FFF; border: 1px solid #FFF; }
                QTableWidget { gridline-color: #FFF; color: #FFF; background-color: #000; }
                QHeaderView::section { background-color: #333; color: #FFF; }
                QDialog { background-color: #000; color: #FFF; }
            """
            )
        else:
            self.setStyleSheet("")

    def change_language(self, index):
        lang = "EN" if index == 1 else "PL"
        role = api.user_data.get("rola", "").lower()

        if lang == "EN":
            self.tabs.setTabText(0, "Repair Orders")
            self.tabs.setTabText(1, "Clients")
            self.tabs.setTabText(2, "Stock")
            self.tabs.setTabText(3, "Part Orders")
            if role == "administrator":
                if hasattr(self, "users_tab"):
                    self.tabs.setTabText(4, "Users")
            elif role == "manager":
                if hasattr(self, "users_tab"):
                    self.tabs.setTabText(4, "Employees")

            self.contrast_btn.setText("High Contrast")
        else:
            self.tabs.setTabText(0, "Zlecenia")
            self.tabs.setTabText(1, "Klienci")
            self.tabs.setTabText(2, "Magazyn")
            self.tabs.setTabText(3, "Zamówienia")
            if role == "administrator":
                if hasattr(self, "users_tab"):
                    self.tabs.setTabText(4, "Użytkownicy")
            elif role == "manager":
                if hasattr(self, "users_tab"):
                    self.tabs.setTabText(4, "Pracownicy")

            self.contrast_btn.setText("Wysoki Kontrast")

        # Wywolujemy zmiane jezyka w poszczegolnych panelach
        if hasattr(self, "users_tab"):
            self.users_tab.set_language(lang)

        self.orders_tab.set_language(lang)
        self.clients_tab.set_language(lang)
        self.parts_tab.set_language(lang)
        self.parts_orders_tab.set_language(lang)
