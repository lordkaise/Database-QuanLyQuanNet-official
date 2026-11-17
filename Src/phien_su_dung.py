import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDateTime, QTimer, Qt, pyqtSignal

from database import get_connection


class PhienSuDung(QWidget):

    # Thông báo khi trạng thái máy tính thay đổi
    trang_thai_may_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý phiên sử dụng máy")
        self.resize(1100, 650)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Chọn khách hàng
        self.khach_hang = QComboBox()
        self.khach_hang.setEditable(True)
        self.khach_hang.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )
        self.khach_hang.setPlaceholderText(
            "Nhập mã hoặc tên khách hàng..."
        )

        # Chọn máy tính
        self.may_tinh = QComboBox()
        self.may_tinh.setEditable(True)
        self.may_tinh.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )
        self.may_tinh.setPlaceholderText(
            "Nhập mã máy tính..."
        )

        self.thoi_gian = QDateTimeEdit()
        self.thoi_gian.setDateTime(
            QDateTime.currentDateTime()
        )
        self.thoi_gian.setDisplayFormat(
            "dd/MM/yyyy HH:mm:ss"
        )

        form.addRow("Khách hàng:", self.khach_hang)
        form.addRow("Máy tính:", self.may_tinh)
        form.addRow("Thời điểm bắt đầu:", self.thoi_gian)

        layout.addLayout(form)

        # Các nút chức năng
        btn_layout = QHBoxLayout()

        self.btn_bat_dau = QPushButton("Bắt đầu phiên")
        self.btn_bat_dau.clicked.connect(self.bat_dau)

        self.btn_ket_thuc = QPushButton("Kết thúc phiên")
        self.btn_ket_thuc.clicked.connect(self.ket_thuc_chon)

        self.btn_tim = QPushButton("Tìm kiếm")
        self.btn_tim.clicked.connect(self.tim_kiem)

        self.btn_tai_lai = QPushButton("Tải lại")
        self.btn_tai_lai.clicked.connect(self.tai_du_lieu)

        btn_layout.addWidget(self.btn_bat_dau)
        btn_layout.addWidget(self.btn_ket_thuc)
        btn_layout.addWidget(self.btn_tim)
        btn_layout.addWidget(self.btn_tai_lai)

        layout.addLayout(btn_layout)

        # Ô tìm kiếm
        self.tu_khoa = QLineEdit()
        self.tu_khoa.setPlaceholderText(
            "Tìm theo mã phiên, mã khách hàng, tên khách hàng hoặc mã máy..."
        )
        layout.addWidget(self.tu_khoa)

        # Bảng phiên sử dụng
        self.bang = QTableWidget()
        layout.addWidget(self.bang)

        self.setLayout(layout)

        self.tai_combo_box()
        self.tai_du_lieu()

        # Tự động kiểm tra thời gian mỗi giây
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cap_nhat_thoi_gian)
        self.timer.start(1000)

    # Tạo chức năng gõ để tìm kiếm
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

    # Tải khách hàng và máy tính
    def tai_combo_box(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            self.khach_hang.clear()
            self.may_tinh.clear()

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
                SELECT mt.MaMT, kv.TenKhuVuc,
                       kv.GiaTienGio, mt.TrangThai
                FROM MayTinh mt
                JOIN KhuVucMay kv ON mt.MaKV = kv.MaKV
                ORDER BY mt.MaMT
            """)

            for ma_mt, ten_kv, gia, trang_thai in cursor.fetchall():
                self.may_tinh.addItem(
                    f"{ma_mt} - {ten_kv} - {trang_thai}",
                    ma_mt
                )

            self.tao_completer(self.khach_hang)
            self.tao_completer(self.may_tinh)

        finally:
            conn.close()

    # Lấy mã đã chọn từ ComboBox
    def lay_ma_da_chon(self, combo):
        index = combo.currentIndex()

        if index < 0:
            return None

        if combo.currentText() != combo.itemText(index):
            return None

        return combo.currentData()

    # Tự động tạo mã phiên theo dạng PS001, PS002, PS003...
    def tao_ma_phien(self, cursor):
        # Khóa vùng dữ liệu để hạn chế việc hai thao tác
        # tạo phiên cùng lúc lấy trùng một mã.
        cursor.execute("""
            SELECT ISNULL(
                MAX(TRY_CONVERT(INT, SUBSTRING(MaPhien, 3, LEN(MaPhien)))),
                0
            )
            FROM PhienSuDung WITH (UPDLOCK, HOLDLOCK)
            WHERE MaPhien LIKE 'PS[0-9]%'
              AND TRY_CONVERT(
                    INT, SUBSTRING(MaPhien, 3, LEN(MaPhien))
                  ) IS NOT NULL
        """)

        so_lon_nhat = cursor.fetchone()[0] or 0
        return f"PS{int(so_lon_nhat) + 1:03d}"

    # Bắt đầu phiên sử dụng
    def bat_dau(self):
        id_kh = self.lay_ma_da_chon(self.khach_hang)
        ma_mt = self.lay_ma_da_chon(self.may_tinh)

        if id_kh is None:
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng chọn khách hàng!"
            )
            return

        if ma_mt is None:
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng chọn máy tính!"
            )
            return

        thoi_diem = self.thoi_gian.dateTime().toPyDateTime()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Kiểm tra khách hàng và lấy số dư
            cursor.execute("""
                SELECT SoDu
                FROM KhachHang
                WHERE ID = ?
            """, id_kh)

            khach = cursor.fetchone()

            if khach is None:
                QMessageBox.warning(
                    self, "Lỗi", "Không tìm thấy khách hàng!"
                )
                return

            so_du = Decimal(str(khach[0] or 0))

            if so_du <= 0:
                QMessageBox.warning(
                    self, "Lỗi",
                    "Khách hàng không đủ số dư để sử dụng máy!"
                )
                return

            # Kiểm tra máy và lấy đơn giá
            cursor.execute("""
                SELECT mt.TrangThai, kv.GiaTienGio
                FROM MayTinh mt
                JOIN KhuVucMay kv ON mt.MaKV = kv.MaKV
                WHERE mt.MaMT = ?
            """, ma_mt)

            may = cursor.fetchone()

            if may is None:
                QMessageBox.warning(
                    self, "Lỗi", "Không tìm thấy máy tính!"
                )
                return

            if may[0] != "Trong":
                QMessageBox.warning(
                    self, "Lỗi",
                    "Máy tính hiện không ở trạng thái Trống!"
                )
                return

            don_gia = Decimal(str(may[1] or 0))

            if don_gia <= 0:
                QMessageBox.warning(
                    self, "Lỗi", "Đơn giá máy không hợp lệ!"
                )
                return

            # Không cho một khách hàng sử dụng nhiều máy cùng lúc
            cursor.execute("""
                SELECT COUNT(*)
                FROM PhienSuDung
                WHERE ID = ? AND ThoiGianKetThuc IS NULL
            """, id_kh)

            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(
                    self, "Lỗi",
                    "Khách hàng đang có một phiên sử dụng chưa kết thúc!"
                )
                return

            # Tự động sinh mã phiên ngay trước khi thêm dữ liệu
            ma = self.tao_ma_phien(cursor)

            # Thêm phiên sử dụng
            cursor.execute("""
                INSERT INTO PhienSuDung
                (MaPhien, ID, MaMT, ThoiGianBatDau,
                 ThoiGianKetThuc, TongThoiGian,
                 DonGiaApDung, SoTienTru)
                VALUES (?, ?, ?, ?, NULL, 0, ?, 0)
            """, ma, id_kh, ma_mt, thoi_diem, don_gia)

            # Cập nhật trạng thái máy
            cursor.execute("""
                UPDATE MayTinh
                SET TrangThai = N'Dang su dung'
                WHERE MaMT = ?
            """, ma_mt)

            conn.commit()

            self.trang_thai_may_changed.emit()
            self.tai_combo_box()

            QMessageBox.information(
                self, "Thông báo",
                f"Bắt đầu phiên thành công!\nMã phiên: {ma}"
            )

            self.thoi_gian.setDateTime(
                QDateTime.currentDateTime()
            )

            self.tai_du_lieu()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Tính số phút và số tiền sử dụng
    def tinh_tien(self, thoi_diem_bd, don_gia):
        giay = max(
            0,
            (datetime.now() - thoi_diem_bd).total_seconds()
        )

        # Làm tròn thời gian đến phút
        so_phut = int(round(giay / 60))

        don_gia = Decimal(str(don_gia))
        so_tien = (
            don_gia * Decimal(so_phut) / Decimal(60)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        return so_phut, so_tien

    # Kết thúc phiên sử dụng
    def ket_thuc(self, ma_phien, tu_dong=False):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Lấy thông tin phiên và số dư khách hàng
            cursor.execute("""
                SELECT
                    ps.ID,
                    ps.MaMT,
                    ps.ThoiGianBatDau,
                    ps.DonGiaApDung,
                    kh.SoDu
                FROM PhienSuDung ps
                JOIN KhachHang kh ON ps.ID = kh.ID
                WHERE ps.MaPhien = ?
                  AND ps.ThoiGianKetThuc IS NULL
            """, ma_phien)

            row = cursor.fetchone()

            if row is None:
                return

            id_kh, ma_mt, bd, don_gia, so_du = row

            so_phut, so_tien = self.tinh_tien(
                bd, don_gia
            )

            so_du = Decimal(str(so_du or 0))

            # Không trừ vượt quá số dư hiện có
            so_tien = min(so_tien, so_du)

            thoi_diem_kt = datetime.now()

            # Cập nhật thông tin phiên
            cursor.execute("""
                UPDATE PhienSuDung
                SET ThoiGianKetThuc = ?,
                    TongThoiGian = ?,
                    SoTienTru = ?
                WHERE MaPhien = ?
                  AND ThoiGianKetThuc IS NULL
            """, thoi_diem_kt, so_phut, so_tien, ma_phien)

            # Trừ tiền khách hàng
            cursor.execute("""
                UPDATE KhachHang
                SET SoDu = ISNULL(SoDu, 0) - ?
                WHERE ID = ?
            """, so_tien, id_kh)

            # Trả máy về trạng thái Trống
            cursor.execute("""
                UPDATE MayTinh
                SET TrangThai = N'Trong'
                WHERE MaMT = ?
            """, ma_mt)

            conn.commit()
            self.trang_thai_may_changed.emit()
            self.tai_combo_box()

            if not tu_dong:
                QMessageBox.information(
                    self, "Thông báo",
                    "Kết thúc phiên thành công!\n"
                    f"Thời gian sử dụng: {so_phut} phút\n"
                    f"Số tiền đã trừ: {so_tien} đồng"
                )

        except Exception as e:
            conn.rollback()

            if not tu_dong:
                QMessageBox.critical(
                    self, "Lỗi", str(e)
                )

        finally:
            conn.close()

    # Kết thúc phiên được chọn trên bảng
    def ket_thuc_chon(self):
        dong = self.bang.currentRow()

        if dong < 0:
            QMessageBox.warning(
                self, "Lỗi",
                "Vui lòng chọn phiên cần kết thúc!"
            )
            return

        ma_phien = self.bang.item(dong, 0).text()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT ThoiGianKetThuc
                FROM PhienSuDung
                WHERE MaPhien = ?
            """, ma_phien)

            row = cursor.fetchone()

            if row is None or row[0] is not None:
                QMessageBox.warning(
                    self, "Lỗi",
                    "Phiên này đã kết thúc!"
                )
                return

        finally:
            conn.close()

        hoi = QMessageBox.question(
            self, "Xác nhận",
            "Bạn có chắc muốn kết thúc phiên này?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if hoi == QMessageBox.StandardButton.Yes:
            self.ket_thuc(ma_phien)
            self.tai_du_lieu()

    # Kiểm tra thời gian còn lại của các phiên đang chạy
    def cap_nhat_thoi_gian(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    ps.MaPhien,
                    ps.ThoiGianBatDau,
                    ps.DonGiaApDung,
                    kh.SoDu
                FROM PhienSuDung ps
                JOIN KhachHang kh ON ps.ID = kh.ID
                WHERE ps.ThoiGianKetThuc IS NULL
            """)

            rows = cursor.fetchall()

        finally:
            conn.close()

        for ma_phien, bd, don_gia, so_du in rows:
            giay_da_dung = max(
                0,
                (datetime.now() - bd).total_seconds()
            )

            so_du = Decimal(str(so_du or 0))
            don_gia = Decimal(str(don_gia or 0))

            if don_gia <= 0:
                continue

            # Thời gian tối đa có thể sử dụng theo số dư
            tong_giay = float(
                so_du * Decimal(3600) / don_gia
            )

            giay_con_lai = tong_giay - giay_da_dung

            if giay_con_lai <= 0:
                self.ket_thuc(ma_phien, True)

        self.tai_du_lieu()

    # Hiển thị danh sách phiên sử dụng
    def tai_du_lieu(self):
        tu_khoa = self.tu_khoa.text().strip()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    ps.MaPhien,
                    ps.ID,
                    kh.HoTen,
                    ps.MaMT,
                    ps.ThoiGianBatDau,
                    ps.ThoiGianKetThuc,
                    ps.TongThoiGian,
                    ps.DonGiaApDung,
                    ps.SoTienTru,
                    kh.SoDu
                FROM PhienSuDung ps
                JOIN KhachHang kh ON ps.ID = kh.ID
                WHERE ps.MaPhien LIKE ?
                   OR ps.ID LIKE ?
                   OR kh.HoTen LIKE ?
                   OR ps.MaMT LIKE ?
                ORDER BY ps.MaPhien DESC
            """,
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            )

            rows = cursor.fetchall()

            self.bang.setColumnCount(9)
            self.bang.setHorizontalHeaderLabels([
                "Mã phiên",
                "Mã khách hàng",
                "Tên khách hàng",
                "Mã máy",
                "Thời điểm bắt đầu",
                "Thời điểm kết thúc",
                "Tổng thời gian (phút)",
                "Số tiền trừ",
                "Trạng thái / Thời gian còn lại"
            ])

            self.bang.setRowCount(len(rows))

            for i, row in enumerate(rows):
                ma_phien, id_kh, hoten, ma_mt, bd, kt, tong_phut, gia, tien, so_du = row

                if kt is None:
                    giay_da_dung = max(
                        0,
                        (datetime.now() - bd).total_seconds()
                    )

                    don_gia = Decimal(str(gia or 0))
                    so_du = Decimal(str(so_du or 0))

                    if don_gia > 0:
                        giay_con_lai = max(
                            0,
                            float(
                                so_du * Decimal(3600) / don_gia
                            ) - giay_da_dung
                        )

                        phut_con = int(giay_con_lai // 60)
                        giay_con = int(giay_con_lai % 60)

                        trang_thai = (
                            f"Đang sử dụng - "
                            f"{phut_con}p {giay_con}s"
                        )
                    else:
                        trang_thai = "Đang sử dụng"
                else:
                    trang_thai = "Đã kết thúc"

                values = [
                    ma_phien,
                    id_kh,
                    hoten,
                    ma_mt,
                    bd,
                    kt if kt is not None else "",
                    tong_phut if kt is not None else "",
                    tien if kt is not None else "",
                    trang_thai
                ]

                for j, value in enumerate(values):
                    self.bang.setItem(
                        i, j, QTableWidgetItem(str(value))
                    )

            self.bang.resizeColumnsToContents()

        finally:
            conn.close()

    # Tìm kiếm phiên sử dụng
    def tim_kiem(self):
        self.tai_du_lieu()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhienSuDung()
    window.show()
    sys.exit(app.exec())
