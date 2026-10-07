# ui_py/ ui_notebook_page.py
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_NotebookPage(object):
    def __init__(self, user_id=None):
        self.user_id = user_id  # Lưu user_id để sử dụng sau này

    def setupUi(self, NotebookPage):
        self.ui = NotebookPage
        NotebookPage.setObjectName("NotebookPage")
        NotebookPage.resize(718, 485)
        NotebookPage.setStyleSheet("""
        QLineEdit {
            padding: 5px;
            font-size: 20px;
            border: 1px solid #5DADE2;
            border-radius: 6px;
        }
        QPushButton {
            background-color: #3498DB;
            color: white;
            padding: 5px 15px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2980B9;
        }
        QTableView {
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 8px;
            gridline-color: #ddd;
        }
        QHeaderView::section {
            background-color: #3498DB;
            color: white;
            padding: 4px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }
        QTableView QTableCornerButton::section {
            background-color: #f9f9f9;
        }
        QTableView::item {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        QTableView::item:selected {
            background-color: #3498DB;
            color: white;
        }
        QComboBox {
            background-color: #3498DB;
            color: white;
            border: 1px solid #3399cc;
            border-radius:6px;
            padding: 4px 8px;
            font-weight: bold;
        }
        QComboBox QAbstractItemView {
            background-color: #3498DB;
            color: white;
            selection-background-color: #99ccff;
            selection-color: #003344;
            border: 1px solid #3399cc;
            border-radius:6px;
        }
        """)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NotebookPage)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setSpacing(10)

        # Header chính
        self.header = QtWidgets.QWidget(parent=NotebookPage)
        self.header_layout = QtWidgets.QVBoxLayout(self.header)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(10)

        # Thanh tìm kiếm
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.level_box = QtWidgets.QComboBox()
        self.level_box.setMinimumSize(QtCore.QSize(70, 40))
        self.level_box.setMaximumSize(QtCore.QSize(70, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.level_box.setFont(font)
        self.horizontalLayout.addWidget(self.level_box)

        self.level_search = QtWidgets.QLineEdit()
        self.horizontalLayout.addWidget(self.level_search)

        self.level_search_button = QtWidgets.QPushButton()
        self.level_search_button.setMinimumSize(QtCore.QSize(40, 40))
        self.level_search_button.setMaximumSize(QtCore.QSize(40, 40))
        self.level_search_button.setIcon(QtGui.QIcon("C:\VS Code\CHINESE_APP\icon\icons8-search-128.png"))
        self.level_search_button.setIconSize(QtCore.QSize(28, 28))
        self.horizontalLayout.addWidget(self.level_search_button)

        self.header_layout.addLayout(self.horizontalLayout)

        # Bảng dữ liệu
        self.tableView = QtWidgets.QTableView()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header_layout.addWidget(self.tableView)

        ## Nút chức năng
        self.delete_word_button = QtWidgets.QPushButton("Xóa từ")
        font_btn = QtGui.QFont()
        font_btn.setPointSize(15)
        font_btn.setBold(True)
        font_btn.setWeight(75)
        self.delete_word_button.setFont(font_btn)
        self.delete_word_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.header_layout.addWidget(self.delete_word_button)


        # Add toàn bộ vào layout chính
        self.verticalLayout_2.addWidget(self.header)

        self.retranslateUi(NotebookPage)
        QtCore.QMetaObject.connectSlotsByName(NotebookPage)

    def retranslateUi(self, NotebookPage):
        _translate = QtCore.QCoreApplication.translate
        NotebookPage.setWindowTitle(_translate("NotebookPage", "Notebook"))

    
