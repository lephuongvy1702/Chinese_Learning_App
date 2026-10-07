import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt6.QtWidgets import QWidget, QStyledItemDelegate
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from ui_py.ui_notebook_page import Ui_NotebookPage
from database.db_helper import get_notebook_words, get_current_user_level, delete_word_in_so_tay

class DisabledItemDelegate(QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        item = model.itemFromIndex(index)
        if item and not item.isEnabled():
            return False
        return super().editorEvent(event, model, option, index)

class NotebookPage(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.ui = Ui_NotebookPage()
        self.ui.setupUi(self)
        self.user_id = user_id

        self.setup_level_box()
        self.refresh_level_lock()
        self.setup_table()
        self.update_notebook()

        self.ui.level_box.currentTextChanged.connect(self.on_level_change)
        self.ui.level_search.textChanged.connect(self.filter_words)
        self.ui.level_search_button.clicked.connect(self.filter_words)
        self.ui.delete_word_button.clicked.connect(self.delete_word)

    def delete_word(self):
        word = self.get_selected_word()
        if word:
            delete_word_in_so_tay(self.user_id, word)
            self.filter_words()

    def get_selected_word(self):
        selected_index = self.ui.tableView.selectionModel().selectedIndexes()
        if selected_index:
            row = selected_index[0].row()
            word_item = self.ui.tableView.model().item(row, 0)
            return word_item.text()
        return None

    def setup_level_box(self):
        self.levels = ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"]
        model = QStandardItemModel()

        for level in self.levels:
            item = QStandardItem(level)
            item.setEnabled(True)
            model.appendRow(item)

        self.ui.level_box.setModel(model)
        self.ui.level_box.setItemDelegate(DisabledItemDelegate(self.ui.level_box))

    def refresh_level_lock(self):
        try:
            self.current_level = get_current_user_level(self.user_id)
            self.ui.level_box.setCurrentText(self.current_level)
            self.lock_higher_levels()
        except Exception as e:
            print(f"Error in refresh_level_lock: {e}")

    def lock_higher_levels(self):
        max_index = self.levels.index(self.current_level)
        model = self.ui.level_box.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            item.setEnabled(i <= max_index)

    def setup_table(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([
            "Từ mới",
            "Phiên âm",
            "Giải thích",
            "Ví dụ (chữ hán)",
            "Phiên âm ví dụ",
            "Dịch",
            "Đã học"
        ])
        self.ui.tableView.setModel(self.model)

        # Làm các cột tự co giãn đầy chiều ngang
        header = self.ui.tableView.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    # (Tùy chọn) Làm cho chiều cao hàng tự điều chỉnh theo nội dung
        self.ui.tableView.resizeRowsToContents()

    # (Tùy chọn) Tăng cỡ chữ cho bảng
        self.ui.tableView.setStyleSheet("QTableView { font-size: 10pt; }")

    def on_level_change(self):
        self.ui.level_search.setText("")  # Reset tìm kiếm về rỗng
        self.update_notebook()

    def update_notebook(self):
        """Tải lại toàn bộ bảng dựa trên cấp độ hiện tại và ô tìm kiếm (rỗng khi mới đổi cấp độ)"""
        selected_level = self.ui.level_box.currentText()
        data = get_notebook_words(self.user_id)
        data = data[data['cap_do'] == selected_level]
        self.populate_table(data)

    def filter_words(self):
        selected_level = self.ui.level_box.currentText()
        keyword = self.ui.level_search.text().strip().lower()

        data = get_notebook_words(self.user_id)
        data = data[data['cap_do'] == selected_level]

        if keyword:
            data = data[
                data["tu_moi"].str.contains(keyword, case=False, na=False) |
                data["giai_thich"].str.contains(keyword, case=False, na=False)
            ]

        self.populate_table(data)

    def populate_table(self, data):
        self.model.removeRows(0, self.model.rowCount())
        for _, row in data.iterrows():
            items = [
                QStandardItem(row["tu_moi"]),
                QStandardItem(row["phien_am"]),
                QStandardItem(row["giai_thich"]),
                QStandardItem(row["vi_du"]),
                QStandardItem(row["phien_am_vi_du"]),
                QStandardItem(row["dich"])
            ]

            # Tạo checkbox không cho tương tác (cột "Đã học")
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.CheckState.Checked if row.get("da_hoc") else Qt.CheckState.Unchecked)
            checkbox_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Không thể click

            items.append(checkbox_item)
            self.model.appendRow(items)

        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.resizeRowsToContents()

    def update_notebook_checkbox(self, user_id, word_id):
        """Cập nhật lại trạng thái checkbox 'Đã học' cho từ vựng trong bảng"""
        print(f"Updating checkbox for user {user_id}, word_id: {word_id}")
        for row in range(self.model.rowCount()):
            word_item = self.model.item(row, 0)
            print(f"Checking row {row}: word_item.text() = {word_item.text()}")
            if word_item.text() == word_id:
                checkbox_item = self.model.item(row, 6)
                checkbox_item.setCheckState(Qt.CheckState.Checked)
                print(f"Updated checkbox for word: {word_id}")
                break
        else:
            print(f"Word {word_id} not found in table")

