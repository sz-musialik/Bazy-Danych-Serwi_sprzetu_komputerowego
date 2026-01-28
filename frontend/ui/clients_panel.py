from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QHeaderView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QBrush  # <--- DODANO
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


# Okno Dialogowe
class ClientDialog(QDialog):
    def __init__(self, parent=None, client_data=None):
        super().__init__(parent)
        self.setWindowTitle("Dane Klienta")
        self.client_data = client_data
        self.resize(400, 300)

        layout = QFormLayout(self)

        self.imie_edit = QLineEdit(client_data.get("imie", "") if client_data else "")
        self.nazwisko_edit = QLineEdit(
            client_data.get("nazwisko", "") if client_data else ""
        )
        self.email_edit = QLineEdit(client_data.get("email", "") if client_data else "")
        self.tel_edit = QLineEdit(
            client_data.get("nr_telefonu", "") if client_data else ""
        )
        self.adres_edit = QLineEdit(client_data.get("adres", "") if client_data else "")

        layout.addRow("Imię:", self.imie_edit)
        layout.addRow("Nazwisko:", self.nazwisko_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Telefon:", self.tel_edit)
        layout.addRow("Adres:", self.adres_edit)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Zapisz")
        cancel_btn = QPushButton("Anuluj")

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        return {
            "imie": self.imie_edit.text(),
            "nazwisko": self.nazwisko_edit.text(),
            "email": self.email_edit.text(),
            "nr_telefonu": self.tel_edit.text(),
            "adres": self.adres_edit.text(),
        }


# Panel Glowny
class ClientsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.clients_cache = []
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Hover Setup
        self.table.setMouseTracking(True)
        self.hover_delegate = RowHoverDelegate(self.table)
        self.table.setItemDelegate(self.hover_delegate)
        self.table.viewport().installEventFilter(self)

        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Odśwież")
        self.add_btn = QPushButton("Dodaj Klienta")
        self.edit_btn = QPushButton("Edytuj Klienta")

        self.user_role = api.user_data.get("rola", "").lower()

        if self.user_role != "administrator":
            self.edit_btn.setEnabled(False)
            self.edit_btn.setToolTip("Tylko administrator może edytować dane klientów")

        self.refresh_btn.clicked.connect(self.load_data)
        self.add_btn.clicked.connect(self.add_client)
        self.edit_btn.clicked.connect(self.edit_client)

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        self.layout.addLayout(btn_layout)

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
            headers = ["First Name", "Last Name", "Email", "Phone", "Address"]
            self.refresh_btn.setText("Refresh")
            self.add_btn.setText("Add Client")
            self.edit_btn.setText("Edit Client")
        else:
            headers = ["Imię", "Nazwisko", "Email", "Telefon", "Adres"]
            self.refresh_btn.setText("Odśwież")
            self.add_btn.setText("Dodaj Klienta")
            self.edit_btn.setText("Edytuj Klienta")

        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self):
        scope = "active_orders" if self.user_role == "pracownik" else None
        self.clients_cache = api.get_clients(scope=scope)

        self.table.setRowCount(len(self.clients_cache))
        for i, c in enumerate(self.clients_cache):
            c_imie = str(c.get("imie") or "")
            c_nazwisko = str(c.get("nazwisko") or "")
            c_email = str(c.get("email") or "")
            c_tel = str(c.get("nr_telefonu") or "")
            c_adres = str(c.get("adres", "") or "")

            self.table.setItem(i, 0, QTableWidgetItem(c_imie))
            self.table.setItem(i, 1, QTableWidgetItem(c_nazwisko))
            self.table.setItem(i, 2, QTableWidgetItem(c_email))
            self.table.setItem(i, 3, QTableWidgetItem(c_tel))
            self.table.setItem(i, 4, QTableWidgetItem(c_adres))

    def add_client(self):
        dialog = ClientDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            success, resp = api.create_client(**data)
            if success:
                QMessageBox.information(self, "Sukces", "Dodano klienta")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(resp))

    def edit_client(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz klienta do edycji")
            return

        client_data = self.clients_cache[row]
        client_id = client_data["id_klienta"]

        current_data = {
            "imie": client_data.get("imie", ""),
            "nazwisko": client_data.get("nazwisko", ""),
            "email": client_data.get("email", ""),
            "nr_telefonu": client_data.get("nr_telefonu", ""),
            "adres": client_data.get("adres", ""),
        }

        dialog = ClientDialog(self, current_data)
        if dialog.exec():
            new_data = dialog.get_data()
            success, err = api.update_client(client_id, new_data)
            if success:
                QMessageBox.information(self, "Sukces", "Zaktualizowano dane")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(err))
