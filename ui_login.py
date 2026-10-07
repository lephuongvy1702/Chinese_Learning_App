
from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.widget = QtWidgets.QWidget(parent=Dialog)
        self.widget.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.widget.setStyleSheet("QWidget {\n"
"    background-color: #ecf0f1;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 2px solid #3498db;\n"
"    border-radius: 8px;\n"
"    padding: 6px 10px;\n"
"    font-size: 14px;\n"
"    background-color: white;\n"
"    color: #2c3e50;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border: 2px solid #2980b9;\n"
"}\n"
"\n"
"QPushButton#login_button {\n"
"    background-color: #3498db;\n"
"    color: white;\n"
"    border-radius: 10px;\n"
"    padding: 8px 16px;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #54a0ff;  /* khi rê chuột */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #1e70bf;  /* khi nhấn */\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #2e86de;  \n"
"    color: white;              \n"
"    border-radius: 10px;       \n"
"    padding: 6px 12px;\n"
"    font-weight: bold;\n"
"    font-size: 14px;\n"
"}\n"
"")
        self.widget.setObjectName("widget")
        self.label_2 = QtWidgets.QLabel(parent=self.widget)
        self.label_2.setGeometry(QtCore.QRect(170, 20, 60, 60))
        self.label_2.setMinimumSize(QtCore.QSize(60, 60))
        self.label_2.setMaximumSize(QtCore.QSize(60, 60))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("C:\VS Code\CHINESE_APP\icon\chinese.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.dang_nhap_button = QtWidgets.QPushButton(parent=self.widget)
        self.dang_nhap_button.setGeometry(QtCore.QRect(160, 190, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.dang_nhap_button.setFont(font)
        self.dang_nhap_button.setCheckable(True)
        self.dang_nhap_button.setObjectName("dang_nhap_button")
        self.widget1 = QtWidgets.QWidget(parent=self.widget)
        self.widget1.setGeometry(QtCore.QRect(60, 90, 301, 81))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.widget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_3 = QtWidgets.QLabel(parent=self.widget1)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.ten_dang_nhap = QtWidgets.QLineEdit(parent=self.widget1)
        self.ten_dang_nhap.setStyleSheet("")
        self.ten_dang_nhap.setObjectName("ten_dang_nhap")
        self.verticalLayout.addWidget(self.ten_dang_nhap)
        self.mat_khau = QtWidgets.QLineEdit(parent=self.widget1)
        self.mat_khau.setStyleSheet("")
        self.mat_khau.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.mat_khau.setObjectName("mat_khau")
        self.verticalLayout.addWidget(self.mat_khau)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.widget2 = QtWidgets.QWidget(parent=self.widget)
        self.widget2.setGeometry(QtCore.QRect(10, 250, 184, 40))
        self.widget2.setObjectName("widget2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(parent=self.widget2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_4.setMinimumWidth(120)  # Hoặc tăng giá trị này nếu cần
        self.dang_ky_button = QtWidgets.QPushButton(parent=self.widget2)
        self.dang_ky_button.setObjectName("dang_ky_button")
        self.dang_ky_button.setCheckable(True)
        self.horizontalLayout_2.addWidget(self.dang_ky_button)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.dang_nhap_button.setText(_translate("Dialog", "Đăng nhập"))
        self.label.setText(_translate("Dialog", "Tên đăng nhập"))
        self.label_3.setText(_translate("Dialog", "Mật khẩu"))
        self.label_4.setText(_translate("Dialog", "Chưa có tài khoản\u003f"))
        self.dang_ky_button.setText(_translate("Dialog", "Đăng ký"))
