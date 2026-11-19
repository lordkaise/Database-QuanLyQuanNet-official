import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox
)
from database import get_connection


class QuanLyKhachHang(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ KHÁCH HÀNG")
        self.setGeometry(200, 100, 1100, 600)

        self.tao_giao_dien()
        self.hien_thi_danh_sach()

    def tao_giao_dien(self):
        layout = QVBoxLayout()

        title = QLabel("QUẢN LÝ KHÁCH HÀNG")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2457A7;"
        )
        layout.addWidget(title)

        form = QFormLayout()

        self.ma = QLineEdit()
        self.ma.setReadOnly(True)
        self.ma.setPlaceholderText("Mã khách hàng được tự động tạo")

        self.ten = QLineEdit()
        self.sdt = QLineEdit()
        self.loai_tk = QLineEdit()

        self.tong_tien = QLineEdit()
        self.tong_tien.setReadOnly(True)

        self.so_du = QLineEdit()
        self.so_du.setReadOnly(True)

        form.addRow("Mã khách hàng:", self.ma)
        form.addRow("Họ tên:", self.ten)
        form.addRow("Số điện thoại:", self.sdt)
        form.addRow("Loại tài khoản:", self.loai_tk)
        form.addRow("Tổng tiền đã nạp:", self.tong_tien)
        form.addRow("Số dư:", self.so_du)

        layout.addLayout(form)

        buttons = QHBoxLayout()

        self.btn_them = QPushButton("Thêm")
        self.btn_sua = QPushButton("Sửa")
        self.btn_xoa = QPushButton("Xóa")
        self.btn_lam_moi = QPushButton("Làm mới")

        buttons.addWidget(self.btn_them)
        buttons.addWidget(self.btn_sua)
        buttons.addWidget(self.btn_xoa)
        buttons.addWidget(self.btn_lam_moi)

        layout.addLayout(buttons)

        # Tìm kiếm
        search_layout = QHBoxLayout()

        self.tim_kiem = QLineEdit()
        self.tim_kiem.setPlaceholderText(
            "Nhập mã, tên hoặc số điện thoại khách hàng cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")

        search_layout.addWidget(self.tim_kiem)
        search_layout.addWidget(self.btn_tim)

        layout.addLayout(search_layout)

        # Bảng khách hàng
        self.bang = QTableWidget()
        self.bang.setColumnCount(6)

        self.bang.setHorizontalHeaderLabels([
            "Mã khách hàng",
            "Họ tên",
            "Số điện thoại",
            "Loại tài khoản",
            "Tổng tiền đã nạp",
            "Số dư"
        ])

        self.bang.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.bang.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.bang.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.bang)

        self.setLayout(layout)

        # Kết nối sự kiện
        self.btn_them.clicked.connect(self.them_khach_hang)
        self.btn_sua.clicked.connect(self.sua_khach_hang)
        self.btn_xoa.clicked.connect(self.xoa_khach_hang)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_tim.clicked.connect(self.tim_khach_hang)

        self.bang.cellClicked.connect(self.chon_khach_hang)

    # Hiển thị danh sách khách hàng
    def hien_thi_danh_sach(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ID, HoTen, SDT, LoaiTK, TongTienDaNap, SoDu
                FROM KhachHang
                ORDER BY ID DESC
            """)

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Hiển thị dữ liệu lên bảng
    def hien_thi_bang(self, rows):
        self.bang.setRowCount(0)

        for row_data in rows:
            row = self.bang.rowCount()
            self.bang.insertRow(row)

            for col, value in enumerate(row_data):
                if value is None:
                    value = ""

                self.bang.setItem(
                    row, col, QTableWidgetItem(str(value))
                )

    # Tự động tạo mã khách hàng theo dạng KH001, KH002, KH003...
    def tao_ma_khach_hang(self, cursor):
        cursor.execute("""
            SELECT ISNULL(
                MAX(TRY_CONVERT(INT, SUBSTRING(ID, 3, LEN(ID)))),
                0
            )
            FROM KhachHang WITH (UPDLOCK, HOLDLOCK)
            WHERE ID LIKE 'KH[0-9]%'
              AND TRY_CONVERT(
                    INT, SUBSTRING(ID, 3, LEN(ID))
                  ) IS NOT NULL
        """)

        so_lon_nhat = cursor.fetchone()[0] or 0
        return f"KH{int(so_lon_nhat) + 1:03d}"

    # Kiểm tra dữ liệu nhập
    def kiem_tra(self):
        if not self.ten.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập họ tên khách hàng!"
            )
            return False

        sdt = self.sdt.text().strip()

        if not sdt:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập số điện thoại!"
            )
            return False

        if not sdt.isdigit() or len(sdt) > 15:
            QMessageBox.warning(
                self, "Thông báo",
                "Số điện thoại chỉ được chứa chữ số và tối đa 15 số!"
            )
            return False

        return True

    # Thêm khách hàng
    def them_khach_hang(self):
        if not self.kiem_tra():
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Tự động sinh mã khách hàng
            ma_moi = self.tao_ma_khach_hang(cursor)

            cursor.execute("""
                INSERT INTO KhachHang
                (ID, HoTen, SDT, LoaiTK, TongTienDaNap, SoDu)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (
                ma_moi,
                self.ten.text().strip(),
                self.sdt.text().strip(),
                self.loai_tk.text().strip()
            ))

            conn.commit()

            QMessageBox.information(
                self, "Thông báo",
                f"Thêm khách hàng thành công!\nMã khách hàng: {ma_moi}"
            )

            self.lam_moi()

        except Exception as e:
            if conn is not None:
                conn.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

        finally:
            if conn is not None:
                conn.close()

    # Chọn khách hàng trên bảng
    def chon_khach_hang(self, row, col):
        self.ma.setText(self.bang.item(row, 0).text())
        self.ten.setText(self.bang.item(row, 1).text())
        self.sdt.setText(self.bang.item(row, 2).text())
        self.loai_tk.setText(self.bang.item(row, 3).text())
        self.tong_tien.setText(self.bang.item(row, 4).text())
        self.so_du.setText(self.bang.item(row, 5).text())

    # Sửa khách hàng
    def sua_khach_hang(self):
        if not self.ma.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn khách hàng cần sửa!"
            )
            return

        if not self.kiem_tra():
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE KhachHang
                SET HoTen = ?, SDT = ?, LoaiTK = ?
                WHERE ID = ?
            """, (
                self.ten.text().strip(),
                self.sdt.text().strip(),
                self.loai_tk.text().strip(),
                self.ma.text().strip()
            ))

            conn.commit()

            QMessageBox.information(
                self, "Thông báo", "Cập nhật thành công!"
            )

            self.lam_moi()

        except Exception as e:
            if conn is not None:
                conn.rollback()
            QMessageBox.critical(self, "Lỗi", str(e))

        finally:
            if conn is not None:
                conn.close()

    # Xóa khách hàng
    def xoa_khach_hang(self):
        ma = self.ma.text().strip()

        if not ma:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn khách hàng cần xóa!"
            )
            return

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xóa khách hàng này?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.No:
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM KhachHang WHERE ID = ?", (ma,)
            )

            conn.commit()

            QMessageBox.information(
                self, "Thông báo", "Xóa khách hàng thành công!"
            )

            self.lam_moi()

        except Exception as e:
            if conn is not None:
                conn.rollback()
            QMessageBox.critical(
                self, "Không thể xóa",
                "Khách hàng có thể đã phát sinh giao dịch, "
                "phiên sử dụng hoặc hóa đơn.\n" + str(e)
            )

        finally:
            if conn is not None:
                conn.close()

    # Tìm kiếm theo mã, tên hoặc số điện thoại
    def tim_khach_hang(self):
        tu_khoa = self.tim_kiem.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT ID, HoTen, SDT, LoaiTK, TongTienDaNap, SoDu
                FROM KhachHang
                WHERE ID LIKE ?
                   OR HoTen LIKE ?
                   OR SDT LIKE ?
                ORDER BY ID DESC
            """, (
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            ))

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Làm mới form
    def lam_moi(self):
        self.ma.clear()
        self.ma.setReadOnly(True)
        self.ma.setPlaceholderText(
            "Mã khách hàng được tự động tạo"
        )

        self.ten.clear()
        self.sdt.clear()
        self.loai_tk.clear()
        self.tong_tien.clear()
        self.so_du.clear()
        self.tim_kiem.clear()

        self.hien_thi_danh_sach()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuanLyKhachHang()
    window.show()

    sys.exit(app.exec())
