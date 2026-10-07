import sys
import os

# Lấy đường dẫn của thư mục gốc (thư mục chứa cả 'windows' và 'ui_py')
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
import sqlite3
from datetime import datetime, timedelta
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from ui_py.ui_home_page import Ui_Form
from database.db_helper import get_user_vocabulary, add_word_to_notebook


class CustomFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = ""

    def setSearchText(self, text):
        self.search_text = text.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        word_index = model.index(source_row, 1, source_parent)  # "Từ mới"
        explanation_index = model.index(source_row, 3, source_parent)  # "Giải thích"
        word = model.data(word_index)
        explanation = model.data(explanation_index)
        return self.search_text in str(word).lower() or self.search_text in str(explanation).lower()


class HomePage(QWidget):
    def __init__(self, parent=None, user_id=None, notebook_page=None):
        super().__init__(parent)
        self.user_id = user_id
        self.notebook_page = notebook_page
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.result.setStyleSheet("QTableView { font-size: 10pt; }")

        # Kết nối các nút
        self.ui.search_button.clicked.connect(self.filter_words)
        self.ui.search.textChanged.connect(self.filter_words)
        self.ui.add_to_notebook.clicked.connect(self.add_word_to_notebook)

        self.ui.result.setSelectionBehavior(self.ui.result.SelectionBehavior.SelectRows)

        self.proxy_model = CustomFilterProxyModel(self)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.load_user_vocabulary()
        self.load_random_meo()
        self.update_streak()
        self.highlight_today()

    def load_user_vocabulary(self):
        data = get_user_vocabulary(self.user_id)
        if data.empty:
            print("Không có từ vựng cho người dùng.")
            return

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "Cấp độ", "Từ mới", "Phiên âm", "Giải thích", "Ví dụ (chữ hán)", "Phiên âm ví dụ", "Dịch"
        ])

        for _, row in data.iterrows():
            items = [
                QStandardItem(f"HSK{row['cap_do']}"),
                QStandardItem(str(row["tu_moi"])),
                QStandardItem(str(row["phien_am"])),
                QStandardItem(str(row["giai_thich"])),
                QStandardItem(str(row["vi_du"])),
                QStandardItem(str(row["phien_am_vi_du"])),
                QStandardItem(str(row["dich"])),
            ]
            model.appendRow(items)

        self.proxy_model.setSourceModel(model)
        self.ui.result.setModel(self.proxy_model)

        header = self.ui.result.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)  # HSK level
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)  # Từ mới
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)  # Phiên âm
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.ui.result.resizeRowsToContents()


    def filter_words(self, text=""):
        self.proxy_model.setSearchText(text)

    def add_word_to_notebook(self):
        selected_row = self.ui.result.selectionModel().currentIndex().row()
        if selected_row == -1:
            print("Chưa chọn từ vựng để thêm.")
            return

        model = self.ui.result.model()
        index_map = lambda col: model.index(selected_row, col)
        level = model.data(index_map(0))
        word = model.data(index_map(1))
        pinyin = model.data(index_map(2))
        explanation = model.data(index_map(3))
        example = model.data(index_map(4))
        example_pinyin = model.data(index_map(5))
        translation = model.data(index_map(6))

        add_word_to_notebook(
            self.user_id, level, word, pinyin, explanation, example, example_pinyin, translation
        )
        print(f"Đã thêm từ: {word} vào sổ tay.")

        if self.notebook_page:
            self.notebook_page.update_notebook()

    def load_random_meo(self):
        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT noi_dung FROM MeoHoc ORDER BY RANDOM() LIMIT 1")
            tip = cursor.fetchone()
            if tip:
                self.ui.tips.setText(tip[0])
            else:
                self.ui.tips.setText("Không có mẹo học nào.")
        except sqlite3.Error as e:
            print(f"Lỗi SQL khi lấy mẹo học: {e}")
            self.ui.tips.setText("Lỗi khi tải mẹo học.")
        except AttributeError:
            print("'tips' không tồn tại trong Ui_Form.")
        finally:
            conn.close()

    def update_streak(self):
        if not self.user_id:
            self.ui.streak.setText("0")
            return

        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT thoi_gian_dang_nhap FROM PhienDangNhap
                WHERE ma_nguoi_dung = ?
                ORDER BY thoi_gian_dang_nhap DESC
            """, (self.user_id,))
            rows = cursor.fetchall()

            if not rows:
                self.ui.streak.setText("0")
                return

            dates = sorted(set(self.convert_str_to_date(row[0]) for row in rows), reverse=True)
            streak = 0
            today = datetime.today().date()

            for i in range(len(dates)):
                expected_day = today - timedelta(days=i)
                if expected_day in dates:
                    streak += 1
                else:
                    break

            self.ui.streak.setText(f"{streak} ngày")

        except sqlite3.Error as e:
            print(f"Lỗi khi tính chuỗi học: {e}")
        finally:
            conn.close()

    def convert_str_to_date(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f").date()
        except ValueError:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").date()

    def highlight_today(self):
        try:
            weekday_index = datetime.today().weekday()  # 0 = Monday
            buttons = [
                self.ui.mon, self.ui.tues, self.ui.wednes,
                self.ui.thurs, self.ui.fri, self.ui.satur, self.ui.sun
            ]

            if 0 <= weekday_index < len(buttons):
                today_button = buttons[weekday_index]
                today_button.setStyleSheet("""
                    background-color: #F1C40F;
                    color: black;
                    font-weight: bold;
                    border: 2px solid #F39C12;
                """)
        except Exception as e:
            print(f"Lỗi khi highlight nút ngày hôm nay: {e}")
