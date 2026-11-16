
import sys
from datetime import datetime

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from database import get_connection


class ChamCong(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quản lý chấm công nhân viên")
        self.resize(1000, 600)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Chọn nhân viên
        self.nhan_vien = QComboBox()
        self.nhan_vien.setEditable(True)
        self.nhan_vien.setInsertPolicy(
            QComboBox.InsertPolicy.NoInsert
        )
        self.nhan_vien.setPlaceholderText(
            "Nhập mã hoặc tên nhân viên..."
        )

        form.addRow("Nhân viên:", self.nhan_vien)
        layout.addLayout(form)

        # Các nút chức năng
        btn_layout = QHBoxLayout()

        self.btn_cham_cong = QPushButton("Chấm công")
        self.btn_cham_cong.clicked.connect(self.cham_cong)

        self.btn_tim = QPushButton("Tìm kiếm")
        self.btn_tim.clicked.connect(self.tim_kiem)

        self.btn_tai_lai = QPushButton("Tải lại")
        self.btn_tai_lai.clicked.connect(self.tai_du_lieu)

        btn_layout.addWidget(self.btn_cham_cong)
        btn_layout.addWidget(self.btn_tim)
        btn_layout.addWidget(self.btn_tai_lai)

        layout.addLayout(btn_layout)

        # Ô tìm kiếm
        self.tu_khoa = QLineEdit()
        self.tu_khoa.setPlaceholderText(
            "Tìm theo mã nhân viên, tên nhân viên hoặc mã chấm công..."
        )
        layout.addWidget(self.tu_khoa)

        # Bảng lịch sử chấm công
        self.bang = QTableWidget()
        self.bang.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.bang.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.bang)

        self.setLayout(layout)

        self.tai_combo_box()
        self.tai_du_lieu()

    # Tạo chức năng gõ để tìm nhân viên
    def tao_completer(self):
        completer = QCompleter(
            self.nhan_vien.model(), self
        )

        completer.setFilterMode(
            Qt.MatchFlag.MatchContains
        )

        completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        self.nhan_vien.setCompleter(completer)

    # Tải danh sách nhân viên
    def tai_combo_box(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            self.nhan_vien.clear()

            cursor.execute("""
                SELECT MaNV, TenNV
                FROM NhanVien
                ORDER BY MaNV
            """)

            for ma_nv, ten_nv in cursor.fetchall():
                self.nhan_vien.addItem(
                    f"{ma_nv} - {ten_nv}", ma_nv
                )

            self.tao_completer()

        finally:
            conn.close()

    # Lấy mã nhân viên đã chọn
    def lay_ma_nhan_vien(self):
        index = self.nhan_vien.findText(
            self.nhan_vien.currentText(),
            Qt.MatchFlag.MatchExactly
        )

        if index < 0:
            return None

        return self.nhan_vien.itemData(index)

    # Thực hiện chấm công
    def cham_cong(self):
        ma_nv = self.lay_ma_nhan_vien()

        if ma_nv is None:
            QMessageBox.warning(
                self, "Lỗi",
                "Vui lòng chọn nhân viên!"
            )
            return

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Đếm số lần chấm công của nhân viên
            cursor.execute("""
                SELECT COUNT(*)
                FROM ChamCong
                WHERE MaNV = ?
            """, ma_nv)

            so_lan = cursor.fetchone()[0]

            # Lần lẻ là check-in, lần chẵn là check-out
            if so_lan % 2 == 0:
                loai = "Check-in"
            else:
                loai = "Check-out"

            # Tự động tạo mã chấm công
            cursor.execute("""
                SELECT MaChamCong
                FROM ChamCong
                WITH (UPDLOCK, HOLDLOCK)
            """)

            rows = cursor.fetchall()

            so_lon_nhat = 0

            for row in rows:
                ma = str(row[0])

                if ma.startswith("CC") and ma[2:].isdigit():
                    so_lon_nhat = max(
                        so_lon_nhat,
                        int(ma[2:])
                    )

            ma_cc = "CC" + str(
                so_lon_nhat + 1
            ).zfill(2)

            thoi_diem = datetime.now()

            cursor.execute("""
                INSERT INTO ChamCong
                (MaChamCong, MaNV, ThoiDiemChamCong)
                VALUES (?, ?, ?)
            """, ma_cc, ma_nv, thoi_diem)

            conn.commit()

            QMessageBox.information(
                self, "Thông báo",
                f"Chấm công thành công!\n"
                f"Loại: {loai}\n"
                f"Thời điểm: {thoi_diem.strftime('%d/%m/%Y %H:%M:%S')}"
            )

            self.tai_du_lieu()

        except Exception as e:
            conn.rollback()

            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Hiển thị lịch sử chấm công
    def tai_du_lieu(self):
        tu_khoa = self.tu_khoa.text().strip()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    cc.MaChamCong,
                    cc.MaNV,
                    nv.TenNV,
                    cc.ThoiDiemChamCong
                FROM ChamCong cc
                JOIN NhanVien nv ON cc.MaNV = nv.MaNV
                WHERE cc.MaChamCong LIKE ?
                   OR cc.MaNV LIKE ?
                   OR nv.TenNV LIKE ?
                ORDER BY cc.ThoiDiemChamCong DESC
            """,
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%",
                "%" + tu_khoa + "%"
            )

            rows = cursor.fetchall()

            self.bang.setColumnCount(5)

            self.bang.setHorizontalHeaderLabels([
                "Mã chấm công",
                "Mã nhân viên",
                "Tên nhân viên",
                "Thời điểm",
                "Loại chấm công"
            ])

            self.bang.setRowCount(len(rows))

            for i, row in enumerate(rows):
                ma_cc, ma_nv, ten_nv, thoi_diem = row

                # Xác định lần chấm công của nhân viên
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM ChamCong
                    WHERE MaNV = ?
                      AND ThoiDiemChamCong <= ?
                """, ma_nv, thoi_diem)

                thu_tu = cursor.fetchone()[0]

                if thu_tu % 2 == 1:
                    loai = "Check-in"
                else:
                    loai = "Check-out"

                values = [
                    ma_cc,
                    ma_nv,
                    ten_nv,
                    thoi_diem.strftime("%d/%m/%Y %H:%M:%S"),
                    loai
                ]

                for j, value in enumerate(values):
                    self.bang.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            self.bang.resizeColumnsToContents()

        finally:
            conn.close()

    # Tìm kiếm
    def tim_kiem(self):
        self.tai_du_lieu()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChamCong()
    window.show()
    sys.exit(app.exec())
