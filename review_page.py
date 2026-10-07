import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from PyQt6.QtWidgets import QWidget, QMessageBox, QComboBox
from PyQt6.QtGui import QFont
from ui_py.ui_review_page import Ui_ReviewPage
from database.db_helper import (
    get_initial_assessment_questions,
    submit_assessment_answers,
    calculate_hsk_level,
    add_vocabulary_for_user,
    get_user_assessment_status_v2,
    start_review,
    check_answer_and_mark,
    check_vocabulary_progress,
    update_user_hsk_level, 
    import_words_to_next_hsk_level,
    cap_nhat_tien_do_hoc,
    cap_nhat_thong_ke_tu_on_tap
)
import sqlite3

class ReviewPage(QWidget):
    def __init__(self, parent=None, user_id=None, profile_page=None, notebook_page=None, home_page=None):
        super().__init__(parent)
        self.user_id = user_id
        self.profile_page = profile_page
        self.notebook_page = notebook_page
        self.home_page = home_page
        self.ui = Ui_ReviewPage(user_id=self.user_id)
        self.ui.setupUi(self)
        large_font = QFont()
        large_font.setPointSize(14)  # Tăng kích cỡ chữ (tuỳ chỉnh nếu cần)

        # Áp dụng cho câu hỏi
        self.ui.question.setFont(large_font)

        # Áp dụng cho các nút chọn đáp án
        self.ui.optionA.setFont(large_font)
        self.ui.optionB.setFont(large_font)
        self.ui.optionC.setFont(large_font)
        self.ui.optionD.setFont(large_font)

    # Áp dụng cho kết quả (ví dụ: result_label nếu có)
        self.ui.result.setFont(large_font)

        self.current_question_index = 0
        self.questions = []  # Cho bài kiểm tra đánh giá
        self.review_questions = []  # Cho bài ôn tập
        self.has_completed_assessment = False
        self.mode = "assessment"
        self.selected_hsk_level = None  # Cấp độ HSK được chọn để ôn tập
        self.is_reviewing = False  # Trạng thái ôn tập

    def setup_for_user(self, user_id):
        self.user_id = user_id
        self.has_completed_assessment = get_user_assessment_status_v2(self.user_id)
        print(f"[DEBUG] Trạng thái đánh giá hiện tại: {self.has_completed_assessment}")

        self.mode = "assessment" if not self.has_completed_assessment else "review"
        self.setup_ui_connections()
        if self.has_completed_assessment:
            self.setup_hsk_level_selector()

    def setup_hsk_level_selector(self):
        """Thiết lập QComboBox để chọn cấp độ HSK"""
        current_hsk_level = self.get_current_hsk_level()
        max_level = int(current_hsk_level.replace("HSK", ""))
        available_levels = [f"HSK{i}" for i in range(1, max_level + 1)]  # Chỉ hiển thị cấp độ từ HSK1 đến cấp hiện tại

        self.ui.level_box.clear()
        self.ui.level_box.addItems(available_levels)
        self.ui.level_box.setCurrentText(current_hsk_level)
        self.selected_hsk_level = current_hsk_level
        self.ui.level_box.currentTextChanged.connect(self.on_hsk_level_changed)

    def on_hsk_level_changed(self, hsk_level):
        """Xử lý khi người dùng thay đổi cấp độ HSK"""
        self.selected_hsk_level = hsk_level
        self.ui.result.setText(f"Đã chọn ôn tập cấp độ {hsk_level}. Nhấn 'Bắt đầu ôn tập' để tiếp tục.")
        self.ui.start_question_button.setEnabled(True)
        self.ui.check_button.setEnabled(False)
        self.ui.next_question_button.setEnabled(False)
        self.hide_question_ui()

    def setup_ui_connections(self):
        """Thiết lập các kết nối tín hiệu cho UI"""
        self.ui.start_question_button.clicked.connect(self.start_current_mode)
        self.ui.check_button.clicked.connect(self.check_answer)
        self.ui.next_question_button.clicked.connect(self.next_question)

        if self.has_completed_assessment:
            self.prepare_review_mode()
        else:
            self.ui.start_question_button.setText("Bắt đầu bài đánh giá")
            self.ui.result.setText("Vui lòng hoàn thành bài đánh giá trước khi ôn tập.")
            self.ui.check_button.setEnabled(False)
            self.ui.next_question_button.setEnabled(False)
            self.ui.level_box.setEnabled(False)

    def start_current_mode(self):
        """Khởi động chế độ hiện tại (đánh giá hoặc ôn tập)"""
        if self.mode == "assessment":
            self.start_assessment()
        else:
            self.start_review()

    def load_questions(self):
        if hasattr(self, 'questions_loaded') and self.questions_loaded:
            return True
        """Tải câu hỏi cho bài kiểm tra đánh giá"""
        self.questions = get_initial_assessment_questions(self.user_id)
        if not self.questions:
            print(f"Lỗi: Không thể tải câu hỏi khảo sát. ID người dùng: {self.user_id}")
            QMessageBox.warning(self, "Lỗi", "Không thể tải câu hỏi khảo sát. Vui lòng kiểm tra cơ sở dữ liệu.")
            self.ui.result.setText("Không thể tạo bài khảo sát.")
            return False
        print(f"Đã tải {len(self.questions)} câu hỏi khảo sát. ID người dùng: {self.user_id}")
        self.questions_loaded = True
        return True

    def display_question(self):
        """Hiển thị câu hỏi dựa trên chế độ hiện tại"""
        questions = self.questions if self.mode == "assessment" else self.review_questions
        if self.current_question_index >= len(questions):
            self.ui.result.setText("Hoàn tất!")
            return

        question = questions[self.current_question_index]
        self.ui.question.setText(question['cau_hoi'])
        self.ui.optionA.setText(f"A. {question['dap_an_A']}")
        self.ui.optionB.setText(f"B. {question['dap_an_B']}")
        self.ui.optionC.setText(f"C. {question['dap_an_C']}")
        self.ui.optionD.setText(f"D. {question['dap_an_D']}")
        for option in [self.ui.optionA, self.ui.optionB, self.ui.optionC, self.ui.optionD]:
            option.setChecked(False)

    def start_assessment(self):
        """Bắt đầu bài kiểm tra đánh giá"""
        if not self.user_id:
            print("Lỗi: ID người dùng không hợp lệ hoặc rỗng")
            QMessageBox.warning(self, "Lỗi", "Không thể bắt đầu bài kiểm tra: ID người dùng không hợp lệ.")
            return
        
        if not hasattr(self, 'questions_loaded') or not self.questions_loaded:
            self.current_question_index = 0
            self.ui.result.clear()
            self.ui.check_button.setEnabled(True)
            self.ui.next_question_button.setEnabled(False)
            if not self.load_questions():
                return
        
        self.display_question()
        self.ui.start_question_button.setEnabled(False)

    def check_answer(self):
        """Kiểm tra đáp án cho cả hai chế độ"""
        questions = self.questions if self.mode == "assessment" else self.review_questions
        if self.current_question_index >= len(questions):
            return

        selected_answer = self.get_selected_option()
        if not selected_answer:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một đáp án!")
            return

        question = questions[self.current_question_index]
        question['dap_an_chon'] = selected_answer

        if self.mode == "assessment":
            if selected_answer == question['dap_an_dung']:
                self.ui.result.setText("Đúng!")
            else:
                self.ui.result.setText(f"Sai! Đáp án đúng là: {question['dap_an_dung']}")
        else:
            question['is_correct'] = selected_answer == question['dap_an_dung']
            if question['is_correct']:
                if check_answer_and_mark(self.user_id, question, selected_answer):
                    self.mark_vocab_learned(question)
                else:
                    self.ui.result.setText(f"Sai! Đáp án đúng là: {question['dap_an_dung']}")
            else:
                self.ui.result.setText(f"Sai! Đáp án đúng là: {question['dap_an_dung']}")

        self.ui.check_button.setEnabled(False)
        self.ui.next_question_button.setEnabled(True)

    def next_question(self):
        """Chuyển sang câu hỏi tiếp theo"""
        self.current_question_index += 1
        questions = self.questions if self.mode == "assessment" else self.review_questions
        if self.current_question_index < len(questions):
            self.display_question()
            self.ui.check_button.setEnabled(True)
            self.ui.next_question_button.setEnabled(False)
            self.ui.result.clear()
        else:
            if self.mode == "assessment":
                self.finish_assessment()
            else:
                self.finish_review()

    def finish_assessment(self):
        """Hoàn tất bài kiểm tra đánh giá"""
        self.ui.result.setText("Bài kiểm tra đã hoàn thành!")
        submit_assessment_answers(self.user_id, self.questions)
        hsk_level = calculate_hsk_level(self.user_id)
        self.show_hsk_popup(hsk_level)
        add_vocabulary_for_user(self.user_id, hsk_level)
        if self.notebook_page:
            self.notebook_page.update_notebook()
        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE NguoiDung SET da_lam_danh_gia = 1 WHERE ma_nguoi_dung = ?", (self.user_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Lỗi khi cập nhật trạng thái đánh giá: {e}")
        self.has_completed_assessment = True
        self.mode = "review"
        self.prepare_review_mode(first_time_review=True)
        self.window().unlock_navigation()
        self.window().update_pages_user_id()
        self.hide_question_ui()
        self.ui.check_button.setEnabled(False)
        self.ui.next_question_button.setEnabled(False)
        self.ui.level_box.setEnabled(True)

        if hasattr(self, 'questions_loaded'):
            del self.questions_loaded

    def show_hsk_popup(self, hsk_level, progress=None, level_up=False):
        """Hiển thị thông báo kết quả"""
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Thông báo")
        if level_up:
            message_box.setText(f"Chúc mừng! Bạn đã hoàn thành {progress:.2f}% từ vựng HSK {hsk_level} và được nâng lên cấp độ tiếp theo!")
        elif self.review_questions and progress is not None:
            message_box.setText(f"Bạn đã hoàn thành bài ôn tập từ vựng HSK {hsk_level}! Tiến độ: {progress:.2f}%")
        else:
            message_box.setText(f"Chúc mừng! Trình độ HSK của bạn là: {hsk_level}")
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()

    def hide_question_ui(self):
        """Ẩn giao diện câu hỏi"""
        self.ui.question.clear()
        for option in [self.ui.optionA, self.ui.optionB, self.ui.optionC, self.ui.optionD]:
            option.setText("")
            option.setChecked(False)
        self.ui.result.clear()

    def get_selected_option(self):
        """Lấy đáp án được chọn"""
        if self.ui.optionA.isChecked():
            return 'A'
        elif self.ui.optionB.isChecked():
            return 'B'
        elif self.ui.optionC.isChecked():
            return 'C'
        elif self.ui.optionD.isChecked():
            return 'D'
        return None

    def prepare_review_mode(self, first_time_review=False):
        """Chuẩn bị chế độ ôn tập"""
        self.first_time_review = first_time_review
        self.ui.result.setText("Chọn cấp độ HSK và bắt đầu ôn tập từ vựng!")
        self.ui.start_question_button.setText("Bắt đầu ôn tập")
        self.ui.start_question_button.setEnabled(True)
        self.ui.check_button.setEnabled(False)
        self.ui.next_question_button.setEnabled(False)
        self.setup_hsk_level_selector()

    def start_review(self):
        """Bắt đầu bài ôn tập với cấp độ HSK được chọn"""
        if self.is_reviewing:
            return

        self.is_reviewing = True
        result = start_review(self.user_id, self.selected_hsk_level)
        if isinstance(result, str):
            if self.first_time_review:
                QMessageBox.information(self, "Chúc mừng", result)
            else:
                QMessageBox.warning(self, "Lỗi", result)
            self.ui.start_question_button.setEnabled(True)
            self.is_reviewing = False
            return

        self.review_questions = result
        self.current_question_index = 0
        self.ui.result.clear()
        self.display_question()
        self.ui.check_button.setEnabled(True)
        self.ui.next_question_button.setEnabled(False)
        self.ui.start_question_button.setEnabled(False)

        total_questions = len(self.review_questions)
        if total_questions < 20:
            print(f"Chú ý: Đã tải {total_questions} câu hỏi ôn tập HSK {self.selected_hsk_level} cho người dùng {self.user_id}.")
            QMessageBox.information(self, "Thông báo", f"Chỉ có {total_questions} từ vựng chưa học ở HSK {self.selected_hsk_level}. Hãy thử cấp độ khác hoặc thêm từ vựng!")
        else:
            print(f"Đã tạo {total_questions} câu hỏi ôn tập HSK {self.selected_hsk_level} cho người dùng {self.user_id}")

    def mark_vocab_learned(self, question):
        """Đánh dấu từ vựng đã học"""
        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT tu_moi FROM SoTayTuVung WHERE ma_so_tay = ?", (question['ma_so_tay'],))
            result = cursor.fetchone()
            conn.close()

            if result:
                tu_moi = result[0]
                self.ui.result.setText("Đúng!")
                if self.notebook_page:
                    self.notebook_page.update_notebook_checkbox(self.user_id, tu_moi)
            else:
                self.ui.result.setText("Lỗi: Không tìm thấy từ vựng trong sổ tay!")
        except Exception as e:
            self.ui.result.setText(f"Lỗi cơ sở dữ liệu: {str(e)}")

    def get_current_hsk_level(self):
        """Lấy cấp độ HSK hiện tại của người dùng"""
        try:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT cap_do_hien_tai FROM NguoiDung WHERE ma_nguoi_dung = ?", (self.user_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "HSK1"
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy cấp độ HSK: {e}")
            return "HSK1"

    def finish_review(self):
        """Hoàn tất bài ôn tập"""
        correct_answers = sum(1 for q in self.review_questions if q.get('dap_an_chon') == q.get('dap_an_dung'))
        current_hsk_level = self.get_current_hsk_level()
        #cap_nhat_tien_do_hoc(self.user_id)
        is_complete, progress = check_vocabulary_progress(self.user_id, self.selected_hsk_level)
        level_up = False
        if is_complete and self.selected_hsk_level == current_hsk_level:
            new_level = update_user_hsk_level(self.user_id, current_hsk_level)
            import_words_to_next_hsk_level(self.user_id, current_hsk_level)
            current_hsk_level = new_level
            level_up = True
            self.setup_hsk_level_selector()
            if self.home_page:
                self.home_page.load_user_vocabulary()
            if self.notebook_page:
                self.notebook_page.refresh_level_lock()
        
        cap_nhat_thong_ke_tu_on_tap(self.user_id, self.selected_hsk_level, correct_answers)
        message = f"Bạn đã trả lời đúng {correct_answers} trên {len(self.review_questions)} câu!"

        self.show_hsk_popup(self.selected_hsk_level, progress, level_up)
        if not is_complete and progress < 80:
            print(f"Tiến độ HSK {self.selected_hsk_level}: {progress:.2f}%. Cần đạt 80% để mở cấp độ tiếp theo.")
            QMessageBox.information(self, "Thông báo", 
                                    f"Tiến độ HSK {self.selected_hsk_level}: {progress:.2f}%. Hãy tiếp tục học để đạt 80% và mở cấp độ tiếp theo!")
        if self.notebook_page:
            self.notebook_page.update_notebook()
        cap_nhat_tien_do_hoc(self.user_id)
        self.ui.result.setText(message)
        self.ui.check_button.setEnabled(False)
        self.ui.next_question_button.setEnabled(False)
        self.is_reviewing = False