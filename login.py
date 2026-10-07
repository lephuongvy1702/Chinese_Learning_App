from PyQt6.QtWidgets import QDialog, QMessageBox
import sys
import os
import pandas as pd
import sqlite3
import bcrypt
import hashlib

# Thêm đường dẫn tới thư mục cha để import được các module khác
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui_py.ui_login import Ui_Dialog


class LoginDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.dang_nhap_button.clicked.connect(self.handle_login)
        self.ui.dang_ky_button.clicked.connect(self.open_register)
        self.user_id = None

    def handle_login(self):
        username = self.ui.ten_dang_nhap.text().strip()
        password = self.ui.mat_khau.text().strip()

        if not username or not password:
            self.show_error("Vui lòng nhập đầy đủ thông tin đăng nhập!")
            return

        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()

            # Kiểm tra thông tin đăng nhập
            cursor.execute("""
                SELECT ma_nguoi_dung, mat_khau FROM NguoiDung WHERE ten_dang_nhap=?
            """, (username,))
            result = cursor.fetchone()

            if result:
                user_id, stored_hash = result
                # Thử kiểm tra với bcrypt
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                        self.handle_successful_login(user_id, username)

                        return
                except ValueError:
                    # Nếu bcrypt thất bại, kiểm tra SHA-256
                    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    if stored_hash == sha256_hash:
                        # Cập nhật mật khẩu sang bcrypt
                        new_hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute("""
                            UPDATE NguoiDung 
                            SET mat_khau = ? 
                            WHERE ma_nguoi_dung = ?
                        """, (new_hashed_password, user_id))
                        conn.commit()
                        self.handle_successful_login(user_id, username)

                        return
                    # Kiểm tra văn bản thô
                    if stored_hash == password:
                        # Cập nhật mật khẩu sang bcrypt
                        new_hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute("""
                            UPDATE NguoiDung 
                            SET mat_khau = ? 
                            WHERE ma_nguoi_dung = ?
                        """, (new_hashed_password, user_id))
                        conn.commit()
                        self.handle_successful_login(user_id, username)

                        return

                self.show_error("Tên đăng nhập hoặc mật khẩu không đúng!")
            else:
                self.show_error("Tên đăng nhập hoặc mật khẩu không đúng!")

            conn.close()

        except Exception as e:
            print(f"Lỗi đăng nhập: {e}")
            self.show_error(f"Lỗi đăng nhập: {str(e)}")

    def handle_successful_login(self, user_id, username):
        self.user_id = user_id
        QMessageBox.information(self, "Thành công", f"Chào {username}!")
        self.accept()

    def get_user_id_from_username(self, username, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT ma_nguoi_dung FROM NguoiDung WHERE ten_dang_nhap=?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def show_error(self, message):
        QMessageBox.critical(self, "Lỗi", message)

    def open_register(self):
        from windows.register import RegisterDialog  # IMPORT TRỄ
        self.close()
        register_dialog = RegisterDialog()
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def get_user_id(self):
        return getattr(self, "user_id", None)
    
    