import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt6.QtWidgets import QMainWindow, QDialog
import sqlite3
from ui_py.ui_main_window import Ui_MainWindow
from windows.login import LoginDialog
from windows.home_page import HomePage
from windows.notebook_page import NotebookPage
from windows.review_page import ReviewPage
from windows.profile_page import ProfilePage
from database.db_helper import get_user_assessment_status, import_hsk_vocabulary, ghi_nhan_dang_nhap, ghi_nhan_dang_xuat

import_hsk_vocabulary()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Khởi tạo các trang
        self.notebook_page = NotebookPage(user_id=self.user_id)
        self.profile_page = ProfilePage(user_id=self.user_id)
        self.home_page = HomePage(user_id=self.user_id, notebook_page=self.notebook_page)
        self.review_page = ReviewPage(parent=self, user_id=self.user_id, profile_page=self.profile_page, notebook_page=self.notebook_page, home_page=self.home_page)

        # Thêm các trang vào stackedWidget
        self.ui.stackedWidget.addWidget(self.home_page)
        self.ui.stackedWidget.addWidget(self.notebook_page)
        self.ui.stackedWidget.addWidget(self.review_page)
        self.ui.stackedWidget.addWidget(self.profile_page)

        # Gán sự kiện nút
        self.ui.sign_in_button.clicked.connect(self.open_login_dialog)
        self.ui.home_page_button1.toggled.connect(self.show_home_page)
        self.ui.home_page_button2.toggled.connect(self.show_home_page)
        self.ui.notebook_button1.toggled.connect(self.show_notebook_page)
        self.ui.notebook_button2.toggled.connect(self.show_notebook_page)
        self.ui.review_button1.toggled.connect(self.show_review_page)
        self.ui.review_button2.toggled.connect(self.show_review_page)
        self.ui.profile_button1.toggled.connect(self.show_profile_page)
        self.ui.profile_button2.toggled.connect(self.show_profile_page)
        self.ui.sign_out_button1.toggled.connect(self.handle_sign_out)
        self.ui.sign_out_button2.toggled.connect(self.handle_sign_out)
        self.set_navigation_enabled(False)

    def set_navigation_enabled(self, enabled: bool):
        self.ui.home_page_button1.setEnabled(enabled)
        self.ui.home_page_button2.setEnabled(enabled)
        self.ui.notebook_button1.setEnabled(enabled)
        self.ui.notebook_button2.setEnabled(enabled)
        self.ui.profile_button1.setEnabled(enabled)
        self.ui.profile_button2.setEnabled(enabled)

    def unlock_navigation(self):
        """Gọi khi bài đánh giá hoàn tất"""
        self.set_navigation_enabled(True)
        self.ui.stackedWidget.setCurrentWidget(self.home_page)

    def update_pages_user_id(self):
        """Cập nhật user_id cho các trang và tải lại dữ liệu"""
        self.home_page.user_id = self.user_id
        self.notebook_page.user_id = self.user_id
        self.review_page.user_id = self.user_id
        self.profile_page.user_id = self.user_id

        self.home_page.load_user_vocabulary()
        self.home_page.update_streak()
        self.notebook_page.update_notebook()
        self.notebook_page.refresh_level_lock()
        self.review_page.setup_for_user(self.user_id)
        self.profile_page.load_profile(self.user_id)

    def check_users(self):
        conn = sqlite3.connect("chinese_app.db")  
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM NguoiDung")
        users = cursor.fetchall()
        print("Danh sách người dùng:", users)
        conn.close()

    def open_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_id = dialog.get_user_id()
            if user_id is not None:
                self.user_id = user_id
                print(f"Đăng nhập thành công với user_id: {self.user_id}")
                ghi_nhan_dang_nhap(self.user_id)
                self.update_pages_user_id()
                self.check_users()
                if get_user_assessment_status(self.user_id) == 0:
                    self.set_navigation_enabled(False)
                    self.ui.stackedWidget.setCurrentWidget(self.review_page)
                else:
                    self.set_navigation_enabled(True)
                    self.ui.stackedWidget.setCurrentWidget(self.home_page)
        
    def show_home_page(self, checked):
        if checked:
            self.ui.stackedWidget.setCurrentWidget(self.home_page)

    def show_notebook_page(self, checked):
        if checked:
            self.ui.stackedWidget.setCurrentWidget(self.notebook_page)

    def show_review_page(self, checked):
        if checked:
            self.ui.stackedWidget.setCurrentWidget(self.review_page)

    def show_profile_page(self, checked):
        if checked:
            self.ui.stackedWidget.setCurrentWidget(self.profile_page)
            self.profile_page.load_profile(self.user_id)
    
    def handle_sign_out(self):
        ghi_nhan_dang_xuat(self.user_id)
        self.close()