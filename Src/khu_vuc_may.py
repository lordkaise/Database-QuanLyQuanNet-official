
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox
)
from database import get_connection


class QuanLyKhuVuc(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ KHU VỰC MÁY")
        self.setGeometry(200, 100, 900, 550)

        self.tao_giao_dien()
        self.hien_thi_danh_sach()

    def tao_giao_dien(self):
        layout = QVBoxLayout()

        title = QLabel("QUẢN LÝ KHU VỰC MÁY")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2457A7;"
        )
        layout.addWidget(title)

        form = QFormLayout()

        self.ma = QLineEdit()
        self.ten = QLineEdit()
        self.cau_hinh = QLineEdit()
        self.gia = QLineEdit()

        form.addRow("Mã khu vực:", self.ma)
        form.addRow("Tên khu vực:", self.ten)
        form.addRow("Cấu hình:", self.cau_hinh)
        form.addRow("Giá tiền/giờ:", self.gia)

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
            "Nhập mã hoặc tên khu vực cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")

        search_layout.addWidget(self.tim_kiem)
        search_layout.addWidget(self.btn_tim)

        layout.addLayout(search_layout)

        self.bang = QTableWidget()
        self.bang.setColumnCount(4)

        self.bang.setHorizontalHeaderLabels([
            "Mã khu vực", "Tên khu vực",
            "Cấu hình", "Giá tiền/giờ"
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

        self.btn_them.clicked.connect(self.them_khu_vuc)
        self.btn_sua.clicked.connect(self.sua_khu_vuc)
        self.btn_xoa.clicked.connect(self.xoa_khu_vuc)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_tim.clicked.connect(self.tim_khu_vuc)

        self.bang.cellClicked.connect(self.chon_khu_vuc)

    # Hiển thị danh sách khu vực
    def hien_thi_danh_sach(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaKV, TenKhuVuc, CauHinh, GiaTienGio
                FROM KhuVucMay
                ORDER BY MaKV
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

    # Kiểm tra dữ liệu
    def kiem_tra(self):
        if not self.ma.text().strip() or not self.ten.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập mã và tên khu vực!"
            )
            return None

        try:
            gia = float(self.gia.text())

            if gia < 0:
                raise ValueError

            return gia

        except ValueError:
            QMessageBox.warning(
                self, "Lỗi",
                "Giá tiền phải là số không âm!"
            )
            return None

    # Thêm khu vực
    def them_khu_vuc(self):
        gia = self.kiem_tra()

        if gia is None:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO KhuVucMay
                (MaKV, TenKhuVuc, CauHinh, GiaTienGio)
                VALUES (?, ?, ?, ?)
            """, (
                self.ma.text().strip(),
                self.ten.text().strip(),
                self.cau_hinh.text(),
                gia
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Thêm khu vực thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Chọn khu vực trên bảng
    def chon_khu_vuc(self, row, col):
        self.ma.setText(self.bang.item(row, 0).text())
        self.ten.setText(self.bang.item(row, 1).text())
        self.cau_hinh.setText(self.bang.item(row, 2).text())
        self.gia.setText(self.bang.item(row, 3).text())

        self.ma.setReadOnly(True)

    # Sửa khu vực
    def sua_khu_vuc(self):
        if not self.ma.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn khu vực cần sửa!"
            )
            return

        gia = self.kiem_tra()

        if gia is None:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE KhuVucMay
                SET TenKhuVuc = ?, CauHinh = ?, GiaTienGio = ?
                WHERE MaKV = ?
            """, (
                self.ten.text().strip(),
                self.cau_hinh.text(),
                gia,
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

    # Xóa khu vực
    def xoa_khu_vuc(self):
        ma = self.ma.text().strip()

        if not ma:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn khu vực cần xóa!"
            )
            return

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xóa khu vực này?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.No:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM KhuVucMay WHERE MaKV = ?", (ma,)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Xóa khu vực thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(
                self, "Không thể xóa",
                "Khu vực có thể đang được sử dụng bởi máy tính.\n"
                + str(e)
            )

    # Tìm kiếm khu vực
    def tim_khu_vuc(self):
        tu_khoa = self.tim_kiem.text().strip()

        try:
            #Giáp đẹp trai vcl
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaKV, TenKhuVuc, CauHinh, GiaTienGio
                FROM KhuVucMay
                WHERE MaKV LIKE ? OR TenKhuVuc LIKE ?
                ORDER BY MaKV
            """, (
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            ))

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Làm mới
    def lam_moi(self):
        self.ma.clear()
        self.ma.setReadOnly(False)

        self.ten.clear()
        self.cau_hinh.clear()
        self.gia.clear()
        self.tim_kiem.clear()

        self.hien_thi_danh_sach()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuanLyKhuVuc()
    window.show()

    sys.exit(app.exec())
