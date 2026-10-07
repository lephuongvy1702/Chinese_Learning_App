# ui_py/ ui_reiview_page.py
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QRadioButton, QButtonGroup, QVBoxLayout


class Ui_ReviewPage(object):
    def __init__(self, user_id=None):
        self.user_id = user_id  # Lưu user_id để sử dụng sau này

    def setupUi(self, ReviewPage):
        self.ui = ReviewPage
        ReviewPage.setObjectName("ReviewPage")
        ReviewPage.resize(631, 501)
        ReviewPage.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.gridLayout = QtWidgets.QGridLayout(ReviewPage)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(parent=ReviewPage)
        self.widget.setStyleSheet("QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    padding: 5px 15px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}\n"
"\n"
"QComboBox {\n"
"    background-color: #3498DB;\n"
"    color: white;                 /* Màu chữ xanh đậm */\n"
"    border: 1px solid #3399cc;\n"
"    border-radius:6px;\n"
"    padding: 4px 8px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #3498DB;\n"
"    color: white;     \n"
"    selection-background-color: #99ccff;\n"
"    selection-color: #003344;\n"
"    border: 1px solid #3399cc;\n"
"    border-radius:6px;\n"
"}\n"
"")
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 35)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.level_box = QtWidgets.QComboBox(parent=self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.level_box.setFont(font)
        self.level_box.setObjectName("level_box")
        self.level_box.addItem("")
        self.level_box.addItem("")
        self.level_box.addItem("")
        self.level_box.addItem("")
        self.level_box.addItem("")
        self.level_box.addItem("")
        self.horizontalLayout.addWidget(self.level_box)
        self.start_question_button = QtWidgets.QPushButton(parent=self.widget)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.start_question_button.setFont(font)
        self.start_question_button.setStyleSheet("font-weight: bold")
        self.start_question_button.setObjectName("start_question_button")
        self.horizontalLayout.addWidget(self.start_question_button)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.widget_2 = QtWidgets.QWidget(parent=ReviewPage)
        self.widget_2.setStyleSheet("QPushButton {\n"
"    background-color: #3498DB;\n"
"    color: white;\n"
"    padding: 5px 15px;\n"
"    border-radius: 6px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #2980B9;\n"
"}\n"
"")
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.question = QtWidgets.QLabel(parent=self.widget_2)
        self.question.setObjectName("question")
        self.verticalLayout_7.addWidget(self.question)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.optionA = QtWidgets.QRadioButton(parent=self.widget_2)
        self.optionA.setText("")
        self.optionA.setObjectName("optionA")
        self.verticalLayout.addWidget(self.optionA)
        self.optionB = QtWidgets.QRadioButton(parent=self.widget_2)
        self.optionB.setText("")
        self.optionB.setObjectName("optionB")
        self.verticalLayout.addWidget(self.optionB)
        self.optionC = QtWidgets.QRadioButton(parent=self.widget_2)
        self.optionC.setText("")
        self.optionC.setObjectName("optionC")
        self.verticalLayout.addWidget(self.optionC)
        self.optionD = QtWidgets.QRadioButton(parent=self.widget_2)
        self.optionD.setText("")
        self.optionD.setObjectName("optionD")
        self.verticalLayout.addWidget(self.optionD)
        self.verticalLayout_7.addLayout(self.verticalLayout)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.check_button = QtWidgets.QPushButton(parent=self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.check_button.setFont(font)
        self.check_button.setStyleSheet("font-weight: bold")
        self.check_button.setObjectName("check_button")
        self.verticalLayout_6.addWidget(self.check_button)
        self.result = QtWidgets.QLabel(parent=self.widget_2)
        self.result.setText("")
        self.result.setObjectName("result")
        self.verticalLayout_6.addWidget(self.result)
        self.next_question_button = QtWidgets.QPushButton(parent=self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.next_question_button.setFont(font)
        self.next_question_button.setStyleSheet("font-weight: bold")
        self.next_question_button.setObjectName("next_question_button")
        self.verticalLayout_6.addWidget(self.next_question_button)
        self.verticalLayout_6.setStretch(0, 2)
        self.verticalLayout_6.setStretch(1, 1)
        self.verticalLayout_6.setStretch(2, 2)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 2)
        self.verticalLayout_7.setStretch(2, 2)
        self.gridLayout_3.addLayout(self.verticalLayout_7, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.widget_2, 1, 0, 1, 1)

        self.retranslateUi(ReviewPage)
        QtCore.QMetaObject.connectSlotsByName(ReviewPage)

    def retranslateUi(self, ReviewPage):
        _translate = QtCore.QCoreApplication.translate
        ReviewPage.setWindowTitle(_translate("ReviewPage", "Form"))
        self.level_box.setItemText(0, _translate("ReviewPage", "HSK1"))
        self.level_box.setItemText(1, _translate("ReviewPage", "HSK2"))
        self.level_box.setItemText(2, _translate("ReviewPage", "HSK3"))
        self.level_box.setItemText(3, _translate("ReviewPage", "HSK4"))
        self.level_box.setItemText(4, _translate("ReviewPage", "HSK5"))
        self.level_box.setItemText(5, _translate("ReviewPage", "HSK6"))
        self.start_question_button.setText(_translate("ReviewPage", "Bắt đầu "))
        self.check_button.setText(_translate("ReviewPage", "Check"))
        self.next_question_button.setText(_translate("ReviewPage", "Câu tiếp theo"))
