
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox
)
from database import get_connection


class QuanLyDichVu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ DỊCH VỤ")
        self.setGeometry(200, 100, 900, 600)

        self.tao_giao_dien()
        self.hien_thi_danh_sach()

    def tao_giao_dien(self):
        layout = QVBoxLayout()

        title = QLabel("QUẢN LÝ DỊCH VỤ")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2457A7;"
        )
        layout.addWidget(title)

        form = QFormLayout()

        self.ma = QLineEdit()
        self.ten = QLineEdit()
        self.phan_loai = QLineEdit()
        self.gia = QLineEdit()
        self.so_luong = QLineEdit()

        form.addRow("Mã dịch vụ:", self.ma)
        form.addRow("Tên dịch vụ:", self.ten)
        form.addRow("Phân loại:", self.phan_loai)
        form.addRow("Giá tiền:", self.gia)
        form.addRow("Số lượng:", self.so_luong)

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

        search_layout = QHBoxLayout()

        self.tim_kiem = QLineEdit()
        self.tim_kiem.setPlaceholderText(
            "Nhập mã hoặc tên dịch vụ cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")

        search_layout.addWidget(self.tim_kiem)
        search_layout.addWidget(self.btn_tim)

        layout.addLayout(search_layout)

        self.bang = QTableWidget()
        self.bang.setColumnCount(5)

        self.bang.setHorizontalHeaderLabels([
            "Mã dịch vụ", "Tên dịch vụ",
            "Phân loại", "Giá tiền", "Số lượng"
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

        self.btn_them.clicked.connect(self.them_dich_vu)
        self.btn_sua.clicked.connect(self.sua_dich_vu)
        self.btn_xoa.clicked.connect(self.xoa_dich_vu)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_tim.clicked.connect(self.tim_dich_vu)

        self.bang.cellClicked.connect(self.chon_dich_vu)

    # Hiển thị danh sách dịch vụ
    def hien_thi_danh_sach(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaDV, TenDV, PhanLoai, GiaTien, SoLuong
                FROM DichVu
                ORDER BY MaDV DESC
            """)

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Đổ dữ liệu lên bảng
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

    # Kiểm tra dữ liệu nhập
    def kiem_tra(self):
        if not self.ma.text().strip() or not self.ten.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập mã và tên dịch vụ!"
            )
            return None

        try:
            gia = float(self.gia.text())
            so_luong = int(self.so_luong.text())

            if gia < 0 or so_luong < 0:
                raise ValueError

            return gia, so_luong

        except ValueError:
            QMessageBox.warning(
                self, "Lỗi",
                "Giá tiền phải là số không âm và số lượng phải là số nguyên không âm!"
            )
            return None

    # Thêm dịch vụ
    def them_dich_vu(self):
        data = self.kiem_tra()

        if data is None:
            return

        gia, so_luong = data

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO DichVu
                (MaDV, TenDV, PhanLoai, GiaTien, SoLuong)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.ma.text().strip(),
                self.ten.text().strip(),
                self.phan_loai.text(),
                gia,
                so_luong
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Thêm dịch vụ thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Chọn dịch vụ trên bảng
    def chon_dich_vu(self, row, col):
        self.ma.setText(self.bang.item(row, 0).text())
        self.ten.setText(self.bang.item(row, 1).text())
        self.phan_loai.setText(self.bang.item(row, 2).text())
        self.gia.setText(self.bang.item(row, 3).text())
        self.so_luong.setText(self.bang.item(row, 4).text())

        self.ma.setReadOnly(True)

    # Sửa dịch vụ
    def sua_dich_vu(self):
        if not self.ma.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn dịch vụ cần sửa!"
            )
            return

        data = self.kiem_tra()

        if data is None:
            return

        gia, so_luong = data

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE DichVu
                SET TenDV = ?, PhanLoai = ?,
                    GiaTien = ?, SoLuong = ?
                WHERE MaDV = ?
            """, (
                self.ten.text().strip(),
                self.phan_loai.text(),
                gia,
                so_luong,
                self.ma.text().strip()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Cập nhật thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Xóa dịch vụ
    def xoa_dich_vu(self):
        ma = self.ma.text().strip()

        if not ma:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn dịch vụ cần xóa!"
            )
            return

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xóa dịch vụ này?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.No:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM DichVu WHERE MaDV = ?", (ma,)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Xóa dịch vụ thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(
                self, "Không thể xóa",
                "Dịch vụ có thể đã xuất hiện trong hóa đơn.\n" + str(e)
            )

    # Tìm kiếm dịch vụ
    def tim_dich_vu(self):
        tu_khoa = self.tim_kiem.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaDV, TenDV, PhanLoai, GiaTien, SoLuong
                FROM DichVu
                WHERE MaDV LIKE ? OR TenDV LIKE ? OR Phanloai LIKE ?
                ORDER BY MaDV DESC
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
        self.ma.setReadOnly(False)

        self.ten.clear()
        self.phan_loai.clear()
        self.gia.clear()
        self.so_luong.clear()
        self.tim_kiem.clear()

        self.hien_thi_danh_sach()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuanLyDichVu()
    window.show()

    sys.exit(app.exec())
