
import sys
from datetime import datetime

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from database import get_connection


class HoaDon(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quản lý hóa đơn")
        self.resize(1100, 900)

        self.gio_hang = {}

        layout = QVBoxLayout()

        # Thông tin hóa đơn
        form = QFormLayout()

        self.khach_hang = QComboBox()
        self.khach_hang.setEditable(True)
        self.khach_hang.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )

        self.nhan_vien = QComboBox()
        self.nhan_vien.setEditable(True)
        self.nhan_vien.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )

        form.addRow("Khách hàng:", self.khach_hang)
        form.addRow("Nhân viên:", self.nhan_vien)

        layout.addLayout(form)

        # Chọn dịch vụ
        layout.addWidget(QLabel("Danh sách dịch vụ"))

        dich_vu_layout = QHBoxLayout()

        self.dich_vu = QComboBox()
        self.so_luong = QSpinBox()
        self.so_luong.setMinimum(1)
        self.so_luong.setMaximum(100000)

        self.btn_them = QPushButton("Thêm dịch vụ")
        self.btn_them.clicked.connect(self.them_dich_vu)

        dich_vu_layout.addWidget(QLabel("Dịch vụ:"))
        dich_vu_layout.addWidget(self.dich_vu)
        dich_vu_layout.addWidget(QLabel("Số lượng:"))
        dich_vu_layout.addWidget(self.so_luong)
        dich_vu_layout.addWidget(self.btn_them)

        layout.addLayout(dich_vu_layout)

        # Bảng dịch vụ trong hóa đơn
        self.bang_chi_tiet = QTableWidget()
        self.bang_chi_tiet.setColumnCount(5)

        self.bang_chi_tiet.setHorizontalHeaderLabels([
            "Mã dịch vụ",
            "Tên dịch vụ",
            "Đơn giá",
            "Số lượng",
            "Thành tiền"
        ])

        self.bang_chi_tiet.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.bang_chi_tiet)

        self.tong_tien = QLabel("Tổng tiền: 0 VNĐ")
        layout.addWidget(self.tong_tien)

        self.btn_xoa = QPushButton("Xóa dịch vụ đã chọn")
        self.btn_xoa.clicked.connect(self.xoa_dich_vu)

        self.btn_tao = QPushButton("Tạo hóa đơn")
        self.btn_tao.clicked.connect(self.tao_hoa_don)

        layout.addWidget(self.btn_xoa)
        layout.addWidget(self.btn_tao)

        # Thanh toán hóa đơn
        layout.addWidget(QLabel("Thanh toán hóa đơn"))

        pay_layout = QHBoxLayout()

        self.phuong_thuc = QComboBox()
        self.phuong_thuc.addItems([
            "Tiền mặt",
            "Chuyển khoản"
        ])

        self.btn_thanh_toan = QPushButton("Thanh toán")
        self.btn_thanh_toan.clicked.connect(
            self.thanh_toan
        )

        pay_layout.addWidget(QLabel("Phương thức:"))
        pay_layout.addWidget(self.phuong_thuc)
        pay_layout.addWidget(self.btn_thanh_toan)

        layout.addLayout(pay_layout)

        # Tìm kiếm hóa đơn
        self.tim = QLineEdit()
        self.tim.setPlaceholderText(
            "Tìm theo mã hóa đơn, mã khách hàng hoặc tên khách hàng..."
        )

        btn_tim = QPushButton("Tìm kiếm")
        btn_tim.clicked.connect(self.tim_kiem)

        btn_tai_lai = QPushButton("Tải lại")
        btn_tai_lai.clicked.connect(self.tai_hoa_don)

        tim_layout = QHBoxLayout()
        tim_layout.addWidget(self.tim)
        tim_layout.addWidget(btn_tim)
        tim_layout.addWidget(btn_tai_lai)

        layout.addLayout(tim_layout)

        # Bảng hóa đơn
        self.bang_hoa_don = QTableWidget()
        self.bang_hoa_don.setColumnCount(7)

        self.bang_hoa_don.setHorizontalHeaderLabels([
            "Mã hóa đơn",
            "Mã khách hàng",
            "Tên khách hàng",
            "Nhân viên",
            "Thời điểm xuất",
            "Tổng tiền",
            "Trạng thái"
        ])

        self.bang_hoa_don.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.bang_hoa_don.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.bang_hoa_don)
        self.btn_chi_tiet = QPushButton("Xem chi tiết hóa đơn")
        self.btn_chi_tiet.clicked.connect(self.xem_chi_tiet)

        layout.addWidget(self.btn_chi_tiet)

        self.setLayout(layout)

        self.tai_combo_box()
        self.tai_dich_vu()
        self.tai_hoa_don()

    # Tạo autocomplete
    def tao_completer(self, combo):
        completer = QCompleter(combo.model(), self)

        completer.setFilterMode(
            Qt.MatchFlag.MatchContains
        )

        completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        combo.setCompleter(completer)

    # Tải khách hàng và nhân viên
    def tai_combo_box(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT ID, HoTen
                FROM KhachHang
                ORDER BY ID
            """)

            self.khach_hang.clear()

            for ma, ten in cursor.fetchall():
                self.khach_hang.addItem(
                    f"{ma} - {ten}", ma
                )

            cursor.execute("""
                SELECT MaNV, TenNV
                FROM NhanVien
                ORDER BY MaNV
            """)

            self.nhan_vien.clear()

            for ma, ten in cursor.fetchall():
                self.nhan_vien.addItem(
                    f"{ma} - {ten}", ma
                )

            self.tao_completer(self.khach_hang)
            self.tao_completer(self.nhan_vien)

        finally:
            conn.close()

    # Lấy mã từ combobox
    def lay_ma(self, combo):
        index = combo.findText(
            combo.currentText(),
            Qt.MatchFlag.MatchExactly
        )

        if index < 0:
            return None

        return combo.itemData(index)

    # Tải danh sách dịch vụ
    def tai_dich_vu(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT MaDV, TenDV, GiaTien, SoLuong
                FROM DichVu
                ORDER BY MaDV
            """)

            self.dich_vu.clear()

            for ma, ten, gia, sl in cursor.fetchall():
                self.dich_vu.addItem(
                    f"{ma} - {ten} (Kho: {sl})",
                    (ma, ten, gia, sl)
                )

        finally:
            conn.close()

    # Thêm dịch vụ vào danh sách hóa đơn
    def them_dich_vu(self):
        du_lieu = self.dich_vu.currentData()

        if du_lieu is None:
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng chọn dịch vụ!"
            )
            return

        ma, ten, gia, ton_kho = du_lieu
        sl = self.so_luong.value()

        if ma in self.gio_hang:
            self.gio_hang[ma]["so_luong"] += sl
        else:
            self.gio_hang[ma] = {
                "ten": ten,
                "gia": gia,
                "so_luong": sl
            }

        self.hien_thi_gio_hang()

    # Hiển thị chi tiết hóa đơn
    def hien_thi_gio_hang(self):
        self.bang_chi_tiet.setRowCount(
            len(self.gio_hang)
        )

        tong = 0

        for i, (ma, item) in enumerate(
            self.gio_hang.items()
        ):
            gia = item["gia"]
            sl = item["so_luong"]
            thanh_tien = gia * sl

            tong += thanh_tien

            values = [
                ma,
                item["ten"],
                f"{gia:,.0f}",
                sl,
                f"{thanh_tien:,.0f}"
            ]

            for j, value in enumerate(values):
                self.bang_chi_tiet.setItem(
                    i, j,
                    QTableWidgetItem(str(value))
                )

        self.bang_chi_tiet.resizeColumnsToContents()

        self.tong_tien.setText(
            f"Tổng tiền: {tong:,.0f} VNĐ"
        )

    # Xóa dịch vụ khỏi danh sách
    def xoa_dich_vu(self):
        row = self.bang_chi_tiet.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn dịch vụ cần xóa!"
            )
            return

        ma = self.bang_chi_tiet.item(row, 0).text()

        if ma in self.gio_hang:
            del self.gio_hang[ma]

        self.hien_thi_gio_hang()

    # Tạo mã hóa đơn
    def tao_ma_hoa_don(self, cursor):
        cursor.execute("""
            SELECT MaHD
            FROM HoaDon WITH (UPDLOCK, HOLDLOCK)
        """)

        rows = cursor.fetchall()
        so_lon_nhat = 0

        for row in rows:
            ma = str(row[0])

            if ma.startswith("HD") and ma[2:].isdigit():
                so_lon_nhat = max(
                    so_lon_nhat,
                    int(ma[2:])
                )

        return "HD" + str(
            so_lon_nhat + 1
        ).zfill(3)

    # Tạo hóa đơn
    def tao_hoa_don(self):
        ma_kh = self.lay_ma(self.khach_hang)
        ma_nv = self.lay_ma(self.nhan_vien)

        if ma_kh is None or ma_nv is None:
            QMessageBox.warning(
                self, "Lỗi",
                "Vui lòng chọn khách hàng và nhân viên!"
            )
            return

        if not self.gio_hang:
            QMessageBox.warning(
                self, "Lỗi",
                "Hóa đơn chưa có dịch vụ!"
            )
            return

        tong = sum(
            item["gia"] * item["so_luong"]
            for item in self.gio_hang.values()
        )

        conn = get_connection()
        cursor = conn.cursor()

        try:
            ma_hd = self.tao_ma_hoa_don(cursor)
            thoi_diem = datetime.now()

            cursor.execute("""
                INSERT INTO HoaDon
                (MaHD, ID, MaNV, ThoiDiemXuat, TongTien,
                 TrangThaiThanhToan, PhuongThucThanhToan,
                 ThoiDiemThanhToan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                ma_hd,
                ma_kh,
                ma_nv,
                thoi_diem,
                tong,
                "Chua thanh toan",
                None,
                None
            )

            for ma_dv, item in self.gio_hang.items():
                sl = item["so_luong"]
                gia = item["gia"]

                cursor.execute("""
                    INSERT INTO ChiTietHoaDon
                    (MaHD, MaDV, SoLuong, DonGia, ThanhTien)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    ma_hd,
                    ma_dv,
                    sl,
                    gia,
                    gia * sl
                )

            conn.commit()

            QMessageBox.information(
                self, "Thông báo",
                f"Tạo hóa đơn thành công!\nMã hóa đơn: {ma_hd}\n"
                f"Tổng tiền: {tong:,.0f} VNĐ\n"
                f"Trạng thái: Chưa thanh toán"
            )

            self.gio_hang.clear()
            self.hien_thi_gio_hang()
            self.tai_hoa_don()

        except Exception as e:
            conn.rollback()

            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Thanh toán hóa đơn đang chọn
    def thanh_toan(self):
        row = self.bang_hoa_don.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn hóa đơn cần thanh toán!"
            )
            return

        ma_hd = self.bang_hoa_don.item(row, 0).text()
        phuong_thuc = self.phuong_thuc.currentText()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT TrangThaiThanhToan
                FROM HoaDon
                WHERE MaHD = ?
            """, ma_hd)

            ket_qua = cursor.fetchone()

            if ket_qua is None:
                raise Exception("Không tìm thấy hóa đơn!")

            if ket_qua[0] == "Da thanh toan":
                QMessageBox.warning(
                    self, "Thông báo",
                    "Hóa đơn này đã được thanh toán!"
                )
                return

            # Lấy chi tiết hóa đơn
            cursor.execute("""
                SELECT MaDV, SoLuong
                FROM ChiTietHoaDon
                WHERE MaHD = ?
            """, ma_hd)

            chi_tiet = cursor.fetchall()

            # Kiểm tra tồn kho trước khi thanh toán
            for ma_dv, sl in chi_tiet:
                cursor.execute("""
                    SELECT SoLuong
                    FROM DichVu
                    WHERE MaDV = ?
                """, ma_dv)

                ton_kho = cursor.fetchone()

                if ton_kho is None:
                    raise Exception(
                        f"Không tìm thấy dịch vụ {ma_dv}!"
                    )

                if ton_kho[0] < sl:
                    raise Exception(
                        f"Dịch vụ {ma_dv} không đủ số lượng trong kho!"
                    )

            # Trừ số lượng dịch vụ
            for ma_dv, sl in chi_tiet:
                cursor.execute("""
                    UPDATE DichVu
                    SET SoLuong = SoLuong - ?
                    WHERE MaDV = ?
                """, sl, ma_dv)

            # Cập nhật hóa đơn
            cursor.execute("""
                UPDATE HoaDon
                SET TrangThaiThanhToan = ?,
                    PhuongThucThanhToan = ?,
                    ThoiDiemThanhToan = ?
                WHERE MaHD = ?
            """,
                "Da thanh toan",
                phuong_thuc,
                datetime.now(),
                ma_hd
            )

            conn.commit()

            QMessageBox.information(
                self, "Thông báo",
                "Thanh toán hóa đơn thành công!"
            )

            self.tai_dich_vu()
            self.tai_hoa_don()

        except Exception as e:
            conn.rollback()

            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Hiển thị danh sách hóa đơn
    def tai_hoa_don(self):
        tu_khoa = self.tim.text().strip()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    hd.MaHD,
                    hd.ID,
                    kh.HoTen,
                    nv.TenNV,
                    hd.ThoiDiemXuat,
                    hd.TongTien,
                    hd.TrangThaiThanhToan
                FROM HoaDon hd
                JOIN KhachHang kh ON hd.ID = kh.ID
                JOIN NhanVien nv ON hd.MaNV = nv.MaNV
                WHERE hd.MaHD LIKE ?
                   OR hd.ID LIKE ?
                   OR kh.HoTen LIKE ?
                ORDER BY hd.ThoiDiemXuat DESC
            """,
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            )

            rows = cursor.fetchall()

            self.bang_hoa_don.setRowCount(len(rows))

            for i, row in enumerate(rows):
                values = [
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4].strftime("%d/%m/%Y %H:%M:%S"),
                    f"{row[5]:,.0f}",
                    row[6]
                ]

                for j, value in enumerate(values):
                    self.bang_hoa_don.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            self.bang_hoa_don.resizeColumnsToContents()

        finally:
            conn.close()

    # Tìm kiếm
    def tim_kiem(self):
        self.tai_hoa_don()

    
    # Xem chi tiết hóa đơn
    def xem_chi_tiet(self):
        row = self.bang_hoa_don.currentRow()

        if row < 0:
            QMessageBox.warning(
                self, "Thông báo",
                "Vui lòng chọn hóa đơn cần xem!"
            )
            return

        ma_hd = self.bang_hoa_don.item(row, 0).text()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    ct.MaDV,
                    dv.TenDV,
                    ct.DonGia,
                    ct.SoLuong,
                    ct.ThanhTien
                FROM ChiTietHoaDon ct
                JOIN DichVu dv ON ct.MaDV = dv.MaDV
                WHERE ct.MaHD = ?
                ORDER BY ct.MaDV
            """, ma_hd)

            rows = cursor.fetchall()

            dialog = QDialog(self)
            dialog.setWindowTitle(
                "Chi tiết hóa đơn " + ma_hd
            )
            dialog.resize(750, 400)

            layout = QVBoxLayout()

            title = QLabel(
                "CHI TIẾT HÓA ĐƠN: " + ma_hd
            )
            title.setStyleSheet(
                "font-size: 20px; font-weight: bold;"
            )

            layout.addWidget(title)

            bang = QTableWidget()
            bang.setColumnCount(5)

            bang.setHorizontalHeaderLabels([
                "Mã dịch vụ",
                "Tên dịch vụ",
                "Đơn giá",
                "Số lượng",
                "Thành tiền"
            ])

            bang.setRowCount(len(rows))

            for i, item in enumerate(rows):
                ma_dv, ten_dv, don_gia, so_luong, thanh_tien = item

                values = [
                    ma_dv,
                    ten_dv,
                    f"{don_gia:,.0f}",
                    so_luong,
                    f"{thanh_tien:,.0f}"
                ]

                for j, value in enumerate(values):
                    bang.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            bang.resizeColumnsToContents()

            layout.addWidget(bang)

            cursor.execute("""
                SELECT TongTien, TrangThaiThanhToan
                FROM HoaDon
                WHERE MaHD = ?
            """, ma_hd)

            thong_tin = cursor.fetchone()

            if thong_tin:
                tong_tien, trang_thai = thong_tin

                label_tong = QLabel(
                    f"Tổng tiền: {tong_tien:,.0f} VNĐ"
                )

                label_trang_thai = QLabel(
                    f"Trạng thái: {trang_thai}"
                )

                layout.addWidget(label_tong)
                layout.addWidget(label_trang_thai)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HoaDon()
    window.show()
    sys.exit(app.exec())
