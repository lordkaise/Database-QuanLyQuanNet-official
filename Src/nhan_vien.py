
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QComboBox, QDateEdit
)
from PyQt6.QtCore import QDate
from database import get_connection


class QuanLyNhanVien(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ NHÂN VIÊN")
        self.setGeometry(200, 100, 1100, 650)

        self.tao_giao_dien()
        self.hien_thi_danh_sach()

    def tao_giao_dien(self):
        layout = QVBoxLayout()

        # Tiêu đề
        title = QLabel("QUẢN LÝ NHÂN VIÊN")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2457A7;"
        )
        layout.addWidget(title)

        # Form nhập thông tin
        form = QFormLayout()

        self.ma = QLineEdit()
        self.ten = QLineEdit()
        self.ngay_sinh = QDateEdit()
        self.ngay_sinh.setCalendarPopup(True)
        self.ngay_sinh.setDisplayFormat("dd/MM/yyyy")
        self.ngay_sinh.setDate(QDate.currentDate())

        self.dia_chi = QLineEdit()

        self.gioi_tinh = QComboBox()
        self.gioi_tinh.addItems(["Nam", "Nữ"])

        self.luong = QLineEdit()
        self.chuc_vu = QLineEdit()
        self.sdt = QLineEdit()

        form.addRow("Mã nhân viên:", self.ma)
        form.addRow("Tên nhân viên:", self.ten)
        form.addRow("Ngày sinh:", self.ngay_sinh)
        form.addRow("Địa chỉ:", self.dia_chi)
        form.addRow("Giới tính:", self.gioi_tinh)
        form.addRow("Mức lương:", self.luong)
        form.addRow("Chức vụ:", self.chuc_vu)
        form.addRow("Số điện thoại:", self.sdt)

        layout.addLayout(form)

        # Các nút chức năng
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
            "Nhập mã hoặc tên nhân viên cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")

        search_layout.addWidget(self.tim_kiem)
        search_layout.addWidget(self.btn_tim)

        layout.addLayout(search_layout)

        # Bảng dữ liệu
        self.bang = QTableWidget()
        self.bang.setColumnCount(8)

        self.bang.setHorizontalHeaderLabels([
            "Mã NV", "Tên nhân viên", "Ngày sinh",
            "Địa chỉ", "Giới tính", "Mức lương",
            "Chức vụ", "Số điện thoại"
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

        # Gắn sự kiện
        self.btn_them.clicked.connect(self.them_nhan_vien)
        self.btn_sua.clicked.connect(self.sua_nhan_vien)
        self.btn_xoa.clicked.connect(self.xoa_nhan_vien)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_tim.clicked.connect(self.tim_nhan_vien)

        self.bang.cellClicked.connect(self.chon_nhan_vien)

    # Hiển thị danh sách nhân viên
    def hien_thi_danh_sach(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaNV, TenNV, NgaySinh, DiaChi,
                       GioiTinh, MucLuong, ChucVu, SDT
                FROM NhanVien
                ORDER BY MaNV
            """)

            rows = cursor.fetchall()

            self.bang.setRowCount(0)

            for row_data in rows:
                row = self.bang.rowCount()
                self.bang.insertRow(row)

                for col, value in enumerate(row_data):
                    if value is None:
                        value = ""
                    elif col == 2:
                        value = value.strftime("%d/%m/%Y")
                    elif col == 5:
                        value = str(value)

                    self.bang.setItem(
                        row, col, QTableWidgetItem(str(value))
                    )

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Thêm nhân viên
    def them_nhan_vien(self):
        try:
            if not self.ma.text().strip() or not self.ten.text().strip():
                QMessageBox.warning(
                    self, "Thông báo",
                    "Vui lòng nhập mã và tên nhân viên!"
                )
                return

            if not self.luong.text().strip():
                QMessageBox.warning(
                    self, "Thông báo",
                    "Vui lòng nhập mức lương!"
                )
                return

            luong = float(self.luong.text())

            if luong < 0:
                QMessageBox.warning(
                    self, "Thông báo",
                    "Mức lương không được âm!"
                )
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO NhanVien
                (MaNV, TenNV, NgaySinh, DiaChi,
                 GioiTinh, MucLuong, ChucVu, SDT)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.ma.text().strip(),
                self.ten.text().strip(),
                self.ngay_sinh.date().toPyDate(),
                self.dia_chi.text(),
                self.gioi_tinh.currentText(),
                luong,
                self.chuc_vu.text(),
                self.sdt.text()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Thêm nhân viên thành công!"
            )

            self.lam_moi()

        except ValueError:
            QMessageBox.warning(
                self, "Lỗi", "Mức lương phải là số!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Chọn nhân viên từ bảng
    def chon_nhan_vien(self, row, col):
        self.ma.setText(self.bang.item(row, 0).text())
        self.ten.setText(self.bang.item(row, 1).text())

        ngay = self.bang.item(row, 2).text()
        if ngay:
            self.ngay_sinh.setDate(
                QDate.fromString(ngay, "dd/MM/yyyy")
            )

        self.dia_chi.setText(self.bang.item(row, 3).text())

        gioi_tinh = self.bang.item(row, 4).text()
        self.gioi_tinh.setCurrentText(gioi_tinh)

        self.luong.setText(self.bang.item(row, 5).text())
        self.chuc_vu.setText(self.bang.item(row, 6).text())
        self.sdt.setText(self.bang.item(row, 7).text())

        self.ma.setReadOnly(True)

    # Sửa nhân viên
    def sua_nhan_vien(self):
        try:
            if not self.ma.text().strip():
                QMessageBox.warning(
                    self, "Thông báo",
                    "Vui lòng chọn nhân viên cần sửa!"
                )
                return

            luong = float(self.luong.text())

            if luong < 0:
                QMessageBox.warning(
                    self, "Thông báo",
                    "Mức lương không được âm!"
                )
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE NhanVien
                SET TenNV = ?, NgaySinh = ?, DiaChi = ?,
                    GioiTinh = ?, MucLuong = ?, ChucVu = ?, SDT = ?
                WHERE MaNV = ?
            """, (
                self.ten.text(),
                self.ngay_sinh.date().toPyDate(),
                self.dia_chi.text(),
                self.gioi_tinh.currentText(),
                luong,
                self.chuc_vu.text(),
                self.sdt.text(),
                self.ma.text()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Cập nhật thành công!"
            )

            self.lam_moi()

        except ValueError:
            QMessageBox.warning(
                self, "Lỗi", "Mức lương phải là số!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Xóa nhân viên
    def xoa_nhan_vien(self):
        ma = self.ma.text().strip()

        if not ma:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn nhân viên cần xóa!"
            )
            return

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xóa nhân viên này?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.No:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM NhanVien WHERE MaNV = ?", (ma,)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Xóa nhân viên thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(
                self, "Không thể xóa",
                "Nhân viên có thể đang được sử dụng trong dữ liệu khác.\n"
                + str(e)
            )

    # Tìm kiếm nhân viên
    def tim_nhan_vien(self):
        tu_khoa = self.tim_kiem.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaNV, TenNV, NgaySinh, DiaChi,
                       GioiTinh, MucLuong, ChucVu, SDT
                FROM NhanVien
                WHERE MaNV LIKE ? OR TenNV LIKE ?
                ORDER BY MaNV
            """, (
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            ))

            rows = cursor.fetchall()
            self.bang.setRowCount(0)

            for row_data in rows:
                row = self.bang.rowCount()
                self.bang.insertRow(row)

                for col, value in enumerate(row_data):
                    if value is None:
                        value = ""
                    elif col == 2:
                        value = value.strftime("%d/%m/%Y")

                    self.bang.setItem(
                        row, col, QTableWidgetItem(str(value))
                    )

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Làm mới form
    def lam_moi(self):
        self.ma.clear()
        self.ma.setReadOnly(False)

        self.ten.clear()
        self.ngay_sinh.setDate(QDate.currentDate())
        self.dia_chi.clear()
        self.gioi_tinh.setCurrentIndex(0)
        self.luong.clear()
        self.chuc_vu.clear()
        self.sdt.clear()
        self.tim_kiem.clear()

        self.hien_thi_danh_sach()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuanLyNhanVien()
    window.show()

    sys.exit(app.exec())
