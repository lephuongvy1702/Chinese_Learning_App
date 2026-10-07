import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import sqlite3
import math 
import matplotlib
matplotlib.use('QTAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget
from ui_py.ui_profile_page import Ui_ProfilePage
from database.db_helper import get_current_user_level, tinh_tong_gio_hoc, lay_tien_do_dict, fetch_hsk_statistics

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QFrame

class HSKBarChartCanvas(FigureCanvas):
    def __init__(self, user_id, parent=None):
        fig = Figure(figsize=(10, 6))
        super().__init__(fig)
        self.setParent(parent)
        self.plot(user_id)

    def plot(self, user_id):
        stats = fetch_hsk_statistics(user_id)
        
        # Kiểm tra nếu không có dữ liệu
        if stats.empty:
            print("Không có dữ liệu để hiển thị biểu đồ.")
            return  # Không vẽ biểu đồ nếu không có dữ liệu
        
        # Chuyển đổi dữ liệu từ numpy.ndarray thành list cho từng cột HSK1 đến HSK6
        dates = stats['ngay'].tolist()  # Danh sách các ngày
        values_hsk = [
            stats['HSK1'].tolist(), 
            stats['HSK2'].tolist(), 
            stats['HSK3'].tolist(), 
            stats['HSK4'].tolist(), 
            stats['HSK5'].tolist(), 
            stats['HSK6'].tolist()
        ]
    
        # Tạo biểu đồ cột chồng
        ax = self.figure.add_subplot(111)

        # Tạo các cột chồng cho mỗi cấp độ HSK
        bottom_values = [0] * len(dates)  # Mảng chứa giá trị chồng lên nhau (ban đầu là 0)
        hsk_colors = ['#3498DB', '#9B59B6', '#1ABC9C', '#E74C3C', '#F39C12', '#2ECC71']  # Màu cho mỗi cấp độ HSK

        for i, hsk_level in enumerate(['HSK1', 'HSK2', 'HSK3', 'HSK4', 'HSK5', 'HSK6']):
            ax.bar(dates, values_hsk[i], width=0.5, label=hsk_level, color=hsk_colors[i], bottom=bottom_values)
            bottom_values = [bottom_values[j] + values_hsk[i][j] for j in range(len(bottom_values))]  # Cập nhật giá trị bottom

        # Thêm các thuộc tính cho biểu đồ
        ax.set_xlabel("Ngày")
        ax.set_ylabel("Số từ đã học")
        ax.set_xticklabels(dates, rotation=0, ha="right")
        ax.legend()

        # Cập nhật biểu đồ trên canvas
        self.draw()

class ProgressCircle(QFrame):
    def __init__(self, progress, parent=None):
        super().__init__(parent)
        self.progress = progress  # Tiến độ
        self.setFixedSize(80, 80)
        self.setStyleSheet("border-radius: 40px; border: 4px solid white;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 4, -4, -4)

        # Vẽ vòng tròn nền (màu xanh nhạt)
        painter.setBrush(QColor("#E3F2FD"))  # Nền xanh nhạt
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect)

        # Vẽ phần tiến độ (pie)
        painter.setBrush(self.get_circle_color(self.progress))
        angle = int(-self.progress * 360 * 16 / 100)
        painter.drawPie(rect, 90 * 16, angle)

        # Vẽ phần trăm: chỉ vẽ nếu tiến độ > 0
        if self.progress > 0:
            # Tính góc giữa phần tô
            center_angle_deg = 90 - (self.progress / 2) * 360 / 100
            center_angle_rad = center_angle_deg * 3.14159 / 180

            # Tính vị trí của chữ phần trăm (tâm cung tròn)
            r = rect.width() / 2 - 10
            cx = rect.center().x() + r * math.cos(center_angle_rad)
            cy = rect.center().y() - r * math.sin(center_angle_rad)


            # Vẽ phần trăm
            painter.setPen(QColor("#000000"))
            painter.setFont(self.font())
            painter.drawText(
                QtCore.QRectF(cx - 20, cy - 10, 40, 20),
                Qt.AlignmentFlag.AlignCenter,
                f"{int(self.progress)}%",
            )


    def setProgress(self, progress):
        self.progress = progress
        self.update()

    def get_circle_color(self, progress):
        """Trả về màu sắc vòng tròn dựa trên tiến độ"""
        if progress >= 80:
            return QColor("#28a745")  # Màu xanh (hoàn thành tốt)
        elif progress >= 50:
            return QColor("#ffc107")  # Màu vàng (hoàn thành trung bình)
        elif progress >= 30:
            return QColor("#fd7e14")  # Màu cam (hoàn thành yếu)
        else:
            return QColor("#5DADE2")  # Màu đỏ (chưa hoàn thành)

class ProfilePage(QWidget):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.ui = Ui_ProfilePage()
        self.ui.setupUi(self)
        self.circle_widget = QtWidgets.QWidget()
        self.circle_layout = QtWidgets.QHBoxLayout(self.circle_widget)
        self.circle_layout.setSpacing(20)

        self.ui.hsk_circles = []  # Danh sách chứa ProgressCircle

    # Tạo 6 vòng tròn tương ứng với HSK1 đến HSK6
        for i in range(1, 7):
            vbox = QtWidgets.QVBoxLayout()
            vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

            label = QtWidgets.QLabel(f"HSK{i}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #3498DB; font-weight: bold;")

            circle = ProgressCircle(0)
            self.ui.hsk_circles.append(circle)

            vbox.addWidget(label)
            vbox.addWidget(circle)

            container = QtWidgets.QWidget()
            container.setLayout(vbox)
            self.circle_layout.addWidget(container)

    # Thêm widget chứa các vòng tròn vào giao diện chính (ví dụ vào một layout cố định)
        self.ui.main_layout.addWidget(self.circle_widget)  # Thay main_layout bằng layout bạn đang dùng

        if user_id:
            print(f"Khởi tạo ProfilePage với user_id: {user_id}")
            self.display_user_statistics()
        else:
            print("Không có user_id, hiển thị giá trị mặc định")
            self._set_default_values()

    def _get_so_ngay_hoc(self):
        """Tính số ngày học dựa trên dữ liệu từ bảng PhienDangNhap"""
        if not self.user_id:
            print("Không có user_id, trả về 0 ngày học.")
            return 0

        try:
            conn = sqlite3.connect("chinese_app.db")
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT DATE(thoi_gian_dang_nhap))
                FROM PhienDangNhap
                WHERE ma_nguoi_dung = ? AND thoi_gian_dang_nhap IS NOT NULL
            """, (self.user_id,))
            result = cursor.fetchone()
            conn.close()
            if not result or result[0] == 0:
                print("Không có dữ liệu phiên đăng nhập cho user_id: {self.user_id}")
            return result[0] if result else 1
        except sqlite3.Error as e:
            print(f"Lỗi khi truy vấn số ngày học: {e}")
            return 0

    def cap_nhat_mau_sac_vong_tron(self, tien_do_dict):
        for i in range(1, 7):
            progress = tien_do_dict.get(f"tien_do_hsk{i}", 0)
            self.ui.hsk_circles[i - 1].setProgress(progress)

    def _set_default_values(self):
        """Đặt giá trị mặc định nếu không có dữ liệu hoặc lỗi xảy ra"""
        self.ui.label_days.setText("Số ngày học: 0")
        self.ui.label_minutes.setText("Số phút học: 0")
        self.ui.label_level.setText("Cấp độ hiện tại: HSK1")

    def _is_valid_user_id(self, user_id):
        """Kiểm tra xem user_id có tồn tại trong bảng NguoiDung không"""
        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT ma_nguoi_dung FROM NguoiDung WHERE ma_nguoi_dung = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except sqlite3.Error as e:
            print(f"Lỗi khi kiểm tra user_id: {e}")
            return False
        
    def display_user_statistics(self):
        """Hiển thị thông tin thống kê người dùng trên giao diện"""
        # Kiểm tra hợp lệ
        if not self._is_valid_user_id(self.user_id):
            print(f"User ID {self.user_id} không hợp lệ.")
            self._set_default_values()
            return

        # Số ngày học
        so_ngay_hoc = self._get_so_ngay_hoc()
        self.ui.label_days.setText(f"Số ngày học: {so_ngay_hoc}")

        # Tổng thời gian học
        try:
            tong_gio_hoc = tinh_tong_gio_hoc(self.user_id)
            self.ui.label_minutes.setText(f"Số phút học: {tong_gio_hoc}")
        except Exception as e:
            print(f"Lỗi khi tính số phút học: {e}")
            self.ui.label_minutes.setText("Số phút học: 0")

        # Cấp độ hiện tại
        try:
            cap_do_hien_tai = get_current_user_level(self.user_id)
            self.ui.label_level.setText(f"Cấp độ hiện tại: {cap_do_hien_tai}")
        except Exception as e:
            print(f"Lỗi khi lấy cấp độ hiện tại: {e}")
            cap_do_hien_tai = "HSK1"
            self.ui.label_level.setText("Cấp độ hiện tại: HSK1")

        # Vòng tròn HSK
        tien_do_dict = lay_tien_do_dict(self.user_id)
    
        # Cập nhật tiến độ và màu sắc cho các vòng tròn
        self.cap_nhat_mau_sac_vong_tron(tien_do_dict)

        # Xóa biểu đồ cũ (nếu có) trong chart_layout
        for i in reversed(range(self.ui.chart_layout.count())):
            widget = self.ui.chart_layout.itemAt(i).widget()
            if widget and isinstance(widget, HSKBarChartCanvas):
                widget.setParent(None)  # Xóa biểu đồ cũ khỏi layout
                widget.deleteLater()
                
        # Thêm biểu đồ mới vào chart_placeholder
        chart_canvas = HSKBarChartCanvas(self.user_id, parent=self.ui.chart_placeholder)
        self.ui.chart_layout.addWidget(chart_canvas)  # Thêm biểu đồ vào layout chart_layout

        # Vẽ lại biểu đồ
        chart_canvas.draw()  # Đảm bảo rằng biểu đồ được vẽ lại đúng cách

    def load_profile(self, user_id):
        self.user_id = user_id
        self.display_user_statistics()


