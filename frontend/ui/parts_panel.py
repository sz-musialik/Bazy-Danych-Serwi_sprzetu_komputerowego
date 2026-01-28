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


class PartDictionaryCache:
    types = {}
    types_rev = {}

    @classmethod
    def load(cls):
        cls.types = api.get_part_types() or {}
        cls.types_rev = {v: k for k, v in cls.types.items()}


class PartDetailsDialog(QDialog):
    def __init__(self, part_data=None, parent=None):
        super().__init__(parent)
        self.part_data = part_data or {}
        is_edit = bool(part_data)
        self.user_role = api.user_data.get("rola", "").lower()
        self.is_read_only = self.user_role != "administrator"

        self.setWindowTitle("Szczegóły Części" if is_edit else "Nowa Część")
        self.resize(400, 400)

        layout = QFormLayout(self)

        self.nazwa_edit = QLineEdit(self.part_data.get("nazwa_czesci", ""))
        layout.addRow("Nazwa części:", self.nazwa_edit)

        self.typ_combo = QComboBox()
        self.typ_combo.addItems(PartDictionaryCache.types.keys())
        current_type_id = self.part_data.get("typ_czesci")
        if current_type_id:
            current_name = PartDictionaryCache.types_rev.get(current_type_id, "")
            self.typ_combo.setCurrentText(current_name)
        layout.addRow("Typ części:", self.typ_combo)

        self.producent_edit = QLineEdit(self.part_data.get("producent", ""))
        layout.addRow("Producent:", self.producent_edit)

        self.nr_kat_edit = QLineEdit(self.part_data.get("numer_katalogowy", ""))
        layout.addRow("Numer katalogowy:", self.nr_kat_edit)

        self.cena_spin = QDoubleSpinBox()
        self.cena_spin.setMaximum(99999.99)
        self.cena_spin.setValue(float(self.part_data.get("cena_katalogowa") or 0.0))
        self.cena_spin.setSuffix(" PLN")
        layout.addRow("Cena katalogowa:", self.cena_spin)

        self.ilosc_spin = QSpinBox()
        self.ilosc_spin.setMaximum(999999)
        self.ilosc_spin.setValue(int(self.part_data.get("ilosc_dostepna") or 0))
        layout.addRow("Ilość dostępna:", self.ilosc_spin)

        if self.is_read_only:
            self.nazwa_edit.setReadOnly(True)
            self.typ_combo.setEnabled(False)
            self.producent_edit.setReadOnly(True)
            self.nr_kat_edit.setReadOnly(True)
            self.cena_spin.setReadOnly(True)
            self.ilosc_spin.setReadOnly(True)
            self.setWindowTitle("Podgląd części")

        btn_box = QHBoxLayout()
        if not self.is_read_only:
            save_btn = QPushButton("Zapisz")
            save_btn.clicked.connect(self.accept)
            btn_box.addWidget(save_btn)

        cancel_btn = QPushButton("Zamknij" if self.is_read_only else "Anuluj")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

    def get_data(self):
        type_name = self.typ_combo.currentText()
        type_id = PartDictionaryCache.types.get(type_name)
        return {
            "nazwa_czesci": self.nazwa_edit.text(),
            "typ_czesci": type_id,
            "producent": self.producent_edit.text(),
            "numer_katalogowy": self.nr_kat_edit.text(),
            "cena_katalogowa": self.cena_spin.value(),
            "ilosc_dostepna": self.ilosc_spin.value(),
        }


class PartsPanel(QWidget):
    def __init__(self):
        super().__init__()
        PartDictionaryCache.load()

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
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
        self.details_btn = QPushButton("Szczegóły / Edycja")

        self.refresh_btn.clicked.connect(self.load_data)
        self.details_btn.clicked.connect(self.open_details)

        btn_layout.addWidget(self.refresh_btn)

        self.user_role = api.user_data.get("rola", "").lower()
        if self.user_role == "administrator":
            self.add_btn = QPushButton("Dodaj Część")
            self.add_btn.clicked.connect(self.add_part)
            btn_layout.addWidget(self.add_btn)
        else:
            self.add_btn = None

        btn_layout.addWidget(self.details_btn)
        self.layout.addLayout(btn_layout)

        self.parts_cache = []
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
            headers = ["Part Name", "Type", "Manufacturer", "Quantity"]
            self.refresh_btn.setText("Refresh")
            self.details_btn.setText("Details / Edit")
            if self.add_btn:
                self.add_btn.setText("Add Part")
        else:
            headers = ["Nazwa Części", "Typ", "Producent", "Ilość"]
            self.refresh_btn.setText("Odśwież")
            self.details_btn.setText("Szczegóły / Edycja")
            if self.add_btn:
                self.add_btn.setText("Dodaj Część")

        self.table.setHorizontalHeaderLabels(headers)

    def load_data(self):
        self.parts_cache = api.get_parts()
        self.table.setRowCount(len(self.parts_cache))

        for i, p in enumerate(self.parts_cache):
            qty = p.get("ilosc_dostepna", 0)
            qty_item = QTableWidgetItem(str(qty))
            if qty == 0:
                qty_item.setForeground(QColor("red"))
            elif qty < 5:
                qty_item.setForeground(QColor("orange"))
            else:
                qty_item.setForeground(QColor("green"))

            type_id = p.get("typ_czesci")
            type_name = PartDictionaryCache.types_rev.get(type_id, str(type_id))

            self.table.setItem(i, 0, QTableWidgetItem(p["nazwa_czesci"]))
            self.table.setItem(i, 1, QTableWidgetItem(type_name))
            self.table.setItem(i, 2, QTableWidgetItem(p.get("producent", "")))
            self.table.setItem(i, 3, qty_item)

    def add_part(self):
        dialog = PartDetailsDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["nazwa_czesci"] or not data["typ_czesci"]:
                QMessageBox.warning(self, "Błąd", "Nazwa i Typ są wymagane!")
                return
            success, msg = api.create_part(data)
            if success:
                QMessageBox.information(self, "Sukces", "Dodano część do magazynu")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))

    def open_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz część z listy")
            return
        part_data = self.parts_cache[row]
        dialog = PartDetailsDialog(part_data, self)
        if dialog.exec():
            new_data = dialog.get_data()
            success, msg = api.update_part(part_data["id_czesci"], new_data)
            if success:
                QMessageBox.information(self, "Sukces", "Zaktualizowano dane części")
                self.load_data()
            else:
                QMessageBox.critical(self, "Błąd", str(msg))
