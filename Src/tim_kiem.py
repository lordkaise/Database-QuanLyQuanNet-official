#Giáp đẹp trai vcl
from PyQt6.QtWidgets import *
from database import get_connection


class TimKiem(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tìm kiếm thông tin")
        self.resize(1100, 650)

        layout = QVBoxLayout()

        title = QLabel("TÌM KIẾM THÔNG TIN")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        # Khu vực tìm kiếm
        tim_layout = QHBoxLayout()

        self.loai = QComboBox()
        self.loai.addItems([
            "Tất cả",
            "Khách hàng",
            "Nhân viên",
            "Dịch vụ",
            "Khu vực máy",
            "Máy tính",
            "Hóa đơn",
            "Phiên sử dụng",
            "Giao dịch nạp tiền"
        ])

        self.tu_khoa = QLineEdit()
        self.tu_khoa.setPlaceholderText(
            "Nhập mã hoặc thông tin cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")
        self.btn_tim.clicked.connect(self.tim_kiem)

        self.btn_xoa = QPushButton("Xóa")
        self.btn_xoa.clicked.connect(self.xoa)

        tim_layout.addWidget(QLabel("Loại dữ liệu:"))
        tim_layout.addWidget(self.loai)
        tim_layout.addWidget(self.tu_khoa)
        tim_layout.addWidget(self.btn_tim)
        tim_layout.addWidget(self.btn_xoa)

        layout.addLayout(tim_layout)

        # Bảng kết quả
        self.bang = QTableWidget()
        self.bang.setColumnCount(5)

        self.bang.setHorizontalHeaderLabels([
            "Loại dữ liệu",
            "Mã",
            "Thông tin",
            "thông tin bổ sung",
            "Giá trị / Thời điểm"
        ])

        self.bang.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.bang.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.bang)

        self.ket_qua = QLabel("Chưa có kết quả tìm kiếm")
        layout.addWidget(self.ket_qua)

        self.setLayout(layout)

        self.tu_khoa.returnPressed.connect(self.tim_kiem)

    # Xóa kết quả
    def xoa(self):
        self.tu_khoa.clear()
        self.bang.setRowCount(0)
        self.ket_qua.setText("Chưa có kết quả tìm kiếm")

    # Tìm kiếm
    def tim_kiem(self):
        tu_khoa = self.tu_khoa.text().strip()

        if not tu_khoa:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập từ khóa tìm kiếm!"
            )
            return

        tu_khoa = "%" + tu_khoa + "%"

        truy_van = {
            "Khách hàng": """
                SELECT
                    N'Khách hàng',
                    ID,
                    HoTen,
                    SDT,
                    CAST(SoDu AS NVARCHAR(50))
                FROM KhachHang
                WHERE ID LIKE ? OR HoTen LIKE ?
                    OR SDT LIKE ? OR LoaiTK LIKE ?
            """,

            "Nhân viên": """
                SELECT
                    N'Nhân viên',
                    MaNV,
                    TenNV,
                    ChucVu,
                    SDT
                FROM NhanVien
                WHERE MaNV LIKE ? OR TenNV LIKE ?
                   OR ChucVu LIKE ? OR SDT LIKE ?
            """,

            "Dịch vụ": """
                SELECT
                    N'Dịch vụ',
                    MaDV,
                    TenDV,
                    PhanLoai,
                    CAST(GiaTien AS NVARCHAR(50))
                FROM DichVu
                WHERE MaDV LIKE ? OR TenDV LIKE ?
                   OR PhanLoai LIKE ?
            """,

            "Khu vực máy": """
                SELECT
                    N'Khu vực máy',
                    MaKV,
                    TenKhuVuc,
                    CauHinh,
                    CAST(GiaTienGio AS NVARCHAR(50))
                FROM KhuVucMay
                WHERE MaKV LIKE ? OR TenKhuVuc LIKE ?
                   OR CauHinh LIKE ?
            """,

            "Máy tính": """
                SELECT
                    N'Máy tính',
                    mt.MaMT,
                    kv.TenKhuVuc,
                    mt.TrangThai,
                    kv.CauHinh
                FROM MayTinh mt
                JOIN KhuVucMay kv ON mt.MaKV = kv.MaKV
                WHERE mt.MaMT LIKE ? OR kv.TenKhuVuc LIKE ?
                   OR mt.TrangThai LIKE ?
            """,

            "Hóa đơn": """
                SELECT
                    N'Hóa đơn',
                    hd.MaHD,
                    kh.HoTen,
                    hd.TrangThaiThanhToan,
                    CAST(hd.TongTien AS NVARCHAR(50))
                FROM HoaDon hd
                JOIN KhachHang kh ON hd.ID = kh.ID
                WHERE hd.MaHD LIKE ? OR hd.ID LIKE ?
                   OR kh.HoTen LIKE ?
                   OR hd.TrangThaiThanhToan LIKE ?
            """,

            "Phiên sử dụng": """
                SELECT
                    N'Phiên sử dụng',
                    MaPhien,
                    ID,
                    MaMT,
                    CONVERT(NVARCHAR(30), ThoiGianBatDau, 120)
                FROM PhienSuDung
                WHERE MaPhien LIKE ? OR ID LIKE ?
                   OR MaMT LIKE ?
            """,

            "Giao dịch nạp tiền": """
                SELECT
                    N'Giao dịch nạp tiền',
                    gd.MaGiaoDich,
                    kh.HoTen,
                    nv.TenNV,
                    CAST(gd.SoTienNap AS NVARCHAR(50))
                FROM GiaoDichNapTien gd
                JOIN KhachHang kh ON gd.ID = kh.ID
                JOIN NhanVien nv ON gd.MaNV = nv.MaNV
                WHERE gd.MaGiaoDich LIKE ? OR gd.ID LIKE ?
                   OR kh.HoTen LIKE ? OR nv.TenNV LIKE ?
            """
        }

        conn = get_connection()
        cursor = conn.cursor()

        try:
            ket_qua = []

            if self.loai.currentText() == "Tất cả":
                for ten_loai, sql in truy_van.items():
                    so_tham_so = sql.count("?")

                    cursor.execute(
                        sql,
                        *([tu_khoa] * so_tham_so)
                    )

                    ket_qua.extend(cursor.fetchall())

            else:
                ten_loai = self.loai.currentText()
                sql = truy_van[ten_loai]

                so_tham_so = sql.count("?")

                cursor.execute(
                    sql,
                    *([tu_khoa] * so_tham_so)
                )

                ket_qua = cursor.fetchall()

            self.bang.setRowCount(len(ket_qua))

            for i, row in enumerate(ket_qua):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(
                        "" if value is None else str(value)
                    )

                    self.bang.setItem(i, j, item)

            self.bang.resizeColumnsToContents()

            self.ket_qua.setText(
                f"Tìm thấy {len(ket_qua)} kết quả"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()
            

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TimKiem()
    window.show()
    sys.exit(app.exec())
