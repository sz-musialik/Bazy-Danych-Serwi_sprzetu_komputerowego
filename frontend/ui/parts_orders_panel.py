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
    QDoubleSpinBox,
    QSpinBox,
    QHeaderView,
    QComboBox,
    QInputDialog,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
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


class OrderContextCache:
    part_types = {}
    part_types_rev = {}
    existing_parts = []

    @classmethod
    def load(cls):
        cls.part_types = api.get_part_types() or {}
        cls.part_types_rev = {v: k for k, v in cls.part_types.items()}
        cls.existing_parts = api.get_parts() or []


class PartOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Złóż zamówienie na część")
        self.resize(450, 450)
        layout = QFormLayout(self)

        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.setPlaceholderText("Wybierz lub wpisz nową nazwę...")
        for p in OrderContextCache.existing_parts:
            self.name_combo.addItem(p["nazwa_czesci"])
        self.name_combo.currentIndexChanged.connect(self.on_part_selected)
        layout.addRow("Nazwa części:", self.name_combo)

        self.typ_combo = QComboBox()
        self.typ_combo.addItems(OrderContextCache.part_types.keys())
        layout.addRow("Typ części:", self.typ_combo)

        self.producent_edit = QLineEdit()
        layout.addRow("Producent:", self.producent_edit)

        self.nr_kat_edit = QLineEdit()
        layout.addRow("Numer katalogowy:", self.nr_kat_edit)

        self.cena_spin = QDoubleSpinBox()
        self.cena_spin.setMaximum(99999.99)
        self.cena_spin.setSuffix(" PLN")
        layout.addRow("Cena katalogowa:", self.cena_spin)

        self.ilosc_spin = QSpinBox()
        self.ilosc_spin.setRange(1, 9999)
        self.ilosc_spin.setValue(1)
        layout.addRow("Ilość:", self.ilosc_spin)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Zamów")
        cancel_btn = QPushButton("Anuluj")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def on_part_selected(self, index):
        if index < 0:
            return
        selected_name = self.name_combo.currentText()
        part_data = next(
            (
                p
                for p in OrderContextCache.existing_parts
                if p["nazwa_czesci"] == selected_name
            ),
            None,
        )
        if part_data:
            type_id = part_data.get("typ_czesci")
            self.typ_combo.setCurrentText(
                OrderContextCache.part_types_rev.get(type_id, "")
            )
            self.producent_edit.setText(part_data.get("producent", ""))
            self.nr_kat_edit.setText(part_data.get("numer_katalogowy", ""))
            try:
                self.cena_spin.setValue(float(part_data.get("cena_katalogowa", 0)))
            except:
                self.cena_spin.setValue(0.0)

    def get_data(self):
        return {
            "nazwa_czesci": self.name_combo.currentText(),
            "typ_czesci": OrderContextCache.part_types.get(
                self.typ_combo.currentText()
            ),
            "producent": self.producent_edit.text(),
            "numer_katalogowy": self.nr_kat_edit.text(),
            "cena_katalogowa": self.cena_spin.value(),
            "ilosc": self.ilosc_spin.value(),
        }


class PartsOrdersPanel(QWidget):
    def __init__(self):
        super().__init__()
        OrderContextCache.load()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.table.setMouseTracking(True)
        self.hover_delegate = RowHoverDelegate(self.table)
        self.table.setItemDelegate(self.hover_delegate)
        self.table.viewport().installEventFilter(self)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        self.layout.addWidget(self.table)

        # Przyciski
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Odśwież")
        self.add_btn = QPushButton("Złóż zamówienie")
        self.refresh_btn.clicked.connect(self.load_data)
        self.add_btn.clicked.connect(self.create_order)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.add_btn)

        self.user_role = api.user_data.get("rola", "").lower()
        self.approve_btn = None
        self.reject_btn = None
        self.edit_status_btn = None

        if self.user_role in ["administrator", "manager"]:
            self.approve_btn = QPushButton("Zatwierdź")
            self.approve_btn.setStyleSheet("background-color: #006600; color: white;")
            self.approve_btn.clicked.connect(self.approve_order)
            self.approve_btn.setEnabled(False)
            btn_layout.addWidget(self.approve_btn)

            self.reject_btn = QPushButton("Odrzuć")
            self.reject_btn.setStyleSheet("background-color: #660000; color: white;")
            self.reject_btn.clicked.connect(self.reject_order)
            self.reject_btn.setEnabled(False)
            btn_layout.addWidget(self.reject_btn)

        if self.user_role == "administrator":
            self.edit_status_btn = QPushButton("Edytuj status")
            self.edit_status_btn.clicked.connect(self.edit_status_dialog)
            btn_layout.addWidget(self.edit_status_btn)

        self.layout.addLayout(btn_layout)
        self.orders_cache = []

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
            headers = ["Part Name", "Type", "Quantity", "Status", "Ordered By", "Date"]
            self.refresh_btn.setText("Refresh")
            self.add_btn.setText("Place Order")
            if self.approve_btn:
                self.approve_btn.setText("Approve")
            if self.reject_btn:
                self.reject_btn.setText("Reject")
            if self.edit_status_btn:
                self.edit_status_btn.setText("Edit Status")
        else:
            headers = ["Nazwa Części", "Typ", "Ilość", "Status", "Zamawiający", "Data"]
            self.refresh_btn.setText("Odśwież")
            self.add_btn.setText("Złóż zamówienie")
            if self.approve_btn:
                self.approve_btn.setText("Zatwierdź")
            if self.reject_btn:
                self.reject_btn.setText("Odrzuć")
            if self.edit_status_btn:
                self.edit_status_btn.setText("Edytuj status")

        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self):
        user_id = None
        if self.user_role == "pracownik":
            user_id = api.user_data.get("id_uzytkownika")

        self.orders_cache = api.get_parts_orders(user_id=user_id)
        self.table.setRowCount(len(self.orders_cache))
        OrderContextCache.load()

        for i, o in enumerate(self.orders_cache):
            status_id = o.get("status_id")
            status_name = o.get("status_nazwa", "")

            status_item = QTableWidgetItem(status_name)
            if status_id == 1:
                status_item.setForeground(QColor("orange"))
            elif status_id == 2:
                status_item.setForeground(QColor("green"))
            elif status_id == 5:
                status_item.setForeground(QColor("blue"))
            elif status_id == 6 or "odrzucone" in status_name.lower():
                status_item.setForeground(QColor("red"))

            type_id = o.get("typ_czesci_id")
            type_name = OrderContextCache.part_types_rev.get(
                type_id, str(type_id) if type_id else ""
            )

            self.table.setItem(i, 0, QTableWidgetItem(o.get("nazwa_czesci")))
            self.table.setItem(i, 1, QTableWidgetItem(type_name))
            self.table.setItem(i, 2, QTableWidgetItem(str(o.get("ilosc"))))
            self.table.setItem(i, 3, status_item)
            self.table.setItem(i, 4, QTableWidgetItem(o.get("zamawiajacy")))
            self.table.setItem(i, 5, QTableWidgetItem(o.get("data_zamowienia")))

    def on_selection_changed(self):
        if not self.approve_btn and not self.reject_btn:
            return

        row = self.table.currentRow()
        should_enable = False

        if row >= 0:
            order = self.orders_cache[row]
            if order.get("status_id") == 1:
                should_enable = True

        if self.approve_btn:
            self.approve_btn.setEnabled(should_enable)
        if self.reject_btn:
            self.reject_btn.setEnabled(should_enable)

    def create_order(self):
        dialog = PartOrderDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["nazwa_czesci"] or not data["typ_czesci"]:
                QMessageBox.warning(self, "Błąd", "Nazwa i Typ są wymagane!")
                return
            user_id = api.user_data.get("id_uzytkownika")
            if not user_id:
                QMessageBox.critical(self, "Błąd", "Nie rozpoznano użytkownika.")
                return
            data["id_skladajacego"] = user_id

            success, msg = api.create_part_order(data)
            if success:
                QMessageBox.information(self, "Sukces", "Zamówienie złożone")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def approve_order(self):
        row = self.table.currentRow()
        if row < 0:
            return
        order = self.orders_cache[row]
        if order.get("status_id") != 1:
            QMessageBox.warning(
                self, "Info", "Możesz zatwierdzać tylko zamówienia 'Do zatwierdzenia'."
            )
            return
        if (
            QMessageBox.question(self, "Potwierdź", "Zatwierdzić?")
            == QMessageBox.StandardButton.Yes
        ):
            success, msg = api.approve_part_order(order["id_zamowienia"])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def reject_order(self):
        row = self.table.currentRow()
        if row < 0:
            return
        order = self.orders_cache[row]

        if order.get("status_id") != 1:
            QMessageBox.warning(
                self, "Info", "Możesz odrzucać tylko zamówienia 'Do zatwierdzenia'."
            )
            return

        if (
            QMessageBox.question(self, "Potwierdź", "Odrzucić zamówienie?")
            == QMessageBox.StandardButton.Yes
        ):
            success, msg = api.reject_part_order(order["id_zamowienia"])
            if success:
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def edit_status_dialog(self):
        row = self.table.currentRow()
        if row < 0:
            return
        order = self.orders_cache[row]

        statuses = [
            "Do zatwierdzenia",
            "Zatwierdzone",
            "W realizacji",
            "Dostarczone",
            "Odrzucone",
        ]
        current_status = order.get("status_nazwa", "")

        try:
            current_idx = statuses.index(current_status)
        except ValueError:
            current_idx = 0

        item, ok = QInputDialog.getItem(
            self, "Edytuj status", "Wybierz nowy status:", statuses, current_idx, False
        )

        if ok and item:
            success, msg = api.change_part_order_status(order["id_zamowienia"], item)
            if success:
                QMessageBox.information(self, "Sukces", "Status zmieniony")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))
