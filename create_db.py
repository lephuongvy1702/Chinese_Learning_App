import sqlite3
import bcrypt

# Hàm băm mật khẩu
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    conn = sqlite3.connect("chinese_app.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Tạo bảng câu hỏi đánh giá
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CauHoiDanhGia (
        ma_cau_hoi INTEGER PRIMARY KEY AUTOINCREMENT,
        cap_do TEXT NOT NULL,  -- HSK1, HSK2, ...
        cau_hoi TEXT NOT NULL,  -- Nội dung câu hỏi
        dap_an_A TEXT NOT NULL, -- Lựa chọn A
        dap_an_B TEXT NOT NULL, -- Lựa chọn B
        dap_an_C TEXT NOT NULL, -- Lựa chọn C
        dap_an_D TEXT NOT NULL, -- Lựa chọn D
        dap_an_dung TEXT NOT NULL -- Đáp án đúng (A, B, C, D)
    );
    """)
    cursor.execute("SELECT COUNT(*) FROM CauHoiDanhGia;")
    if cursor.fetchone()[0] == 0:
        cau_hoi_mau = [
            ("HSK1", "Từ 吃 có nghĩa là gì?", "tạm biệt", "ăn", "ngủ", "đi", "B"),
            ("HSK1", "Từ 多 có nghĩa là gì?", "ghế", "viết", "nhiều", "bao nhiêu", "C"),
            ("HSK1", "Từ 喜欢 có nghĩa là gì?", "buổi chiều", "thích", "trường học", "chúng ta", "B"),
            ("HSK1", "Từ 做 có nghĩa là gì?", "hôm qua", "làm", "như thế nào", "bệnh viện", "B"),
            ("HSK1", "Từ 谢谢 có nghĩa là gì?", "cảm ơn", "học tập", "xuống", "nghe", "A"),

            ("HSK2", "Từ 穿 có nghĩa là gì?", "hiểu", "dài", "mặc", "xe buýt", "C"),
            ("HSK2", "Từ 欢迎 có nghĩa là gì?", "sân bay", "trứng gà", "hoan nghênh, chào mừng", "anh trai", "C"),
            ("HSK2", "Từ 觉得 có nghĩa là gì?", "cà phê", "cảm thấy", "bắt đầu", "nhanh", "B"),
            ("HSK2", "Từ 慢 có nghĩa là gì?", "bận", "cửa", "chậm", "đàn ông", "C"),
            ("HSK2", "Từ 牛奶 có nghĩa là gì?", "phụ nữ", "sữa bò", "bên cạnh", "chạy bộ", "B"),

            ("HSK3", "Từ 阿姨 có nghĩa là gì?", "dì, cô", "Công nhân", "Học sinh", "áo sơ mi", "A"),
            ("HSK3", "Từ 表演 có nghĩa là gì?", "biểu diễn", "người khác", "siêu thị", "đến trễ", "A"),
            ("HSK3", "Từ 关心 có nghĩa là gì?", "quốc gia", "quan tâm", "quá khứ", "vườn hoa", "B"),
            ("HSK3", "Từ 见面 có nghĩa là gì?", "sợ", "nhận, tiếp", "gặp mặt", "dạy", "C"),
            ("HSK3", "Từ 黄 có nghĩa là gì?", "màu vàng", "luyện tập", "hiểu rõ", "con ngựa", "A"),

            ("HSK4", "Từ 爱情 có nghĩa là gì?", "an toàn", "tình yêu", "bánh bao", "ví dụ như", "B"),
            ("HSK4", "Từ 餐厅 có nghĩa là gì?", "căng tin, nhà ăn", "gần như", "nếm thử", "vượt trên", "A"),
            ("HSK4", "Từ 戴 có nghĩa là gì?", "đeo", "làm", "lúc đó", "hướng dẫn viên du lịch", "A"),
            ("HSK4", "Từ 道歉 có nghĩa là gì?", "bắt đầu", "bỏ cuộc", "xin lỗi", "trì hoãn", "C"),
            ("HSK4", "Từ 儿童 có nghĩa là gì?", "trẻ con", "phát triển", "thư giãn", "phong phú", "A"),

            ("HSK5", "Từ 冰淇淋 có nghĩa là gì?", "thôi thúc", "chạy theo", "cổ", "kem", "D"),
            ("HSK5", "Từ 称呼 có nghĩa là gì?", "từ bỏ", "im lặng", "kiên nhẫn", "xưng hô", "D"),
            ("HSK5", "Từ 胆小鬼 có nghĩa là gì?", "cố gắng", "kẻ nhát gan", "yêu cầu", "địa phương", "B"),
            ("HSK5", "Từ 地震 có nghĩa là gì?", "động đất", "hang động", "đậu phụ", "độc lập", "A"),
            ("HSK5", "Từ 蹲 có nghĩa là gì?", "đánh giá", "ngồi xổm", "dự đoán", "khám phá", "B"),

            ("HSK6", "Từ 昂贵 có nghĩa là gì?", "đắt đỏ", "lồi lõm", "sáng ngời", "toàn cầu", "A"),
            ("HSK6", "Từ 暴力 có nghĩa là gì?", "quan trọng", "bạo lực", "không đáng kể", "thực hiện", "B"),
            ("HSK6", "Từ 蹦 có nghĩa là gì?", "nhảy lên", "lo lắng", "cảm thấy", "mệt mỏi", "A"),
            ("HSK6", "Từ 财务 có nghĩa là gì?", "xem xét", "chạm vào", "phân tích", "tài chính", "D"),
            ("HSK6", "Từ 称心如意 có nghĩa là gì?", "vừa ý, hài lòng", "không quan tâm", "tùy tiện", "chỉ có mục tiêu", "A"),
        ]
        # Chèn dữ liệu mẫu vào bảng
        cursor.executemany("""
        INSERT INTO CauHoiDanhGia (cap_do, cau_hoi, dap_an_A, dap_an_B, dap_an_C, dap_an_D, dap_an_dung)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, cau_hoi_mau)

    # Tạo bảng kết quả đánh giá người dùng
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS KetQuaDanhGia (
        ma_nguoi_dung INTEGER NOT NULL,  -- ID người dùng
        diem_hsk1 REAL DEFAULT 0,        -- Điểm của HSK1
        diem_hsk2 REAL DEFAULT 0,        -- Điểm của HSK2
        diem_hsk3 REAL DEFAULT 0,        -- Điểm của HSK3
        diem_hsk4 REAL DEFAULT 0,        -- Điểm của HSK4
        diem_hsk5 REAL DEFAULT 0,        -- Điểm của HSK5
        diem_hsk6 REAL DEFAULT 0,        -- Điểm của HSK6                       -- Điểm số
        PRIMARY KEY (ma_nguoi_dung),
        FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS NguoiDung (
        ma_nguoi_dung INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_dang_nhap TEXT NOT NULL UNIQUE,
        mat_khau TEXT NOT NULL,
        cap_do_hien_tai TEXT DEFAULT NULL,    -- HSK cấp độ hiện tại của người dùng, ví dụ: 'HSK3'
        da_lam_danh_gia INTEGER DEFAULT 0     -- 0: chưa làm đánh giá năng lực, 1: đã làm
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TuVungHeThong (
    ma_tu_vung INTEGER PRIMARY KEY AUTOINCREMENT,
    cap_do TEXT NOT NULL,         -- HSK1, HSK2, ...
    tu_moi TEXT NOT NULL,
    phien_am TEXT,
    giai_thich TEXT,
    vi_du TEXT,
    phien_am_vi_du TEXT,
    dich TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TuVungNguoiDung (
    ma_nguoi_dung INTEGER NOT NULL,
    ma_tu_vung INTEGER NOT NULL,
    PRIMARY KEY (ma_nguoi_dung, ma_tu_vung),
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE,
    FOREIGN KEY (ma_tu_vung) REFERENCES TuVungHeThong(ma_tu_vung) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SoTayTuVung (
    ma_so_tay INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    cap_do TEXT,
    tu_moi TEXT NOT NULL,
    phien_am TEXT,
    giai_thich TEXT,
    vi_du TEXT,
    phien_am_vi_du TEXT,
    dich TEXT,
    da_hoc INTEGER DEFAULT 0,
    FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung)
    UNIQUE (ma_nguoi_dung, tu_moi, cap_do)
    );
    """)

    # Tạo bảng Mẹo Học
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MeoHoc (
        ma_meo INTEGER PRIMARY KEY AUTOINCREMENT,
        noi_dung TEXT NOT NULL
    );
    """)

    # Chèn dữ liệu mẫu vào bảng Mẹo Học nếu bảng chưa có dữ liệu
    cursor.execute("SELECT COUNT(*) FROM MeoHoc;")
    if cursor.fetchone()[0] == 0:
        meo_hoc_mau = [
            "Mỗi ngày 5 từ – tích tiểu thành đại.",
            "Học từ – phải có ví dụ.",
            "Chữ – Âm – Nghĩa – Ví dụ: đủ combo mới nhớ lâu.",
            "Hán Việt là chìa khóa – đoán nghĩa không cần tra.",
            "Lặp đi lặp lại – bộ não sẽ ghi.",
            "Âm gần giống tiếng Việt – liên tưởng để dễ nhớ.",
            "Từ khó không bỏ – cứ gặp nhiều là quen.",
            "Từ mới là nguyên liệu – hội thoại là món ăn.",
            "Chơi game, xem phim – từ vựng tự chui vào đầu.",
            "Càng sai nhiều – càng nhớ lâu."
        ]

        for meo in meo_hoc_mau:
            cursor.execute("INSERT INTO MeoHoc (noi_dung) VALUES (?);", (meo,))

    # Tạo bảng Tiến Độ Học
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS TienDoHoc (
        ma_tien_do INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_nguoi_dung INTEGER NOT NULL,
        so_tu_da_hoc INTEGER DEFAULT 0,
        tien_do_hsk1 REAL DEFAULT 0,
        tien_do_hsk2 REAL DEFAULT 0,
        tien_do_hsk3 REAL DEFAULT 0,
        tien_do_hsk4 REAL DEFAULT 0,
        tien_do_hsk5 REAL DEFAULT 0,
        tien_do_hsk6 REAL DEFAULT 0,
        FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE
    );
    """)

    # Tạo bảng Phiên Đăng Nhập
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PhienDangNhap (
        ma_phien INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_nguoi_dung INTEGER NOT NULL,
        thoi_gian_dang_nhap TEXT NOT NULL,
        thoi_gian_dang_xuat TEXT,
        tong_thoi_gian_phut INTEGER DEFAULT 0,
        FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ThongKeHSKTheoNgay (
        ma_thong_ke INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_nguoi_dung INTEGER NOT NULL,
        ngay TEXT NOT NULL,  -- định dạng YYYY-MM-DD
        tong_hsk1 INTEGER DEFAULT 0,
        tong_hsk2 INTEGER DEFAULT 0,
        tong_hsk3 INTEGER DEFAULT 0,
        tong_hsk4 INTEGER DEFAULT 0,
        tong_hsk5 INTEGER DEFAULT 0,
        tong_hsk6 INTEGER DEFAULT 0,
        FOREIGN KEY (ma_nguoi_dung) REFERENCES NguoiDung(ma_nguoi_dung) ON DELETE CASCADE
    );
    """)


    conn.commit()
    print("✅ Đã khởi tạo cơ sở dữ liệu và chèn dữ liệu mẫu thành công.")

except sqlite3.Error as e:
    print(f"Lỗi khi tạo cơ sở dữ liệu: {e}")

finally:
    conn.close()