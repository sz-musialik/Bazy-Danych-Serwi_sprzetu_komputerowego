import os
import textwrap
from datetime import datetime
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
    QTextEdit,
    QHeaderView,
    QLabel,
    QDateEdit,
    QDoubleSpinBox,
    QScrollArea,
    QGroupBox,
    QSpinBox,
    QFileDialog,
    QCheckBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from PyQt6.QtCore import Qt, QDate, QModelIndex
from PyQt6.QtGui import QColor, QPalette, QBrush
from frontend.api_client import api

# Importy Do Pdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors


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


class DictionaryCache:
    types = {}
    statuses = {}
    statuses_rev = {}

    @classmethod
    def load(cls):
        cls.types = api.get_equipment_types() or {}
        cls.statuses = api.get_statuses() or {}
        cls.statuses_rev = {v: k for k, v in cls.statuses.items()}


class ClientSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz Klienta")
        self.resize(600, 400)
        self.selected_client = None
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Szukaj:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Imię / Nazwisko / Telefon...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Imię", "Nazwisko", "Telefon"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.select_and_close)
        layout.addWidget(self.table)
        self.all_clients = []
        self.load_clients()

    def load_clients(self):
        self.all_clients = api.get_clients()
        self.populate_table(self.all_clients)

    def populate_table(self, clients_list):
        self.table.setRowCount(len(clients_list))
        for i, c in enumerate(clients_list):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.get("id_klienta") or "")))
            self.table.setItem(i, 1, QTableWidgetItem(str(c.get("imie") or "")))
            self.table.setItem(i, 2, QTableWidgetItem(str(c.get("nazwisko") or "")))
            self.table.setItem(i, 3, QTableWidgetItem(str(c.get("nr_telefonu") or "")))

    def filter_table(self):
        text = self.search_input.text().lower()
        filtered = [
            c
            for c in self.all_clients
            if text in (c.get("imie") or "").lower()
            or text in (c.get("nazwisko") or "").lower()
            or text in str(c.get("nr_telefonu") or "")
        ]
        self.populate_table(filtered)

    def select_and_close(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_client = {
                "id": int(self.table.item(row, 0).text()),
                "display": f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}",
            }
            self.accept()


class OrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nowe Zlecenie")
        self.resize(500, 400)
        self.selected_client_id = None
        self.layout = QFormLayout(self)

        client_layout = QHBoxLayout()
        self.client_display = QLineEdit()
        self.client_display.setPlaceholderText("Nie wybrano klienta")
        self.client_display.setReadOnly(True)
        self.select_client_btn = QPushButton("Szukaj...")
        self.select_client_btn.clicked.connect(self.open_client_selector)
        client_layout.addWidget(self.client_display)
        client_layout.addWidget(self.select_client_btn)
        self.layout.addRow("Klient:", client_layout)

        self.type_combo = QComboBox()
        self.type_combo.addItems(DictionaryCache.types.keys())
        self.layout.addRow("Typ sprzętu:", self.type_combo)

        self.opis_edit = QTextEdit()
        self.layout.addRow("Opis usterki:", self.opis_edit)
        self.marka_edit = QLineEdit()
        self.layout.addRow("Marka:", self.marka_edit)
        self.model_edit = QLineEdit()
        self.layout.addRow("Model:", self.model_edit)
        self.sn_edit = QLineEdit()
        self.layout.addRow("Nr Seryjny:", self.sn_edit)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Utwórz")
        cancel_btn = QPushButton("Anuluj")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        self.layout.addRow(btn_box)

    def open_client_selector(self):
        selector = ClientSelectorDialog(self)
        if selector.exec() and selector.selected_client:
            self.selected_client_id = selector.selected_client["id"]
            self.client_display.setText(selector.selected_client["display"])

    def get_data(self):
        return {
            "id_klienta": self.selected_client_id,
            "id_typu_sprzetu": DictionaryCache.types.get(self.type_combo.currentText()),
            "opis_usterki": self.opis_edit.toPlainText(),
            "marka": self.marka_edit.text(),
            "model": self.model_edit.text(),
            "sn": self.sn_edit.text(),
            "status_zlecenia": 1,
        }


class OrderDetailsDialog(QDialog):
    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Szczegóły zlecenia #{order_data['id_zlecenia']}")
        self.resize(800, 850)
        self.order_data = order_data
        self.user_role = api.user_data.get("rola", "").lower()

        self.available_parts = []
        self.used_parts_list = []

        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        self.lbl_id = QLineEdit(str(order_data["id_zlecenia"]))
        self.lbl_id.setReadOnly(True)
        self.lbl_klient = QLineEdit(order_data.get("klient_imie_nazwisko", ""))
        self.lbl_klient.setReadOnly(True)
        self.form_layout.addRow("ID:", self.lbl_id)
        self.form_layout.addRow("Klient:", self.lbl_klient)

        self.worker_combo = QComboBox()
        self.workers_map = {}
        users = api.get_users()
        current_worker_id = order_data.get("id_pracownika")
        for u in users:
            display_text = f"{u['imie']} {u['nazwisko']} ({u.get('rola', 'user')})"
            u_id = u["id_uzytkownika"]
            self.workers_map[display_text] = u_id
            self.worker_combo.addItem(display_text)
            if u_id == current_worker_id:
                self.worker_combo.setCurrentText(display_text)
        if self.user_role == "pracownik":
            self.worker_combo.setEnabled(False)
        self.form_layout.addRow("Przypisany pracownik:", self.worker_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(DictionaryCache.statuses.keys())
        current_status_txt = DictionaryCache.statuses_rev.get(
            order_data["status_zlecenia"], ""
        )
        self.status_combo.setCurrentText(current_status_txt)
        self.status_combo.currentIndexChanged.connect(self.handle_status_change)
        self.form_layout.addRow("Status:", self.status_combo)

        self.opis_edit = QTextEdit(order_data.get("opis_usterki") or "")
        self.form_layout.addRow("Opis usterki:", self.opis_edit)
        self.marka_edit = QLineEdit(order_data.get("marka_sprzetu") or "")
        self.form_layout.addRow("Marka:", self.marka_edit)
        self.model_edit = QLineEdit(order_data.get("model_sprzetu") or "")
        self.form_layout.addRow("Model:", self.model_edit)
        self.sn_edit = QLineEdit(order_data.get("numer_seryjny") or "")
        self.form_layout.addRow("Nr Seryjny:", self.sn_edit)
        self.diagnoza_edit = QTextEdit(order_data.get("diagnoza") or "")
        self.form_layout.addRow("Diagnoza:", self.diagnoza_edit)
        self.czynnosci_edit = QTextEdit(order_data.get("wykonane_czynnosci") or "")
        self.form_layout.addRow("Wykonane czynności:", self.czynnosci_edit)

        self.parts_group = QGroupBox("Wykorzystane części (Magazyn)")
        parts_layout = QVBoxLayout()
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(5)
        self.parts_table.setHorizontalHeaderLabels(
            ["ID", "Nazwa Części", "Ilość", "Cena jedn.", "Suma"]
        )
        self.parts_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.parts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.parts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.parts_table.setMinimumHeight(150)
        parts_layout.addWidget(self.parts_table)

        add_part_layout = QHBoxLayout()
        self.part_select_combo = QComboBox()
        self.part_select_combo.setPlaceholderText("Wybierz część z magazynu...")
        self.part_qty_spin = QSpinBox()
        self.part_qty_spin.setRange(1, 100)
        self.part_qty_spin.setSuffix(" szt.")

        self.add_part_btn = QPushButton("Dodaj część")
        self.add_part_btn.clicked.connect(self.add_used_part)
        self.del_part_btn = QPushButton("Usuń zaznaczone")
        self.del_part_btn.clicked.connect(self.delete_used_part)
        self.del_part_btn.setStyleSheet("background-color: #660000; color: white;")

        add_part_layout.addWidget(QLabel("Część:"))
        add_part_layout.addWidget(self.part_select_combo, 2)
        add_part_layout.addWidget(QLabel("Ilość:"))
        add_part_layout.addWidget(self.part_qty_spin)
        add_part_layout.addWidget(self.add_part_btn)
        add_part_layout.addWidget(self.del_part_btn)

        parts_layout.addLayout(add_part_layout)
        self.parts_group.setLayout(parts_layout)
        self.form_layout.addRow(self.parts_group)

        self.koszt_robocizny = QDoubleSpinBox()
        self.koszt_robocizny.setMaximum(99999.99)
        self.koszt_robocizny.setValue(float(order_data.get("koszt_robocizny") or 0))
        self.form_layout.addRow("Koszt robocizny:", self.koszt_robocizny)

        self.koszt_czesci = QDoubleSpinBox()
        self.koszt_czesci.setMaximum(99999.99)
        self.koszt_czesci.setValue(float(order_data.get("koszt_czesci") or 0))
        self.form_layout.addRow("Koszt części:", self.koszt_czesci)

        if self.user_role != "administrator":
            self.koszt_robocizny.setReadOnly(True)
            self.koszt_czesci.setReadOnly(True)
            self.koszt_robocizny.setStyleSheet("background-color: #333; color: #aaa;")
            self.koszt_czesci.setStyleSheet("background-color: #333; color: #aaa;")

        def safe_parse_date(date_str):
            if not date_str:
                return QDate.currentDate()
            date_str = str(date_str).split(" ")[0]
            d = QDate.fromString(date_str, "yyyy-MM-dd")
            return d if d.isValid() else QDate.currentDate()

        self.data_rozp = QDateEdit()
        self.data_rozp.setCalendarPopup(True)
        self.data_rozp.setDisplayFormat("yyyy-MM-dd")
        self.data_rozp.setDate(safe_parse_date(order_data.get("data_rozpoczecia")))
        self.form_layout.addRow("Data rozpoczęcia:", self.data_rozp)

        self.data_zak = QDateEdit()
        self.data_zak.setCalendarPopup(True)
        self.data_zak.setDisplayFormat("yyyy-MM-dd")
        self.data_zak.setDate(safe_parse_date(order_data.get("data_zakonczenia")))

        self.has_end_date = QComboBox()
        self.has_end_date.addItems(["Nieustalona", "Ustalona"])
        if order_data.get("data_zakonczenia"):
            self.has_end_date.setCurrentIndex(1)

        self.form_layout.addRow("Data zakończenia:", self.has_end_date)
        self.form_layout.addRow("Wybór daty zak.:", self.data_zak)

        if self.user_role == "pracownik":
            self.data_rozp.setReadOnly(True)
            self.data_zak.setReadOnly(True)
            self.has_end_date.setEnabled(False)

        self.handle_status_change()
        self.load_available_parts()
        self.load_used_parts()

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Zapisz Zmiany")
        cancel_btn = QPushButton("Anuluj")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        main_layout.addLayout(btn_box)

    def load_available_parts(self):
        self.available_parts = api.get_parts() or []
        self.part_select_combo.clear()
        for p in self.available_parts:
            if p.get("ilosc_dostepna", 0) > 0:
                self.part_select_combo.addItem(
                    f"{p['nazwa_czesci']} (Dostępne: {p['ilosc_dostepna']}, Cena: {p['cena_katalogowa']} PLN)",
                    p["id_czesci"],
                )

    def load_used_parts(self):
        order_id = self.order_data["id_zlecenia"]
        self.used_parts_list = api.get_order_used_parts(order_id) or []
        self.parts_table.setRowCount(len(self.used_parts_list))
        total_parts_cost = 0.0
        parts_map = {p["id_czesci"]: p["nazwa_czesci"] for p in self.available_parts}

        for i, up in enumerate(self.used_parts_list):
            part_id = up["id_czesci"]
            qty = up["ilosc"]
            price = float(up["cena_jednostkowa"])
            row_sum = qty * price
            total_parts_cost += row_sum
            part_name = parts_map.get(part_id, f"Część ID: {part_id}")

            self.parts_table.setItem(i, 0, QTableWidgetItem(str(up.get("id_pozycji"))))
            self.parts_table.setItem(i, 1, QTableWidgetItem(part_name))
            self.parts_table.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.parts_table.setItem(i, 3, QTableWidgetItem(f"{price:.2f}"))
            self.parts_table.setItem(i, 4, QTableWidgetItem(f"{row_sum:.2f}"))

        self.koszt_czesci.setValue(total_parts_cost)

    def add_used_part(self):
        idx = self.part_select_combo.currentIndex()
        if idx < 0:
            return
        part_id = self.part_select_combo.currentData()
        qty = self.part_qty_spin.value()
        part_data = next(
            (p for p in self.available_parts if p["id_czesci"] == part_id), None
        )
        if not part_data:
            return
        price = part_data.get("cena_katalogowa")

        success, response = api.add_order_used_part(
            self.order_data["id_zlecenia"], part_id, qty, price
        )
        if success:
            QMessageBox.information(self, "Sukces", "Część dodana do zlecenia.")
            self.load_available_parts()
            self.load_used_parts()
        else:
            QMessageBox.critical(self, "Błąd", str(response))

    def delete_used_part(self):
        row = self.parts_table.currentRow()
        if row < 0:
            return
        item_id = int(self.parts_table.item(row, 0).text())
        if (
            QMessageBox.question(
                self, "Potwierdź", "Usunąć część ze zlecenia? Ilość wróci do magazynu."
            )
            == QMessageBox.StandardButton.Yes
        ):
            success, msg = api.delete_order_used_part(
                self.order_data["id_zlecenia"], item_id
            )
            if success:
                self.load_available_parts()
                self.load_used_parts()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def handle_status_change(self):
        status_txt = self.status_combo.currentText()
        status_id = DictionaryCache.statuses.get(status_txt)
        is_finished = status_id in [5, 6]

        if self.user_role != "pracownik":
            self.has_end_date.setEnabled(is_finished)
            self.data_zak.setEnabled(is_finished)
            if not is_finished:
                self.has_end_date.setCurrentIndex(0)

    def get_data(self):
        selected_worker_txt = self.worker_combo.currentText()
        selected_worker_id = self.workers_map.get(selected_worker_txt)
        data = {
            "status_zlecenia": DictionaryCache.statuses.get(
                self.status_combo.currentText()
            ),
            "opis_usterki": self.opis_edit.toPlainText(),
            "marka_sprzetu": self.marka_edit.text(),
            "model_sprzetu": self.model_edit.text(),
            "numer_seryjny": self.sn_edit.text(),
            "diagnoza": self.diagnoza_edit.toPlainText(),
            "wykonane_czynnosci": self.czynnosci_edit.toPlainText(),
            "koszt_robocizny": self.koszt_robocizny.value(),
        }
        if self.user_role in ["administrator", "manager"] and selected_worker_id:
            data["id_pracownika"] = selected_worker_id

        if self.user_role != "pracownik":
            data["koszt_czesci"] = self.koszt_czesci.value()
            data["data_rozpoczecia"] = self.data_rozp.date().toString("yyyy-MM-dd")
            status_id = data["status_zlecenia"]
            if status_id in [5, 6] and self.has_end_date.currentIndex() == 1:
                data["data_zakonczenia"] = self.data_zak.date().toString("yyyy-MM-dd")
            else:
                data["data_zakonczenia"] = None
        return data


class CloseOrderDialog(QDialog):
    def __init__(self, order_data, parent=None, view_only=False):
        super().__init__(parent)
        self.order_data = order_data
        self.view_only = view_only
        self.user_role = api.user_data.get("rola", "").lower()

        if self.view_only:
            self.setWindowTitle(f"Raport Zlecenia #{order_data['id_zlecenia']}")
        else:
            self.setWindowTitle(f"Zamknij Zlecenie #{order_data['id_zlecenia']}")

        self.resize(700, 800)

        self.users = api.get_users() or []
        self.used_parts = api.get_order_used_parts(order_data["id_zlecenia"]) or []
        self.all_parts = api.get_parts() or []
        self.parts_map = {p["id_czesci"]: p["nazwa_czesci"] for p in self.all_parts}

        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.form_layout = QFormLayout(content_widget)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Info
        info_group = QGroupBox("Informacje podstawowe")
        info_layout = QFormLayout()

        self.client_name = order_data.get("klient_imie_nazwisko", "")
        info_layout.addRow("Klient:", QLabel(self.client_name))

        worker_id = order_data.get("id_pracownika")
        self.worker_name = "Nie przypisano"
        for u in self.users:
            if u["id_uzytkownika"] == worker_id:
                self.worker_name = f"{u['imie']} {u['nazwisko']}"
                break
        info_layout.addRow("Pracownik:", QLabel(self.worker_name))

        def format_date_only(date_str):
            if not date_str:
                return ""
            return str(date_str)[:10]

        self.start_date_str = format_date_only(order_data.get("data_rozpoczecia"))
        info_layout.addRow("Data rozpoczęcia:", QLabel(self.start_date_str))

        if self.view_only:
            end_d = order_data.get("data_zakonczenia")
            self.end_date_str = format_date_only(end_d) if end_d else "W toku"
            if self.end_date_str != "W toku":
                d = QDate.fromString(self.end_date_str, "yyyy-MM-dd")
                self.end_date = d if d.isValid() else QDate.currentDate()
            else:
                self.end_date = QDate.currentDate()
        else:
            self.end_date = QDate.currentDate()
            self.end_date_str = self.end_date.toString("yyyy-MM-dd")

        info_layout.addRow("Data zakończenia:", QLabel(self.end_date_str))

        info_group.setLayout(info_layout)
        self.form_layout.addRow(info_group)

        # Sprzet
        dev_group = QGroupBox("Sprzęt")
        dev_layout = QFormLayout()
        dev_layout.addRow("Marka:", QLabel(order_data.get("marka_sprzetu", "")))
        dev_layout.addRow("Model:", QLabel(order_data.get("model_sprzetu", "")))
        dev_layout.addRow("Nr Seryjny:", QLabel(order_data.get("numer_seryjny", "")))
        dev_group.setLayout(dev_layout)
        self.form_layout.addRow(dev_group)

        # Szczegoly
        details_group = QGroupBox("Szczegóły naprawy")
        details_layout = QFormLayout()

        self.opis_edit = QTextEdit(order_data.get("opis_usterki") or "")
        details_layout.addRow("Opis usterki:", self.opis_edit)

        self.diagnoza_edit = QTextEdit(order_data.get("diagnoza") or "")
        details_layout.addRow("Diagnoza:", self.diagnoza_edit)

        self.czynnosci_edit = QTextEdit(order_data.get("wykonane_czynnosci") or "")
        details_layout.addRow("Wykonane czynności:", self.czynnosci_edit)

        details_group.setLayout(details_layout)
        self.form_layout.addRow(details_group)

        # Czesci
        parts_group = QGroupBox("Wykorzystane części")
        parts_layout = QVBoxLayout()
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(4)
        self.parts_table.setHorizontalHeaderLabels(
            ["Nazwa", "Ilość", "Cena jedn.", "Suma"]
        )
        self.parts_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.parts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.parts_table.setRowCount(len(self.used_parts))

        self.total_parts_cost = 0.0
        for i, up in enumerate(self.used_parts):
            qty = up["ilosc"]
            price = float(up["cena_jednostkowa"])
            row_sum = qty * price
            self.total_parts_cost += row_sum

            p_name = self.parts_map.get(up["id_czesci"], str(up["id_czesci"]))

            self.parts_table.setItem(i, 0, QTableWidgetItem(p_name))
            self.parts_table.setItem(i, 1, QTableWidgetItem(str(qty)))
            self.parts_table.setItem(i, 2, QTableWidgetItem(f"{price:.2f}"))
            self.parts_table.setItem(i, 3, QTableWidgetItem(f"{row_sum:.2f}"))

        parts_layout.addWidget(self.parts_table)

        cost_layout = QHBoxLayout()
        cost_layout.addWidget(QLabel("Sumaryczny koszt części:"))
        self.parts_cost_display = QLineEdit(f"{self.total_parts_cost:.2f} PLN")
        self.parts_cost_display.setReadOnly(True)
        cost_layout.addWidget(self.parts_cost_display)
        parts_layout.addLayout(cost_layout)

        parts_group.setLayout(parts_layout)
        self.form_layout.addRow(parts_group)

        # Robocizna
        labor_group = QGroupBox("Robocizna")
        labor_layout = QFormLayout()

        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0, 999)
        self.hours_spin.setDecimals(1)
        self.hours_spin.setSuffix(" h")

        current_labor = float(order_data.get("koszt_robocizny") or 0)
        self.hours_spin.setValue(current_labor / 35.0)
        self.hours_spin.valueChanged.connect(self.update_labor_cost)
        labor_layout.addRow("Ilość godzin pracy:", self.hours_spin)

        self.labor_cost_display = QLineEdit(f"{current_labor:.2f}")
        self.labor_cost_display.setReadOnly(True)

        l_layout = QHBoxLayout()
        l_layout.addWidget(self.labor_cost_display)
        l_layout.addWidget(QLabel("PLN (stawka 35 PLN/h)"))
        labor_layout.addRow("Koszt robocizny:", l_layout)

        labor_group.setLayout(labor_layout)
        self.form_layout.addRow(labor_group)

        if self.view_only:
            self.toggle_inputs(False)
            if self.user_role == "administrator":
                self.edit_mode_cb = QCheckBox("Włącz edycję raportu (Administrator)")
                self.edit_mode_cb.stateChanged.connect(self.on_edit_mode_toggled)
                self.form_layout.addRow(self.edit_mode_cb)

        # Przyciski
        btn_box = QHBoxLayout()

        if not self.view_only:
            self.close_btn = QPushButton("Zamknij Zlecenie")
            self.close_btn.setStyleSheet(
                "background-color: #006600; color: white; font-weight: bold; padding: 10px;"
            )
            self.close_btn.clicked.connect(self.accept)
            btn_box.addWidget(self.close_btn)
        else:
            self.save_correction_btn = QPushButton("Zapisz korektę")
            self.save_correction_btn.setStyleSheet(
                "background-color: #d35400; color: white; font-weight: bold; padding: 10px;"
            )
            self.save_correction_btn.clicked.connect(self.save_correction)
            self.save_correction_btn.hide()
            btn_box.addWidget(self.save_correction_btn)

        self.pdf_btn = QPushButton("Pobierz Raport PDF")
        self.pdf_btn.setStyleSheet(
            "background-color: #AA0000; color: white; padding: 10px;"
        )
        self.pdf_btn.clicked.connect(self.generate_pdf)

        cancel_label = "Zamknij" if self.view_only else "Anuluj"
        self.cancel_btn = QPushButton(cancel_label)
        self.cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(self.pdf_btn)
        btn_box.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_box)

    def toggle_inputs(self, enabled):
        self.opis_edit.setReadOnly(not enabled)
        self.diagnoza_edit.setReadOnly(not enabled)
        self.czynnosci_edit.setReadOnly(not enabled)
        self.hours_spin.setEnabled(enabled)

    def on_edit_mode_toggled(self, state):
        is_enabled = state == 2
        self.toggle_inputs(is_enabled)
        if is_enabled:
            self.save_correction_btn.show()
        else:
            self.save_correction_btn.hide()

    def update_labor_cost(self):
        hours = self.hours_spin.value()
        cost = hours * 35.0
        self.labor_cost_display.setText(f"{cost:.2f}")

    def generate_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz Raport PDF",
            f"Raport_Zlecenie_{self.order_data['id_zlecenia']}.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        try:
            font_normal = "Helvetica"
            font_bold = "Helvetica-Bold"
            try:
                pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
                pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))
                font_normal = "Arial"
                font_bold = "Arial-Bold"
            except Exception:
                pass

            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4
            y = height - 50

            c.setFont(font_bold, 16)
            c.drawString(
                50, y, f"Raport Zamkniecia Zlecenia #{self.order_data['id_zlecenia']}"
            )
            y -= 30

            c.setFont(font_normal, 12)
            c.drawString(50, y, f"Klient: {self.client_name}")
            y -= 20
            c.drawString(50, y, f"Pracownik: {self.worker_name}")
            y -= 20
            c.drawString(50, y, f"Data rozp: {self.start_date_str}")
            y -= 20
            c.drawString(50, y, f"Data zak: {self.end_date_str}")
            y -= 30

            c.setFont(font_bold, 12)
            c.drawString(50, y, "Sprzet:")
            c.setFont(font_normal, 12)
            y -= 20
            c.drawString(60, y, f"Marka: {self.order_data.get('marka_sprzetu', '-')}")
            y -= 20
            c.drawString(60, y, f"Model: {self.order_data.get('model_sprzetu', '-')}")
            y -= 20
            c.drawString(60, y, f"SN: {self.order_data.get('numer_seryjny', '-')}")
            y -= 30

            c.setFont(font_bold, 12)
            c.drawString(50, y, "Opis i Diagnoza:")
            y -= 20
            c.setFont(font_normal, 10)

            c.drawString(60, y, "Opis:")
            y -= 15
            opis_text = self.opis_edit.toPlainText().replace("\n", " ")
            opis_lines = textwrap.wrap(opis_text, width=100)
            for line in opis_lines:
                c.drawString(70, y, line)
                y -= 12
            y -= 10

            c.drawString(60, y, "Diagnoza:")
            y -= 15
            diag_text = self.diagnoza_edit.toPlainText().replace("\n", " ")
            diag_lines = textwrap.wrap(diag_text, width=100)
            for line in diag_lines:
                c.drawString(70, y, line)
                y -= 12
            y -= 20

            c.setFont(font_bold, 12)
            c.drawString(50, y, "Koszty:")
            y -= 20
            c.setFont(font_normal, 12)
            labor_cost = float(self.labor_cost_display.text())
            c.drawString(60, y, f"Robocizna: {labor_cost:.2f} PLN")
            y -= 20
            c.drawString(60, y, f"Czesci: {self.total_parts_cost:.2f} PLN")
            y -= 20
            c.setFont(font_bold, 12)
            c.drawString(60, y, f"RAZEM: {labor_cost + self.total_parts_cost:.2f} PLN")

            c.save()
            QMessageBox.information(self, "Sukces", "Raport PDF wygenerowany.")
        except Exception as e:
            QMessageBox.critical(
                self, "Błąd", f"Nie udało się wygenerować PDF:\n{str(e)}"
            )

    def get_data(self):
        data = {
            "opis_usterki": self.opis_edit.toPlainText(),
            "diagnoza": self.diagnoza_edit.toPlainText(),
            "wykonane_czynnosci": self.czynnosci_edit.toPlainText(),
            "koszt_robocizny": float(self.labor_cost_display.text()),
            "data_zakonczenia": self.end_date.toString("yyyy-MM-dd"),
        }

        if not self.view_only:
            data["status_zlecenia"] = 4

        return data

    def save_correction(self):
        if (
            QMessageBox.question(
                self, "Potwierdź", "Czy na pewno chcesz nadpisać dane w raporcie?"
            )
            == QMessageBox.StandardButton.Yes
        ):
            data = self.get_data()
            success, msg = api.update_order_details(
                self.order_data["id_zlecenia"], data
            )
            if success:
                QMessageBox.information(self, "Sukces", "Dane raportu zaktualizowane.")
                self.accept()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))


class OrdersPanel(QWidget):
    def __init__(self):
        super().__init__()
        DictionaryCache.load()

        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Zmniejszono z 5 na 4
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Sledzenie myszy dla efektu hover
        self.table.setMouseTracking(True)
        self.hover_delegate = RowHoverDelegate(self.table)
        self.table.setItemDelegate(self.hover_delegate)
        self.table.viewport().installEventFilter(self)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        self.layout.addWidget(self.table)
        self.table.doubleClicked.connect(self.open_details)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Odśwież")
        self.add_btn = QPushButton("Nowe Zlecenie")
        self.details_btn = QPushButton("Szczegóły / Edycja")

        self.close_order_btn = QPushButton("Zamknij Zlecenie")
        self.close_order_btn.setStyleSheet("background-color: #004488; color: white;")

        self.recreate_report_btn = QPushButton("Odtwórz Raport")
        self.recreate_report_btn.setStyleSheet(
            "background-color: #555555; color: white;"
        )
        self.recreate_report_btn.setEnabled(False)

        self.refresh_btn.clicked.connect(self.load_data)
        self.add_btn.clicked.connect(self.add_order)
        self.details_btn.clicked.connect(self.open_details)
        self.close_order_btn.clicked.connect(self.open_close_order_dialog)
        self.recreate_report_btn.clicked.connect(self.open_recreate_report_dialog)

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.details_btn)
        btn_layout.addWidget(self.close_order_btn)
        btn_layout.addWidget(self.recreate_report_btn)

        self.user_role = api.user_data.get("rola", "").lower()
        if self.user_role == "administrator":
            self.archive_btn = QPushButton("Archiwizuj Zlecenie")
            self.archive_btn.setStyleSheet("background-color: #660000; color: white;")
            self.archive_btn.clicked.connect(self.archive_order)
            btn_layout.addWidget(self.archive_btn)
        else:
            self.archive_btn = None

        self.layout.addLayout(btn_layout)
        self.orders_data_cache = []

        self.set_language("PL")
        self.load_data()

    # Obsluga eventu myszy dla hover
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
            headers = ["Client", "Equipment Type", "Description", "Status"]  # Bez ID
            self.refresh_btn.setText("Refresh")
            self.add_btn.setText("New Order")
            self.details_btn.setText("Details / Edit")
            self.close_order_btn.setText("Close Order")
            self.recreate_report_btn.setText("Recreate Report")
            if self.archive_btn:
                self.archive_btn.setText("Archive Order")
        else:
            headers = ["Klient", "Typ Sprzętu", "Opis Usterki", "Status"]  # Bez ID
            self.refresh_btn.setText("Odśwież")
            self.add_btn.setText("Nowe Zlecenie")
            self.details_btn.setText("Szczegóły / Edycja")
            self.close_order_btn.setText("Zamknij Zlecenie")
            self.recreate_report_btn.setText("Odtwórz Raport")
            if self.archive_btn:
                self.archive_btn.setText("Archiwizuj Zlecenie")

        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self):
        self.orders_data_cache = api.get_orders()
        self.table.setRowCount(len(self.orders_data_cache))
        for i, o in enumerate(self.orders_data_cache):
            status_id = o.get("status_zlecenia")
            status_txt = DictionaryCache.statuses_rev.get(status_id, str(status_id))

            typ_id = o.get("typ_sprzetu")
            typ_txt = str(typ_id)
            for name, tid in DictionaryCache.types.items():
                if tid == typ_id:
                    typ_txt = name
                    break

            item_client = QTableWidgetItem(o.get("klient_imie_nazwisko", ""))
            item_type = QTableWidgetItem(typ_txt)
            item_desc = QTableWidgetItem(o.get("opis_usterki", ""))
            item_status = QTableWidgetItem(status_txt)

            # Kolorowanie Czcionki w Statusie Zlecenia
            text_color = None
            if status_id == 1:  # Przyjęte -> Czerwona
                text_color = QColor("red")
            elif status_id == 3:  # Oczekuje na czesci -> Zolta
                text_color = QColor("darkgoldenrod")
            elif status_id == 4:  # Gotowe -> Zielona
                text_color = QColor("green")
            elif status_id == 6:  # Zarchiwizowane -> Szara
                text_color = QColor("gray")
            # 2 = W naprawie, 5 = Zakonczone -> Domyslny kolor

            # Kolor tylko do statusu
            if text_color:
                item_status.setForeground(text_color)

            row_items = [item_client, item_type, item_desc, item_status]

            # Przesuniecie indeksow (bez ID)
            self.table.setItem(i, 0, item_client)
            self.table.setItem(i, 1, item_type)
            self.table.setItem(i, 2, item_desc)
            self.table.setItem(i, 3, item_status)

    def on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0:
            self.recreate_report_btn.setEnabled(False)
            return

        order_data = self.orders_data_cache[row]
        status_id = order_data.get("status_zlecenia")
        user_role = api.user_data.get("rola", "").lower()

        is_finished = status_id in [4, 5, 6]
        is_privileged = user_role in ["administrator", "manager"]

        if is_finished and is_privileged:
            self.recreate_report_btn.setEnabled(True)
        else:
            self.recreate_report_btn.setEnabled(False)

    def add_order(self):
        dialog = OrderDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["id_klienta"]:
                QMessageBox.warning(self, "Błąd", "Nie wybrano klienta!")
                return
            success, msg = api.create_order(data)
            if success:
                QMessageBox.information(self, "Sukces", "Utworzono zlecenie")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def open_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz zlecenie z listy")
            return
        order_data = self.orders_data_cache[row]
        dialog = OrderDetailsDialog(order_data, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            success, msg = api.update_order_details(
                order_data["id_zlecenia"], updated_data
            )
            if success:
                QMessageBox.information(self, "Sukces", "Zaktualizowano zlecenie")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def open_close_order_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz zlecenie do zamknięcia")
            return

        order_data = self.orders_data_cache[row]
        if order_data.get("status_zlecenia") in [4, 5, 6]:
            QMessageBox.warning(
                self, "Info", "To zlecenie jest już gotowe lub zakończone."
            )
            return

        dialog = CloseOrderDialog(order_data, self, view_only=False)
        if dialog.exec():
            close_data = dialog.get_data()
            success, msg = api.update_order_details(
                order_data["id_zlecenia"], close_data
            )
            if success:
                QMessageBox.information(
                    self, "Sukces", "Zlecenie zostało zamknięte (status: Gotowe)"
                )
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def open_recreate_report_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            return
        order_data = self.orders_data_cache[row]

        dialog = CloseOrderDialog(order_data, self, view_only=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def archive_order(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz zlecenie do archiwizacji")
            return
        order_id = self.orders_data_cache[row]["id_zlecenia"]
        confirm = QMessageBox.question(
            self,
            "Potwierdzenie",
            f"Zarchiwizować zlecenie #{order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            arch_id = DictionaryCache.statuses.get("Zarchiwizowane", 6)
            success, msg = api.update_order_status(order_id, arch_id)
            if success:
                QMessageBox.information(self, "Sukces", "Zlecenie zarchiwizowane")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))
