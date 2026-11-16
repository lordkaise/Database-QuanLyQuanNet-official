
import sys
import csv

from PyQt6.QtWidgets import *
from database import get_connection


class BaoCaoMayBaoTri(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Báo cáo máy bảo trì")
        self.resize(900, 600)

        self.du_lieu = []

        layout = QVBoxLayout()

        title = QLabel("BÁO CÁO MÁY TÍNH ĐANG BẢO TRÌ")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        # Nút thống kê
        self.btn_thong_ke = QPushButton("Cập nhật báo cáo")
        self.btn_thong_ke.clicked.connect(self.thong_ke)

        layout.addWidget(self.btn_thong_ke)

        # Bảng máy bảo trì
        self.bang = QTableWidget()
        self.bang.setColumnCount(4)

        self.bang.setHorizontalHeaderLabels([
            "Mã máy",
            "Khu vực",
            "Cấu hình",
            "Trạng thái"
        ])

        self.bang.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.bang)

        # Tổng số máy
        self.tong = QLabel("Tổng số máy đang bảo trì: 0")
        self.tong.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(self.tong)

        # Xuất CSV
        self.btn_xuat = QPushButton("Xuất báo cáo CSV")
        self.btn_xuat.clicked.connect(self.xuat_bao_cao)

        layout.addWidget(self.btn_xuat)

        self.setLayout(layout)

        self.thong_ke()

    # Thống kê máy bảo trì
    def thong_ke(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    mt.MaMT,
                    kv.TenKhuVuc,
                    kv.CauHinh,
                    mt.TrangThai
                FROM MayTinh mt
                JOIN KhuVucMay kv ON mt.MaKV = kv.MaKV
                WHERE mt.TrangThai = N'Bao Tri'
                ORDER BY mt.MaMT
            """)

            rows = cursor.fetchall()

            self.du_lieu = rows
            self.bang.setRowCount(len(rows))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.bang.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            self.bang.resizeColumnsToContents()

            self.tong.setText(
                f"Tổng số máy đang bảo trì: {len(rows)}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Xuất báo cáo CSV
    def xuat_bao_cao(self):
        if not self.du_lieu:
            QMessageBox.information(
                self, "Thông báo",
                "Hiện không có máy nào đang bảo trì!"
            )
            return

        ten_file, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu báo cáo",
            "BaoCaoMayBaoTri.csv",
            "CSV Files (*.csv)"
        )

        if not ten_file:
            return

        try:
            with open(
                ten_file,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as f:
                writer = csv.writer(f)

                writer.writerow([
                    "MaMay",
                    "KhuVuc",
                    "CauHinh",
                    "TrangThai"
                ])

                for row in self.du_lieu:
                    writer.writerow(row)

                writer.writerow([])
                writer.writerow([
                    "Tong so may dang bao tri",
                    len(self.du_lieu)
                ])

            QMessageBox.information(
                self, "Thông báo",
                "Xuất báo cáo thành công!"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaoCaoMayBaoTri()
    window.show()
    sys.exit(app.exec())
