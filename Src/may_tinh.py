
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QComboBox
)
from database import get_connection


class QuanLyMayTinh(QWidget):
    # Tải lại dữ liệu máy tính
    def tai_lai(self):
        self.hien_thi_danh_sach()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ MÁY TÍNH")
        self.setGeometry(200, 100, 900, 550)

        self.tao_giao_dien()
        self.tai_khu_vuc()
        self.hien_thi_danh_sach()

    def tao_giao_dien(self):
        layout = QVBoxLayout()

        title = QLabel("QUẢN LÝ MÁY TÍNH")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2457A7;"
        )
        layout.addWidget(title)

        form = QFormLayout()

        self.ma = QLineEdit()

        self.khu_vuc = QComboBox()

        self.trang_thai = QComboBox()
        self.trang_thai.addItems([
            "Trong", "Dang su dung", "bao tri"
        ])

        form.addRow("Mã máy tính:", self.ma)
        form.addRow("Khu vực:", self.khu_vuc)
        form.addRow("Trạng thái:", self.trang_thai)

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
            "Nhập mã máy tính cần tìm..."
        )

        self.btn_tim = QPushButton("Tìm kiếm")

        search_layout.addWidget(self.tim_kiem)
        search_layout.addWidget(self.btn_tim)

        layout.addLayout(search_layout)

        self.bang = QTableWidget()
        self.bang.setColumnCount(3)

        self.bang.setHorizontalHeaderLabels([
            "Mã máy tính", "Khu vực", "Trạng thái"
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

        self.btn_them.clicked.connect(self.them_may)
        self.btn_sua.clicked.connect(self.sua_may)
        self.btn_xoa.clicked.connect(self.xoa_may)
        self.btn_lam_moi.clicked.connect(self.lam_moi)
        self.btn_tim.clicked.connect(self.tim_may)

        self.bang.cellClicked.connect(self.chon_may)

    # Lấy danh sách khu vực
    def tai_khu_vuc(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT MaKV, TenKhuVuc
                FROM KhuVucMay
                ORDER BY MaKV
            """)

            rows = cursor.fetchall()

            self.khu_vuc.clear()

            for row in rows:
                self.khu_vuc.addItem(
                    row[1], row[0]
                )

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Hiển thị danh sách máy
    def hien_thi_danh_sach(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT m.MaMT, k.TenKhuVuc, m.TrangThai
                FROM MayTinh m
                JOIN KhuVucMay k ON m.MaKV = k.MaKV
                ORDER BY m.MaMT
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
        if not self.ma.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng nhập mã máy tính!"
            )
            return False

        if self.khu_vuc.count() == 0:
            QMessageBox.warning(
                self, "Thông báo",
                "Chưa có khu vực máy để lựa chọn!"
            )
            return False

        return True

    # Thêm máy tính
    def them_may(self):
        if not self.kiem_tra():
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO MayTinh (MaMT, MaKV, TrangThai)
                VALUES (?, ?, ?)
            """, (
                self.ma.text().strip(),
                self.khu_vuc.currentData(),
                self.trang_thai.currentText()
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Thêm máy tính thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Chọn máy tính trên bảng
    def chon_may(self, row, col):
        self.ma.setText(self.bang.item(row, 0).text())

        ten_kv = self.bang.item(row, 1).text()
        index = self.khu_vuc.findText(ten_kv)

        if index >= 0:
            self.khu_vuc.setCurrentIndex(index)

        trang_thai = self.bang.item(row, 2).text()
        self.trang_thai.setCurrentText(trang_thai)

        self.ma.setReadOnly(True)

    # Sửa máy tính
    def sua_may(self):
        if not self.ma.text().strip():
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn máy tính cần sửa!"
            )
            return

        if not self.kiem_tra():
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE MayTinh
                SET MaKV = ?, TrangThai = ?
                WHERE MaMT = ?
            """, (
                self.khu_vuc.currentData(),
                self.trang_thai.currentText(),
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

    # Xóa máy tính
    def xoa_may(self):
        ma = self.ma.text().strip()

        if not ma:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn máy tính cần xóa!"
            )
            return

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc chắn muốn xóa máy tính này?",
            #Giáp đẹp trai vcl
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.No:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM MayTinh WHERE MaMT = ?", (ma,)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thông báo", "Xóa máy tính thành công!"
            )

            self.lam_moi()

        except Exception as e:
            QMessageBox.critical(
                self, "Không thể xóa",
                "Máy tính có thể đã có lịch sử sử dụng.\n" + str(e)
            )

    # Tìm kiếm máy tính
    def tim_may(self):
        tu_khoa = self.tim_kiem.text().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT m.MaMT, k.TenKhuVuc, m.TrangThai
                FROM MayTinh m
                JOIN KhuVucMay k ON m.MaKV = k.MaKV
                WHERE m.MaMT LIKE ?
                ORDER BY m.MaMT
            """, ("%" + tu_khoa + "%",))

            rows = cursor.fetchall()
            self.hien_thi_bang(rows)

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # Làm mới form
    def lam_moi(self):
        self.ma.clear()
        self.ma.setReadOnly(False)

        self.khu_vuc.setCurrentIndex(0)
        self.trang_thai.setCurrentIndex(0)
        self.tim_kiem.clear()

        self.hien_thi_danh_sach()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QuanLyMayTinh()
    window.show()

    sys.exit(app.exec())
