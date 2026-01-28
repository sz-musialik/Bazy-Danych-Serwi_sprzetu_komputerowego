from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QHeaderView,
    QLabel,
    QGroupBox,
    QDoubleSpinBox,
    QDateEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QPalette, QBrush
from frontend.api_client import api


# Podswietlanie Calego Wiersza
class RowHoverDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_row = -1

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)

        if opt.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(opt.rect, opt.palette.highlight())
            opt.palette.setColor(
                QPalette.ColorRole.Text, opt.palette.highlightedText().color()
            )
        elif index.row() == self.hovered_row:
            hover_color = QColor(82, 100, 128)
            painter.fillRect(opt.rect, hover_color)
            opt.state |= QStyle.StateFlag.State_MouseOver

        super().paint(painter, opt, index)


class RolesCache:
    roles = {}  # "administrator": 1
    roles_rev = {}  # 1: "administrator"

    @classmethod
    def load(cls):
        data = api.get_roles() or []
        cls.roles = {r["nazwa_rola"]: r["id_rola"] for r in data}
        cls.roles_rev = {r["id_rola"]: r["nazwa_rola"] for r in data}


class UserAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj nowego użytkownika")
        self.resize(400, 450)

        self.logged_user_role = api.user_data.get("rola", "").lower()
        layout = QFormLayout(self)

        self.login_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.imie_edit = QLineEdit()
        self.nazwisko_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.tel_edit = QLineEdit()

        layout.addRow("Login (wymagane):", self.login_edit)
        layout.addRow("Hasło (wymagane):", self.password_edit)
        layout.addRow("Imię (wymagane):", self.imie_edit)
        layout.addRow("Nazwisko (wymagane):", self.nazwisko_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Telefon:", self.tel_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(list(RolesCache.roles.keys()))
        layout.addRow("Rola:", self.role_combo)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Utwórz")
        cancel_btn = QPushButton("Anuluj")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        return {
            "login": self.login_edit.text(),
            "password": self.password_edit.text(),
            "imie": self.imie_edit.text(),
            "nazwisko": self.nazwisko_edit.text(),
            "email": self.email_edit.text(),
            "nr_telefonu": self.tel_edit.text(),
            "rola_id": RolesCache.roles.get(self.role_combo.currentText()),
        }


class ResetPasswordDialog(QDialog):
    def __init__(self, user_login, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Reset hasła: {user_login}")
        self.resize(350, 200)

        layout = QFormLayout(self)
        self.pass1 = QLineEdit()
        self.pass1.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass2 = QLineEdit()
        self.pass2.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Nowe hasło:", self.pass1)
        layout.addRow("Powtórz hasło:", self.pass2)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Potwierdź")
        cancel_btn = QPushButton("Anuluj")
        save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def validate_and_accept(self):
        p1 = self.pass1.text()
        p2 = self.pass2.text()
        if not p1 or not p2:
            QMessageBox.warning(self, "Błąd", "Hasło nie może być puste.")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Błąd", "Podane hasła nie są identyczne!")
            return
        self.accept()

    def get_new_password(self):
        return self.pass1.text()


class UserDetailsDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Szczegóły użytkownika: {user_data.get('login', '')}")
        self.resize(500, 600)
        self.user_data = user_data
        self.logged_user_role = api.user_data.get("rola", "").lower()

        self.is_admin = self.logged_user_role == "administrator"
        self.is_read_only = self.logged_user_role == "manager"

        layout = QFormLayout(self)

        self.id_edit = QLineEdit(str(user_data.get("id_uzytkownika", "")))
        self.id_edit.setReadOnly(True)
        layout.addRow("ID:", self.id_edit)

        self.login_edit = QLineEdit(user_data.get("login", ""))
        self.login_edit.setReadOnly(True)
        layout.addRow("Login:", self.login_edit)

        self.imie_edit = QLineEdit(user_data.get("imie", ""))
        layout.addRow("Imię:", self.imie_edit)

        self.nazwisko_edit = QLineEdit(user_data.get("nazwisko", ""))
        layout.addRow("Nazwisko:", self.nazwisko_edit)

        self.email_edit = QLineEdit(user_data.get("email", ""))
        layout.addRow("Email:", self.email_edit)

        self.tel_edit = QLineEdit(user_data.get("nr_telefonu", ""))
        layout.addRow("Telefon:", self.tel_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(list(RolesCache.roles.keys()))
        current_role_id = user_data.get("rola_uzytkownika")
        current_role_name = RolesCache.roles_rev.get(current_role_id, "")
        self.role_combo.setCurrentText(current_role_name)
        layout.addRow("Rola:", self.role_combo)

        self.active_cb = QCheckBox("Użytkownik aktywny")
        self.active_cb.setChecked(bool(user_data.get("czy_aktywny", True)))
        layout.addRow("Status:", self.active_cb)

        self.kadry_group = QGroupBox("Dane Kadrowe")
        kadry_layout = QFormLayout()

        self.pesel_edit = QLineEdit(user_data.get("pesel") or "")
        self.pesel_edit.setMaxLength(11)
        kadry_layout.addRow("PESEL:", self.pesel_edit)

        self.konto_edit = QLineEdit(user_data.get("nr_konta") or "")
        kadry_layout.addRow("Nr Konta:", self.konto_edit)

        self.adres_edit = QLineEdit(user_data.get("adres_zamieszkania") or "")
        kadry_layout.addRow("Adres:", self.adres_edit)

        self.stawka_spin = QDoubleSpinBox()
        self.stawka_spin.setRange(0, 9999.99)
        self.stawka_spin.setSuffix(" PLN/h")
        self.stawka_spin.setValue(float(user_data.get("stawka_godzinowa") or 0))
        kadry_layout.addRow("Stawka:", self.stawka_spin)

        self.data_zatr_edit = QDateEdit()
        self.data_zatr_edit.setCalendarPopup(True)
        self.data_zatr_edit.setDisplayFormat("yyyy-MM-dd")

        d_zatr_str = user_data.get("data_zatrudnienia")
        if d_zatr_str:
            self.data_zatr_edit.setDate(QDate.fromString(d_zatr_str, "yyyy-MM-dd"))
        else:
            self.data_zatr_edit.setDate(QDate.currentDate())

        kadry_layout.addRow("Data zatrudnienia:", self.data_zatr_edit)
        self.kadry_group.setLayout(kadry_layout)
        layout.addRow(self.kadry_group)

        if self.is_read_only:
            self.imie_edit.setReadOnly(True)
            self.nazwisko_edit.setReadOnly(True)
            self.email_edit.setReadOnly(True)
            self.tel_edit.setReadOnly(True)
            self.role_combo.setEnabled(False)
            self.active_cb.setEnabled(False)
            self.pesel_edit.setReadOnly(True)
            self.konto_edit.setReadOnly(True)
            self.adres_edit.setReadOnly(True)
            self.stawka_spin.setReadOnly(True)
            self.data_zatr_edit.setReadOnly(True)
            self.data_zatr_edit.setEnabled(False)
            self.setWindowTitle(
                f"Szczegóły pracownika: {user_data.get('login', '')} (Tylko podgląd)"
            )

        btn_box = QHBoxLayout()
        if not self.is_read_only:
            save_btn = QPushButton("Zapisz Zmiany")
            save_btn.clicked.connect(self.accept)
            btn_box.addWidget(save_btn)

        cancel_btn = QPushButton("Zamknij" if self.is_read_only else "Anuluj")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        data = {
            "imie": self.imie_edit.text(),
            "nazwisko": self.nazwisko_edit.text(),
            "email": self.email_edit.text(),
            "nr_telefonu": self.tel_edit.text(),
            "rola_uzytkownika": RolesCache.roles.get(self.role_combo.currentText()),
            "czy_aktywny": self.active_cb.isChecked(),
        }
        if self.is_admin:
            data["pesel"] = self.pesel_edit.text()
            data["nr_konta"] = self.konto_edit.text()
            data["adres_zamieszkania"] = self.adres_edit.text()
            data["stawka_godzinowa"] = self.stawka_spin.value()
            data["data_zatrudnienia"] = self.data_zatr_edit.date().toString(
                "yyyy-MM-dd"
            )
        return data


class UsersPanel(QWidget):
    def __init__(self):
        super().__init__()
        RolesCache.load()

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Hover
        self.table.setMouseTracking(True)
        self.hover_delegate = RowHoverDelegate(self.table)
        self.table.setItemDelegate(self.hover_delegate)
        self.table.viewport().installEventFilter(self)

        self.layout.addWidget(self.table)

        self.table.doubleClicked.connect(self.open_details)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Odśwież")
        self.details_btn = QPushButton("Szczegóły")

        self.user_role = api.user_data.get("rola", "").lower()

        self.refresh_btn.clicked.connect(self.load_data)
        self.details_btn.clicked.connect(self.open_details)

        btn_layout.addWidget(self.refresh_btn)

        if self.user_role == "administrator":
            self.add_btn = QPushButton("Dodaj Użytkownika")
            self.add_btn.clicked.connect(self.add_user)
            btn_layout.addWidget(self.add_btn)
            self.details_btn.setText("Szczegóły / Edycja")

        btn_layout.addWidget(self.details_btn)

        if self.user_role == "administrator":
            self.archive_btn = QPushButton("Archiwizuj Użytkownika")
            self.archive_btn.setStyleSheet("background-color: #660000; color: white;")
            self.archive_btn.clicked.connect(self.archive_user)
            btn_layout.addWidget(self.archive_btn)

            self.reset_pwd_btn = QPushButton("Resetuj Hasło")
            self.reset_pwd_btn.setStyleSheet("background-color: #d35400; color: white;")
            self.reset_pwd_btn.clicked.connect(self.reset_password)
            btn_layout.addWidget(self.reset_pwd_btn)

        self.layout.addLayout(btn_layout)

        self.users_cache = []
        self.set_language("PL")
        self.load_data()

    def eventFilter(self, source, event):
        if source is self.table.viewport():
            if event.type() == event.Type.MouseMove:
                index = self.table.indexAt(event.pos())
                if index.isValid():
                    self.hover_delegate.hovered_row = index.row()
                else:
                    self.hover_delegate.hovered_row = -1
                self.table.viewport().update()
            elif event.type() == event.Type.Leave:
                self.hover_delegate.hovered_row = -1
                self.table.viewport().update()
        return super().eventFilter(source, event)

    def set_language(self, lang):
        if lang == "EN":
            headers = [
                "First Name",
                "Last Name",
                "Email",
                "Phone",
                "Role",
                "Active",
            ]  # Bez ID
            self.refresh_btn.setText("Refresh")
            if self.user_role == "administrator":
                self.add_btn.setText("Add User")
                self.details_btn.setText("Details / Edit")
                self.archive_btn.setText("Archive User")
                self.reset_pwd_btn.setText("Reset Password")
            else:
                self.details_btn.setText("Details")
        else:
            headers = [
                "Imię",
                "Nazwisko",
                "Email",
                "Telefon",
                "Rola",
                "Aktywny",
            ]
            self.refresh_btn.setText("Odśwież")
            if self.user_role == "administrator":
                self.add_btn.setText("Dodaj Użytkownika")
                self.details_btn.setText("Szczegóły / Edycja")
                self.archive_btn.setText("Archiwizuj Użytkownika")
                self.reset_pwd_btn.setText("Resetuj Hasło")
            else:
                self.details_btn.setText("Szczegóły")

        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self):
        self.users_cache = api.get_users()
        self.table.setRowCount(len(self.users_cache))

        for i, u in enumerate(self.users_cache):
            role_id = u.get("rola_uzytkownika")
            role_name = RolesCache.roles_rev.get(role_id, str(role_id))
            is_active = u.get("czy_aktywny", False)
            active_txt = "Tak" if is_active else "Nie"

            items = [
                QTableWidgetItem(u.get("imie", "")),
                QTableWidgetItem(u.get("nazwisko", "")),
                QTableWidgetItem(u.get("email", "")),
                QTableWidgetItem(u.get("nr_telefonu", "")),
                QTableWidgetItem(role_name),
                QTableWidgetItem(active_txt),
            ]

            if not is_active:
                gray = QColor("gray")
                for item in items:
                    item.setForeground(gray)

            for col, item in enumerate(items):
                self.table.setItem(i, col, item)

    def add_user(self):
        dialog = UserAddDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if (
                not data["login"]
                or not data["password"]
                or not data["imie"]
                or not data["nazwisko"]
            ):
                QMessageBox.warning(
                    self,
                    "Błąd",
                    "Wypełnij pola wymagane (Login, Hasło, Imię, Nazwisko)",
                )
                return
            success, msg = api.create_user(data)
            if success:
                QMessageBox.information(self, "Sukces", "Utworzono użytkownika")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def open_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz użytkownika z listy")
            return
        user_data = self.users_cache[row]
        dialog = UserDetailsDialog(user_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            success, msg = api.update_user(user_data["id_uzytkownika"], new_data)
            if success:
                QMessageBox.information(
                    self, "Sukces", "Zaktualizowano dane użytkownika"
                )
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def archive_user(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz użytkownika do archiwizacji")
            return
        user_data = self.users_cache[row]
        current_login = api.user_data.get("login")
        if user_data.get("login") == current_login:
            QMessageBox.critical(
                self, "Błąd", "Nie możesz zarchiwizować własnego konta!"
            )
            return
        confirm = QMessageBox.question(
            self,
            "Potwierdzenie",
            f"Czy na pewno chcesz dezaktywować konto użytkownika '{user_data.get('login')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success, msg = api.update_user(
                user_data["id_uzytkownika"], {"czy_aktywny": False}
            )
            if success:
                QMessageBox.information(
                    self, "Sukces", "Użytkownik został zarchiwizowany."
                )
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def reset_password(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Uwaga", "Wybierz użytkownika, któremu chcesz zmienić hasło"
            )
            return
        user_data = self.users_cache[row]
        dialog = ResetPasswordDialog(user_data.get("login"), self)
        if dialog.exec():
            new_password = dialog.get_new_password()
            success, msg = api.update_user(
                user_data["id_uzytkownika"], {"password": new_password}
            )
            if success:
                QMessageBox.information(self, "Sukces", "Hasło zostało zmienione.")
            else:
                QMessageBox.critical(self, "Błąd", str(msg))
