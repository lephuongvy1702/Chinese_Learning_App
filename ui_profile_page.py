from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ProfilePage(object):
    def setupUi(self, ProfilePage):
        ProfilePage.setObjectName("ProfilePage")
        ProfilePage.resize(800, 600)
        ProfilePage.setStyleSheet("background-color: white;")
        
        self.main_layout = QtWidgets.QVBoxLayout(ProfilePage)

        # Header section
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setStyleSheet("color: #3498DB; font-size: 18px;")
        self.header_layout = QtWidgets.QHBoxLayout(self.header_widget)
        
        self.label_days = QtWidgets.QLabel("Số ngày học: ")
        self.label_days.setObjectName("label_days")

        self.label_minutes = QtWidgets.QLabel("Số phút học: ")
        self.label_minutes.setObjectName("label_minutes")

        self.label_level = QtWidgets.QLabel("Cấp độ hiện tại: ")
        self.label_level.setObjectName("label_level")
        
        self.header_layout.addWidget(self.label_days)
        self.header_layout.addWidget(self.label_minutes)
        self.header_layout.addWidget(self.label_level)

    # Progress Circles
        self.circle_widget = QtWidgets.QWidget()
        self.circle_layout = QtWidgets.QHBoxLayout(self.circle_widget)
        self.circle_layout.setSpacing(20)

        # Danh sách chứa các đối tượng vòng tròn
        self.hsk_circles = []

        # Chart placeholder
        self.chart_placeholder = QtWidgets.QFrame()
        self.chart_placeholder.setFixedHeight(300)
        self.chart_placeholder.setObjectName("chart_placeholder")
        self.chart_placeholder.setStyleSheet("""
            QFrame {
                border: 2px dashed #3498DB;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.chart_label = QtWidgets.QLabel("Biểu đồ số từ đã học theo ngày", alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setStyleSheet("color: #3498DB; font-size: 16px; font-weight: bold;")
        self.chart_label.setObjectName("chart_label")

        self.chart_layout = QtWidgets.QVBoxLayout(self.chart_placeholder)
        self.chart_layout.addWidget(self.chart_label)

        # Assemble layout
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.circle_widget)
        self.main_layout.addWidget(self.chart_placeholder)

        self.main_layout.setStretch(0, 1)
        self.main_layout.setStretch(1, 2)
        self.main_layout.setStretch(2, 3)

        self.retranslateUi(ProfilePage)
        QtCore.QMetaObject.connectSlotsByName(ProfilePage)

    def retranslateUi(self, ProfilePage):
        _translate = QtCore.QCoreApplication.translate
        ProfilePage.setWindowTitle(_translate("ProfilePage", "Form"))
