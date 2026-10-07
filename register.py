from PyQt6.QtWidgets import QDialog, QMessageBox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui_py.ui_register import Ui_Dialog  # Sử dụng Ui_Dialog thay vì Ui_RegisterDialog
from database.db_helper import register_user
from windows.login import LoginDialog  # Import LoginDialog để quay lại

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Kết nối các nút
        self.ui.dang_ky_button.clicked.connect(self.register)
        self.ui.return_button.clicked.connect(self.show_login)

    def register(self):
        username = self.ui.ten_dang_nhap.text().strip()
        password = self.ui.mat_khau.text().strip()
        confirm_password = self.ui.xac_nhan_mat_khau.text().strip() if hasattr(self.ui, 'xac_nhan_mat_khau') else password

        # Kiểm tra trường trống
        if not username or not password or not confirm_password:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            QMessageBox.critical(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            self.ui.mat_khau.clear()
            if hasattr(self.ui, 'xac_nhan_mat_khau'):
                self.ui.xac_nhan_mat_khau.clear()
            return

        # Thử đăng ký
        if register_user(username, password):
            QMessageBox.information(self, "Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
            self.accept()  # Đóng dialog và quay lại
        else:
            QMessageBox.critical(self, "Lỗi", "Tên đăng nhập đã tồn tại! Vui lòng chọn tên khác.")
            self.ui.ten_dang_nhap.clear()
            self.ui.mat_khau.clear()
            if hasattr(self.ui, 'xac_nhan_mat_khau'):
                self.ui.xac_nhan_mat_khau.clear()

    def show_login(self):
        self.close()
        login_dialog = LoginDialog()
        login_dialog.exec()  # Mở LoginDialog