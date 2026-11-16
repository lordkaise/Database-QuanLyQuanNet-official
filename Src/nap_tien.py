
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDateTime, Qt
from database import get_connection


class NapTien(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý giao dịch nạp tiền")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        # Form nhập thông tin
        form = QFormLayout()

        self.ma = QLineEdit()

        # Chọn khách hàng có chức năng tìm kiếm
        self.khach_hang = QComboBox()
        self.khach_hang.setEditable(True)
        self.khach_hang.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )
        self.khach_hang.setPlaceholderText(
            "Nhập mã hoặc tên khách hàng..."
        )

        # Chọn nhân viên có chức năng tìm kiếm
        self.nhan_vien = QComboBox()
        self.nhan_vien.setEditable(True)
        self.nhan_vien.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )
        self.nhan_vien.setPlaceholderText(
            "Nhập mã hoặc tên nhân viên..."
        )

        self.so_tien = QLineEdit()

        self.thoi_diem = QDateTimeEdit()
        self.thoi_diem.setDateTime(
            QDateTime.currentDateTime()
        )
        self.thoi_diem.setCalendarPopup(True)
        self.thoi_diem.setDisplayFormat(
            "dd/MM/yyyy HH:mm:ss"
        )

        form.addRow("Mã giao dịch:", self.ma)
        form.addRow("Khách hàng:", self.khach_hang)
        form.addRow("Nhân viên:", self.nhan_vien)
        form.addRow("Số tiền nạp:", self.so_tien)
        form.addRow("Thời điểm nạp:", self.thoi_diem)

        layout.addLayout(form)

        # Các nút chức năng
        btn_layout = QHBoxLayout()

        self.btn_them = QPushButton("Nạp tiền")
        self.btn_them.clicked.connect(self.them)

        self.btn_tim = QPushButton("Tìm kiếm")
        self.btn_tim.clicked.connect(self.tim_kiem)

        self.btn_tai_lai = QPushButton("Tải lại")
        self.btn_tai_lai.clicked.connect(self.tai_du_lieu)

        btn_layout.addWidget(self.btn_them)
        btn_layout.addWidget(self.btn_tim)
        btn_layout.addWidget(self.btn_tai_lai)

        layout.addLayout(btn_layout)

        # Bảng lịch sử giao dịch
        self.bang = QTableWidget()
        layout.addWidget(self.bang)

        self.setLayout(layout)

        self.tai_combo_box()
        self.tai_du_lieu()

    # Tải danh sách khách hàng và nhân viên
    def tai_combo_box(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT ID, HoTen
                FROM KhachHang
                ORDER BY ID
            """)

            for id_kh, hoten in cursor.fetchall():
                self.khach_hang.addItem(
                    f"{id_kh} - {hoten}", id_kh
                )

            cursor.execute("""
                SELECT MaNV, TenNV
                FROM NhanVien
                ORDER BY MaNV
            """)

            for ma_nv, ten_nv in cursor.fetchall():
                self.nhan_vien.addItem(
                    f"{ma_nv} - {ten_nv}", ma_nv
                )

            # Tìm kiếm không phân biệt chữ hoa, chữ thường
            completer_kh = QCompleter(
                self.khach_hang.model(), self
            )
            completer_kh.setFilterMode(
                Qt.MatchFlag.MatchContains
            )
            completer_kh.setCaseSensitivity(
                Qt.CaseSensitivity.CaseInsensitive
            )
            completer_kh.setCompletionMode(
                QCompleter.CompletionMode.PopupCompletion
            )
            self.khach_hang.setCompleter(completer_kh)

            completer_nv = QCompleter(
                self.nhan_vien.model(), self
            )
            completer_nv.setFilterMode(
                Qt.MatchFlag.MatchContains
            )
            completer_nv.setCaseSensitivity(
                Qt.CaseSensitivity.CaseInsensitive
            )
            completer_nv.setCompletionMode(
                QCompleter.CompletionMode.PopupCompletion
            )
            self.nhan_vien.setCompleter(completer_nv)

        finally:
            conn.close()

    # Lấy mã khách hàng hoặc nhân viên đã chọn
    def lay_ma_da_chon(self, combo):
        index = combo.currentIndex()

        if index < 0:
            return None

        if combo.currentText() != combo.itemText(index):
            return None

        return combo.currentData()

    # Hiển thị lịch sử giao dịch
    def tai_du_lieu(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    gd.MaGiaoDich,
                    kh.ID,
                    kh.HoTen,
                    nv.MaNV,
                    nv.TenNV,
                    gd.SoTienNap,
                    gd.ThoiDiemNap
                FROM GiaoDichNapTien gd
                JOIN KhachHang kh ON gd.ID = kh.ID
                JOIN NhanVien nv ON gd.MaNV = nv.MaNV
                ORDER BY gd.ThoiDiemNap DESC
            """)

            rows = cursor.fetchall()

            self.hien_thi_bang(rows)

        finally:
            conn.close()

    # Hiển thị dữ liệu lên bảng
    def hien_thi_bang(self, rows):
        self.bang.setColumnCount(7)

        self.bang.setHorizontalHeaderLabels([
            "Mã giao dịch",
            "Mã khách hàng",
            "Tên khách hàng",
            "Mã nhân viên",
            "Tên nhân viên",
            "Số tiền nạp",
            "Thời điểm nạp"
        ])

        self.bang.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.bang.setItem(
                    i, j, QTableWidgetItem(str(value))
                )

        self.bang.resizeColumnsToContents()

    # Thêm giao dịch nạp tiền
    def them(self):
        ma = self.ma.text().strip()
        id_kh = self.lay_ma_da_chon(self.khach_hang)
        ma_nv = self.lay_ma_da_chon(self.nhan_vien)

        if not ma:
            QMessageBox.warning(
                self, "Lỗi", "Chưa nhập mã giao dịch!"
            )
            return

        if id_kh is None:
            QMessageBox.warning(
                self, "Lỗi",
                "Vui lòng chọn khách hàng từ danh sách gợi ý!"
            )
            return

        if ma_nv is None:
            QMessageBox.warning(
                self, "Lỗi",
                "Vui lòng chọn nhân viên từ danh sách gợi ý!"
            )
            return

        try:
            so_tien = float(self.so_tien.text())

            if so_tien <= 0:
                QMessageBox.warning(
                    self, "Lỗi",
                    "Số tiền nạp phải lớn hơn 0!"
                )
                return

            thoi_diem = self.thoi_diem.dateTime().toPyDateTime()

            conn = get_connection()
            cursor = conn.cursor()

            try:
                # Thêm giao dịch nạp tiền
                cursor.execute("""
                    INSERT INTO GiaoDichNapTien
                    (MaGiaoDich, ID, MaNV, ThoiDiemNap, SoTienNap)
                    VALUES (?, ?, ?, ?, ?)
                """, ma, id_kh, ma_nv, thoi_diem, so_tien)

                # Cập nhật tổng tiền đã nạp và số dư
                cursor.execute("""
                    UPDATE KhachHang
                    SET TongTienDaNap =
                            ISNULL(TongTienDaNap, 0) + ?,
                        SoDu = ISNULL(SoDu, 0) + ?
                    WHERE ID = ?
                """, so_tien, so_tien, id_kh)

                conn.commit()

            except Exception:
                conn.rollback()
                raise

            finally:
                conn.close()

            QMessageBox.information(
                self, "Thông báo",
                "Nạp tiền thành công!"
            )

            self.ma.clear()
            self.so_tien.clear()
            self.thoi_diem.setDateTime(
                QDateTime.currentDateTime()
            )

            self.tai_du_lieu()

        except ValueError:
            QMessageBox.warning(
                self, "Lỗi", "Số tiền không hợp lệ!"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

    # Tìm kiếm giao dịch
    # Tìm kiếm giao dịch
    def tim_kiem(self):
        tu_khoa = self.ma.text().strip()

        if not tu_khoa:
            self.tai_du_lieu()
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    gd.MaGiaoDich,
                    kh.ID,
                    kh.HoTen,
                    nv.MaNV,
                    nv.TenNV,
                    gd.SoTienNap,
                    gd.ThoiDiemNap
                FROM GiaoDichNapTien gd
                JOIN KhachHang kh ON gd.ID = kh.ID
                JOIN NhanVien nv ON gd.MaNV = nv.MaNV
                WHERE gd.MaGiaoDich LIKE ?
                OR kh.ID LIKE ?
                OR kh.HoTen LIKE ?
                OR nv.MaNV LIKE ?
                OR nv.TenNV LIKE ?
                ORDER BY gd.ThoiDiemNap DESC
            """,
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            )

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

        finally:
            conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NapTien()
    window.show()
    sys.exit(app.exec())
