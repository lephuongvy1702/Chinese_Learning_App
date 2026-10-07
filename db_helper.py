import sqlite3
import pandas as pd
import os
import hashlib
from datetime import datetime
import random

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    try:
        password_hashed = hash_password(password)
        cursor.execute("INSERT INTO NguoiDung (ten_dang_nhap, mat_khau, da_lam_danh_gia) VALUES (?, ?, ?)", 
                       (username, password_hashed, 0))  # Đặt da_lam_danh_gia = 0
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    password_hashed = hash_password(password)
    cursor.execute("SELECT * FROM NguoiDung WHERE ten_dang_nhap = ? AND mat_khau = ?", 
                   (username, password_hashed))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            'user': user,
            'da_lam_danh_gia': user[5],
            'user_id': user[0]
        }
    else:
        return None

def get_user_assessment_status(user_id):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("SELECT da_lam_danh_gia FROM NguoiDung WHERE ma_nguoi_dung = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_assessment_status_v2(user_id):
    """Kiểm tra trạng thái hoàn thành bài đánh giá"""
    try:
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute("SELECT da_lam_danh_gia FROM NguoiDung WHERE ma_nguoi_dung = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else False
    except sqlite3.Error as e:
        print(f"Lỗi khi kiểm tra trạng thái đánh giá: {e}")
        return False

def get_initial_assessment_questions(user_id):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ma_cau_hoi, cap_do, cau_hoi, dap_an_A, dap_an_B, dap_an_C, dap_an_D, dap_an_dung
        FROM CauHoiDanhGia
        ORDER BY ma_cau_hoi ASC
    """)
    questions = cursor.fetchall()
    result = []
    for q in questions:
        result.append({
            'ma_cau_hoi': q[0],
            'cap_do': q[1],
            'cau_hoi': q[2],
            'dap_an_A': q[3],
            'dap_an_B': q[4],
            'dap_an_C': q[5],
            'dap_an_D': q[6],
            'dap_an_dung': q[7],
            'dap_an_chon': None
        })
    conn.close()
    return result

def submit_assessment_answers(user_id, questions):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    if not user_id:
        raise ValueError("user_id is invalid or None")
    level_correct_answers = {
        'HSK1': 0, 'HSK2': 0, 'HSK3': 0,
        'HSK4': 0, 'HSK5': 0, 'HSK6': 0
    }
    for question in questions:
        if question.get('dap_an_chon') == question.get('dap_an_dung'):
            cap_do = question.get('cap_do')
            if cap_do in level_correct_answers:
                level_correct_answers[cap_do] += 1
    cursor.execute("""
        INSERT OR REPLACE INTO KetQuaDanhGia (
            ma_nguoi_dung, diem_hsk1, diem_hsk2, diem_hsk3,
            diem_hsk4, diem_hsk5, diem_hsk6
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        level_correct_answers['HSK1'],
        level_correct_answers['HSK2'],
        level_correct_answers['HSK3'],
        level_correct_answers['HSK4'],
        level_correct_answers['HSK5'],
        level_correct_answers['HSK6']
    ))
    cursor.execute("""
        UPDATE NguoiDung
        SET da_lam_danh_gia = 1
        WHERE ma_nguoi_dung = ?
    """, (user_id,))
    conn.commit()
    conn.close()

def calculate_hsk_level(user_id):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT diem_hsk1, diem_hsk2, diem_hsk3, diem_hsk4, diem_hsk5, diem_hsk6
        FROM KetQuaDanhGia
        WHERE ma_nguoi_dung = ?
    """, (user_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return "HSK1"
    scores = {
        'HSK1': result[0],
        'HSK2': result[1],
        'HSK3': result[2],
        'HSK4': result[3],
        'HSK5': result[4],
        'HSK6': result[5],
    }
    hsk_level = "HSK1"
    for level in ['HSK1', 'HSK2', 'HSK3', 'HSK4', 'HSK5', 'HSK6']:
        if scores[level] >= 3:
            hsk_level = level
        else:
            break
    cursor.execute("""
        UPDATE NguoiDung
        SET cap_do_hien_tai = ?
        WHERE ma_nguoi_dung = ?
    """, (hsk_level, user_id))
    conn.commit()
    conn.close()
    return hsk_level

def import_hsk_vocabulary(db_path="chinese_app.db", folder_path="C:\VS Code\CHINESE_APP\database\data"):
    hsk_files = [f"HSK{i}.csv" for i in range(1, 7)]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for file_name in hsk_files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.exists(file_path):
            data = pd.read_csv(file_path)
            for _, row in data.iterrows():
                level = row['Level']
                tu_moi = row['Từ mới']
                phien_am = row.get('Phiên âm', '')
                giai_thich = row.get('Giải thích', '')
                vi_du = row.get('Ví dụ (chữ hán)', '')
                phien_am_vi_du = row.get('Phiên âm ví dụ', '')
                dich = row.get('Dịch', '')
                cursor.execute("""
                    SELECT COUNT(*) FROM TuVungHeThong 
                    WHERE tu_moi = ? AND cap_do = ?
                """, (tu_moi, level))
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute("""
                        INSERT INTO TuVungHeThong 
                        (cap_do, tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (level, tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich))
            print(f"✅ Đã xử lý xong file {file_name}")
        else:
            print(f"⚠️ Không tìm thấy file: {file_name}")
    conn.commit()
    conn.close()

def add_vocabulary_for_user(user_id, hsk_level):
    conn = None
    try:
        max_level = int(hsk_level.replace("HSK", ""))
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        total_added = 0
        for level in range(1, max_level + 1):
            cursor.execute("SELECT ma_tu_vung FROM TuVungHeThong WHERE cap_do = ?", (level,))
            vocabulary = cursor.fetchall()
            if not vocabulary:
                print(f"Không có từ vựng cấp độ HSK{level}")
                continue
            added_count = 0
            for word in vocabulary:
                cursor.execute("""
                    INSERT OR IGNORE INTO TuVungNguoiDung (ma_nguoi_dung, ma_tu_vung)
                    VALUES (?, ?)
                """, (user_id, word[0]))
                added_count += cursor.rowcount
            total_added += added_count
            print(f"✅ Đã thêm {added_count} từ vựng từ cấp độ HSK{level} cho người dùng {user_id}")
        conn.commit()
        print(f"Tổng số từ đã thêm: {total_added}")
    except Exception as e:
        print(f"Lỗi khi thêm từ vựng: {e}")
    finally:
        if conn:
            conn.close()

def get_user_vocabulary(user_id):
    conn = sqlite3.connect("chinese_app.db")
    query = """
    SELECT 
        h.cap_do, h.tu_moi, h.phien_am, h.giai_thich, h.vi_du, h.phien_am_vi_du, h.dich
    FROM TuVungNguoiDung u
    JOIN TuVungHeThong h ON u.ma_tu_vung = h.ma_tu_vung
    WHERE u.ma_nguoi_dung = ?
    """
    data = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return data

def add_word_to_notebook(user_id, cap_do, tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich):
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()

        # Kiểm tra xem từ đã tồn tại cho người dùng chưa
        cursor.execute("""
            SELECT 1 FROM SoTayTuVung
            WHERE ma_nguoi_dung = ? AND tu_moi = ? AND cap_do = ?
        """, (user_id, tu_moi, cap_do))
        if cursor.fetchone():
            print(f"Từ '{tu_moi}' đã có trong sổ tay của người dùng {user_id}.")
            return

        # Nếu chưa có thì thêm vào
        cursor.execute("""
            INSERT INTO SoTayTuVung (
                ma_nguoi_dung, cap_do, tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, cap_do, tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich))
        conn.commit()
        print(f"Đã lưu từ '{tu_moi}' vào sổ tay cho người dùng {user_id}.")
    except sqlite3.Error as e:
        print("Lỗi khi thêm từ vào sổ tay:", e)
    finally:
        conn.close()

def get_notebook_words(user_id):
    conn = sqlite3.connect("chinese_app.db")
    query = """
        SELECT tu_moi, phien_am, giai_thich, vi_du, phien_am_vi_du, dich, cap_do, da_hoc
        FROM SoTayTuVung
        WHERE ma_nguoi_dung = ?
    """
    data = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return data

def get_current_user_level(user_id):
    conn = sqlite3.connect("chinese_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT cap_do_hien_tai FROM NguoiDung WHERE ma_nguoi_dung = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "HSK1"

def delete_word_in_so_tay(user_id, word):
    conn = sqlite3.connect("chinese_app.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SoTayTuVung WHERE ma_nguoi_dung = ? AND tu_moi = ?", (user_id, word))
        conn.commit()
        print(f"Từ '{word}' đã được xóa khỏi sổ tay.")
    except sqlite3.Error as e:
        print(f"Đã xảy ra lỗi khi xóa từ: {e}")
    finally:
        conn.close()

def ghi_nhan_dang_nhap(user_id):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO PhienDangNhap (ma_nguoi_dung, thoi_gian_dang_nhap)
        VALUES (?, ?)
    """, (user_id, thoi_gian))
    conn.commit()
    conn.close()

def ghi_nhan_dang_xuat(user_id):
    """
    Ghi nhận thời gian đăng xuất cho phiên đăng nhập gần nhất của người dùng.
    Tính tổng thời gian đã sử dụng trong phiên (phút).
    """
    try:
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Lấy thời gian hiện tại làm thời gian đăng xuất
        thoi_gian_dang_xuat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Tìm phiên đăng nhập gần nhất chưa có thời gian đăng xuất
        cursor.execute("""
            SELECT thoi_gian_dang_nhap, ma_phien
            FROM PhienDangNhap
            WHERE ma_nguoi_dung = ? AND thoi_gian_dang_xuat IS NULL
            ORDER BY thoi_gian_dang_nhap DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()

        if result:
            thoi_gian_dang_nhap_str, ma_phien = result

            # Chuyển đổi thời gian chuỗi sang đối tượng datetime
            try:
                thoi_gian_dang_nhap = datetime.strptime(thoi_gian_dang_nhap_str, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Lỗi định dạng thời gian đăng nhập: {e}")
                conn.close()
                return

            thoi_gian_dang_xuat_dt = datetime.strptime(thoi_gian_dang_xuat, "%Y-%m-%d %H:%M:%S")

            # Tính tổng thời gian sử dụng trong phiên (phút)
            tong_thoi_gian_phut = (thoi_gian_dang_xuat_dt - thoi_gian_dang_nhap).total_seconds() / 60

            # Cập nhật thời gian đăng xuất và tổng thời gian vào CSDL
            cursor.execute("""
                UPDATE PhienDangNhap
                SET thoi_gian_dang_xuat = ?, tong_thoi_gian_phut = ?
                WHERE ma_phien = ?
            """, (thoi_gian_dang_xuat, tong_thoi_gian_phut, ma_phien))

            conn.commit()
            print("Đã ghi nhận đăng xuất.")
        else:
            print("Không tìm thấy phiên đăng nhập đang hoạt động.")
    except Exception as e:
        print(f"Lỗi khi ghi nhận đăng xuất: {e}")
    finally:
        conn.close()

def tinh_tong_gio_hoc(user_id):
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT thoi_gian_dang_nhap, thoi_gian_dang_xuat
        FROM PhienDangNhap
        WHERE ma_nguoi_dung = ? AND thoi_gian_dang_xuat IS NOT NULL
    """, (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    total_seconds = 0
    for start_str, end_str in sessions:
        try:
            start_str = start_str.replace('T', ' ')
            end_str = end_str.replace('T', ' ')
            try:
                start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            try:
                end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
            total_seconds += (end - start).total_seconds()
        except Exception as e:
            print(f"Error processing session {start_str} - {end_str}: {e}")
            continue
    total_hours = round(total_seconds / 60, 2)
    return total_hours

def load_vocabulary_by_hsk_level(user_id, hsk_level):
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tu_moi, phien_am, giai_thich, ma_so_tay 
            FROM SoTayTuVung 
            WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 0
        """, (user_id, hsk_level))
        vocabulary = [{'tu_moi': row[0], 'phien_am': row[1], 'giai_thich': row[2], 'ma_so_tay': row[3]} for row in cursor.fetchall()]
        conn.close()
        if not vocabulary:
            print(f"Không tìm thấy từ vựng chưa học cho HSK {hsk_level}.")
        return vocabulary
    except sqlite3.Error as e:
        print(f"Lỗi khi tải từ vựng: {e}")
        return []

def load_learned_vocabulary_by_hsk_level(user_id, hsk_level):
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tu_moi, phien_am, giai_thich, ma_so_tay 
            FROM SoTayTuVung 
            WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 1
        """, (user_id, hsk_level))
        vocabulary = [{'tu_moi': row[0], 'phien_am': row[1], 'giai_thich': row[2], 'ma_so_tay': row[3]} for row in cursor.fetchall()]
        conn.close()
        if not vocabulary:
            print(f"Không tìm thấy từ vựng đã học cho HSK {hsk_level}.")
        return vocabulary
    except sqlite3.Error as e:
        print(f"Lỗi khi tải từ vựng đã học: {e}")
        return []

def update_vocabulary_status(ma_so_tay, is_correct):
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE SoTayTuVung 
            SET da_hoc = ? 
            WHERE ma_so_tay = ?
        """, (1 if is_correct else 0, ma_so_tay))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Lỗi khi cập nhật trạng thái từ vựng: {e}")

def check_vocabulary_progress(user_id, hsk_level):
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()

        total_words_dict = {
            'HSK1': 149,
            'HSK2': 151,
            'HSK3': 296,
            'HSK4': 601,
            'HSK5': 1296,
            'HSK6': 2514
        }
        total_words = total_words_dict.get(hsk_level, 0)

        cursor.execute("""
            SELECT COUNT(*) 
            FROM SoTayTuVung 
            WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 1
        """, (user_id, hsk_level))
        learned_words = cursor.fetchone()[0]

        if total_words == 0:
            print(f"Không có từ vựng nào cho HSK {hsk_level}.")
            conn.close()
            return False, 0

        progress = (learned_words / total_words) * 100
        print(f"Tiến độ HSK {hsk_level}: {learned_words}/{total_words} từ ({progress:.2f}%)")

        conn.close()
        return progress >= 80, progress

    except sqlite3.Error as e:
        print(f"Lỗi khi kiểm tra tiến độ từ vựng: {e}")
        return False, 0

def get_so_ngay_dang_nhap(user_id):
    try:
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Lấy tất cả các ngày đăng nhập mà không trùng lặp
        cursor.execute("""
            SELECT DISTINCT DATE(thoi_gian_dang_nhap)
            FROM PhienDangNhap
            WHERE ma_nguoi_dung = ? AND thoi_gian_dang_xuat IS NOT NULL
        """, (user_id,))
        result = cursor.fetchall()

        conn.close()

        # Số ngày đăng nhập
        return len(result)

    except Exception as e:
        print(f"Lỗi khi lấy số ngày đăng nhập: {e}")
        return 0

def cap_nhat_tien_do_hoc(user_id):
    try:
        print(f"Đang cập nhật tiến độ học cho người dùng ID: {user_id}")
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Đếm số từ đã học trong tất cả các cấp độ
        cursor.execute("""
            SELECT COUNT(*)
            FROM SoTayTuVung
            WHERE ma_nguoi_dung = ? AND da_hoc = 1
        """, (user_id,))
        so_tu_da_hoc = cursor.fetchone()[0]
        print(f"Số từ đã học: {so_tu_da_hoc}")

        # Tiến độ các cấp độ HSK
        total_words_dict = {
            'HSK1': 149,
            'HSK2': 151,
            'HSK3': 296,
            'HSK4': 601,
            'HSK5': 1296,
            'HSK6': 2514
        }

        tien_do_dict = {}

        for hsk_level, total_words in total_words_dict.items():
            cursor.execute("""
                SELECT COUNT(*)
                FROM SoTayTuVung
                WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 1
            """, (user_id, hsk_level))
            learned_words = cursor.fetchone()[0]
            tien_do_dict[f"tien_do_{hsk_level.lower()}"] = (learned_words / total_words) * 100
            print(f"Tiến độ HSK {hsk_level}: {tien_do_dict[f'tien_do_{hsk_level.lower()}']:.2f}%")

        # Kiểm tra xem đã có bản ghi cho người dùng này chưa
        cursor.execute("""
            SELECT ma_tien_do FROM TienDoHoc
            WHERE ma_nguoi_dung = ?
        """, (user_id,))
        existing = cursor.fetchone()

        if existing:
            print("Bản ghi tiến độ đã tồn tại, đang cập nhật...")
            # Cập nhật nếu đã có bản ghi
            update_query = """
                UPDATE TienDoHoc
                SET so_tu_da_hoc = ?, tien_do_hsk1 = ?, tien_do_hsk2 = ?, tien_do_hsk3 = ?, 
                    tien_do_hsk4 = ?, tien_do_hsk5 = ?, tien_do_hsk6 = ?
                WHERE ma_nguoi_dung = ?
            """
            cursor.execute(update_query, (
                so_tu_da_hoc, tien_do_dict['tien_do_hsk1'], tien_do_dict['tien_do_hsk2'], 
                tien_do_dict['tien_do_hsk3'], tien_do_dict['tien_do_hsk4'], 
                tien_do_dict['tien_do_hsk5'], tien_do_dict['tien_do_hsk6'], user_id
            ))
        else:
            print("Chưa có bản ghi tiến độ, đang tạo mới...")
            # Thêm mới nếu chưa có bản ghi
            insert_query = """
                INSERT INTO TienDoHoc (ma_nguoi_dung, so_tu_da_hoc, tien_do_hsk1, tien_do_hsk2, 
                    tien_do_hsk3, tien_do_hsk4, tien_do_hsk5, tien_do_hsk6)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                user_id, so_tu_da_hoc, tien_do_dict['tien_do_hsk1'], tien_do_dict['tien_do_hsk2'], 
                tien_do_dict['tien_do_hsk3'], tien_do_dict['tien_do_hsk4'], 
                tien_do_dict['tien_do_hsk5'], tien_do_dict['tien_do_hsk6']
            ))

        # Commit các thay đổi vào cơ sở dữ liệu
        print("Đang commit các thay đổi vào cơ sở dữ liệu...")
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Lỗi khi cập nhật tiến độ học: {e}")

def lay_tien_do_dict(user_id):
    """
    Lấy tiến độ học của người dùng theo từng cấp độ HSK.
    
    user_id: ID của người dùng cần lấy tiến độ.
    
    Trả về một dictionary chứa tiến độ của từng cấp độ HSK.
    """
    try:
        conn = sqlite3.connect("chinese_app.db")
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Tiến độ các cấp độ HSK
        total_words_dict = {
            'HSK1': 149,
            'HSK2': 151,
            'HSK3': 296,
            'HSK4': 601,
            'HSK5': 1296,
            'HSK6': 2514
        }

        tien_do_dict = {}

        # Lấy tiến độ của từng cấp độ HSK
        for hsk_level, total_words in total_words_dict.items():
            cursor.execute("""
                SELECT COUNT(*)
                FROM SoTayTuVung
                WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 1
            """, (user_id, hsk_level))
            learned_words = cursor.fetchone()[0]
            tien_do_dict[f"tien_do_{hsk_level.lower()}"] = (learned_words / total_words) * 100
            print(f"Tiến độ HSK {hsk_level}: {tien_do_dict[f'tien_do_{hsk_level.lower()}']:.2f}%")

        conn.close()

        # Trả về dictionary chứa tiến độ
        return tien_do_dict

    except Exception as e:
        print(f"Lỗi khi lấy tiến độ học: {e}")
        return None


def update_user_hsk_level(user_id, current_hsk_level):
    try:
        levels = ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"]
        current_index = levels.index(current_hsk_level)
        if current_index < len(levels) - 1:
            next_level = levels[current_index + 1]
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE NguoiDung 
                SET cap_do_hien_tai = ? 
                WHERE ma_nguoi_dung = ?
            """, (next_level, user_id))
            conn.commit()
            conn.close()
            print(f"Đã nâng cấp độ HSK của người dùng {user_id} lên {next_level}")
            return next_level
        else:
            print("Người dùng đã đạt cấp độ HSK cao nhất (HSK6).")
            return current_hsk_level
    except sqlite3.Error as e:
        print(f"Lỗi khi cập nhật cấp độ HSK: {e}")
        return current_hsk_level

def start_review(user_id, hsk_level=None):
    """Tạo danh sách câu hỏi ôn tập từ vựng chưa học cho cấp độ HSK được chọn"""
    try:
        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()
        
        # Lấy cấp độ HSK hiện tại của người dùng
        cursor.execute("""
            SELECT cap_do_hien_tai FROM NguoiDung WHERE ma_nguoi_dung = ?
        """, (user_id,))
        current_hsk_level = cursor.fetchone()
        current_hsk_level = current_hsk_level[0] if current_hsk_level else "HSK1"
        
        # Nếu không có hsk_level được chỉ định, sử dụng cấp độ hiện tại
        if hsk_level is None:
            hsk_level = current_hsk_level
        
        # Kiểm tra xem cấp độ được chọn có hợp lệ không
        levels = ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"]
        current_level_index = levels.index(current_hsk_level)
        selected_level_index = levels.index(hsk_level)
        if selected_level_index > current_level_index:
            conn.close()
            return f"Không thể ôn tập HSK{hsk_level} vì bạn chưa đạt cấp độ này. Cấp độ hiện tại: {current_hsk_level}."

        # Lấy từ vựng chưa học cho cấp độ được chọn
        cursor.execute("""
            SELECT tu_moi, phien_am, giai_thich, ma_so_tay 
            FROM SoTayTuVung 
            WHERE ma_nguoi_dung = ? AND cap_do = ? AND da_hoc = 0
        """, (user_id, hsk_level))
        vocabulary = [{'tu_moi': row[0], 'phien_am': row[1], 'giai_thich': row[2], 'ma_so_tay': row[3]} for row in cursor.fetchall()]
        conn.close()

        if len(vocabulary) < 20:
            return f"Không đủ từ vựng (cần ít nhất 20 từ, hiện có {len(vocabulary)} từ) để tạo bài ôn tập HSK {hsk_level}."

        random.shuffle(vocabulary)
        selected_words = vocabulary[:20]
        questions = []
        for word in selected_words:
            distractors = [v['giai_thich'] for v in random.sample([v for v in vocabulary if v['tu_moi'] != word['tu_moi']], 3)]
            options = distractors + [word['giai_thich']]
            random.shuffle(options)
            correct_answer = word['giai_thich']
            correct_option = chr(65 + options.index(correct_answer))
            question = {
                'cau_hoi': f"Từ '{word['tu_moi']}' có nghĩa là gì?",
                'dap_an_A': options[0],
                'dap_an_B': options[1],
                'dap_an_C': options[2],
                'dap_an_D': options[3],
                'dap_an_dung': correct_option,
                'dap_an_chon': None,
                'ma_so_tay': word['ma_so_tay'],
                'is_correct': False
            }
            questions.append(question)
        print(f"Đã tạo {len(questions)} câu hỏi ôn tập HSK {hsk_level} cho người dùng {user_id}")
        return questions
    except sqlite3.Error as e:
        print(f"Lỗi khi tạo bài ôn tập: {e}")
        return "Lỗi cơ sở dữ liệu khi tạo bài ôn tập."

def check_answer_and_mark(user_id, question, selected_answer):
    """Kiểm tra đáp án và đánh dấu từ vựng đã học nếu đúng"""
    try:
        is_correct = selected_answer == question['dap_an_dung']
        if is_correct:
            conn = sqlite3.connect("chinese_app.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE SoTayTuVung 
                SET da_hoc = 1 
                WHERE ma_so_tay = ?
            """, (question['ma_so_tay'],))
            conn.commit()
            conn.close()
        return is_correct
    except sqlite3.Error as e:
        print(f"Lỗi khi cập nhật trạng thái từ vựng: {e}")
        return False

def import_words_to_next_hsk_level(user_id, current_hsk_level):
    try:
        # Chuyển "HSK1" → 1, "HSK2" → 2, v.v.
        current_level_number = int(current_hsk_level.replace("HSK", ""))
        next_level_number = current_level_number + 1

        if next_level_number > 6:
            print("Người dùng đã ở cấp độ HSK cao nhất (HSK6).")
            return

        conn = sqlite3.connect("chinese_app.db")
        cursor = conn.cursor()

        # Lấy tất cả từ vựng cấp độ tiếp theo từ bảng TuVungHeThong
        cursor.execute("""
            SELECT ma_tu_vung
            FROM TuVungHeThong
            WHERE cap_do = ?
        """, (str(next_level_number),))  # Lưu ý: cap_do là kiểu TEXT nên ép sang chuỗi

        words = cursor.fetchall()

        # Chèn từ vào bảng TuVungNguoiDung nếu chưa có
        for (ma_tu_vung,) in words:
            cursor.execute("""
                INSERT OR IGNORE INTO TuVungNguoiDung (ma_nguoi_dung, ma_tu_vung)
                VALUES (?, ?)
            """, (user_id, ma_tu_vung))

        conn.commit()
        conn.close()

        print(f"Đã nhập {len(words)} từ cấp độ HSK{next_level_number} vào TuVungNguoiDung cho người dùng {user_id}.")

    except sqlite3.Error as e:
        print(f"Lỗi khi import từ vựng HSK tiếp theo: {e}")

def cap_nhat_thong_ke_tu_on_tap(ma_nguoi_dung: int, cap_do: str, so_tu_da_hoc: int):
    conn = sqlite3.connect("chinese_app.db")
    cursor = conn.cursor()
    ngay = datetime.now().strftime('%Y-%m-%d')
    cot_cap_do = f"tong_{cap_do.lower()}"  # ví dụ: tong_hsk2

    # Kiểm tra xem đã có thống kê hôm nay chưa
    cursor.execute("""
        SELECT ma_thong_ke FROM ThongKeHSKTheoNgay
        WHERE ma_nguoi_dung = ? AND ngay = ?;
    """, (ma_nguoi_dung, ngay))
    row = cursor.fetchone()

    if not row:
        # Tạo mới dòng thống kê
        cursor.execute("""
            INSERT INTO ThongKeHSKTheoNgay (ma_nguoi_dung, ngay)
            VALUES (?, ?);
        """, (ma_nguoi_dung, ngay))

    # Cập nhật số từ đã học cho cấp độ tương ứng
    cursor.execute(f"""
        UPDATE ThongKeHSKTheoNgay
        SET {cot_cap_do} = {cot_cap_do} + ?
        WHERE ma_nguoi_dung = ? AND ngay = ?;
    """, (so_tu_da_hoc, ma_nguoi_dung, ngay))

    conn.commit()
    conn.close()

def fetch_hsk_statistics(user_id):
    conn = sqlite3.connect("chinese_app.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ngay, tong_hsk1, tong_hsk2, tong_hsk3, tong_hsk4, tong_hsk5, tong_hsk6
        FROM ThongKeHSKTheoNgay
        WHERE ma_nguoi_dung = ?
        ORDER BY ngay ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    data = pd.DataFrame(rows, columns=[
        "ngay", "HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"
    ])
    return data
