
import sys
import csv

from PyQt6.QtWidgets import *

from database import get_connection


class BaoCaoDichVu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Báo cáo dịch vụ")
        self.resize(1100, 650)

        self.du_lieu = []

        layout = QVBoxLayout()

        title = QLabel("BÁO CÁO DỊCH VỤ")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        btn_layout = QHBoxLayout()

        self.btn_thong_ke = QPushButton("Thống kê")
        self.btn_thong_ke.clicked.connect(self.thong_ke)

        self.btn_xuat = QPushButton("Xuất báo cáo CSV")
        self.btn_xuat.clicked.connect(self.xuat_bao_cao)

        btn_layout.addWidget(self.btn_thong_ke)
        btn_layout.addWidget(self.btn_xuat)

        layout.addLayout(btn_layout)

        # Bảng thống kê
        self.bang = QTableWidget()
        self.bang.setColumnCount(6)

        self.bang.setHorizontalHeaderLabels([
            "Mã dịch vụ",
            "Tên dịch vụ",
            "Phân loại",
            "Số lượng bán hôm nay",
            "Doanh thu hôm nay",
            "Tồn kho hiện tại"
        ])

        self.bang.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.bang.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.bang)

        self.tong = QLabel(
            "Tổng số lượng đã bán: 0 | Tổng doanh thu: 0 VNĐ"
        )

        self.tong.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )

        layout.addWidget(self.tong)

        self.setLayout(layout)

        self.thong_ke()

    # Thống kê dịch vụ
    def thong_ke(self):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    dv.MaDV,
                    dv.TenDV,
                    dv.PhanLoai,

                    ISNULL(SUM(
                        CASE
                            WHEN hd.TrangThaiThanhToan = N'Da thanh toan'
                            AND hd.ThoiDiemThanhToan >= CAST(GETDATE() AS DATE)
                            AND hd.ThoiDiemThanhToan < DATEADD(
                                DAY, 1, CAST(GETDATE() AS DATE)
                            )
                            THEN ct.SoLuong
                            ELSE 0
                        END
                    ), 0) AS TongSoLuong,

                    ISNULL(SUM(
                        CASE
                            WHEN hd.TrangThaiThanhToan = N'Da thanh toan'
                            AND hd.ThoiDiemThanhToan >= CAST(GETDATE() AS DATE)
                            AND hd.ThoiDiemThanhToan < DATEADD(
                                DAY, 1, CAST(GETDATE() AS DATE)
                            )
                            THEN ct.ThanhTien
                            ELSE 0
                        END
                    ), 0) AS DoanhThu,

                    dv.SoLuong AS TonKho

                FROM DichVu dv

                LEFT JOIN ChiTietHoaDon ct
                    ON dv.MaDV = ct.MaDV

                LEFT JOIN HoaDon hd
                    ON ct.MaHD = hd.MaHD

                GROUP BY
                    dv.MaDV,
                    dv.TenDV,
                    dv.PhanLoai,
                    dv.SoLuong

                ORDER BY dv.MaDV
            """)

            rows = cursor.fetchall()

            self.du_lieu = rows
            self.bang.setRowCount(len(rows))

            tong_so_luong = 0
            tong_doanh_thu = 0

            for i, row in enumerate(rows):
                ma, ten, loai, sl, doanh_thu, ton_kho = row

                sl = sl or 0
                doanh_thu = doanh_thu or 0

                tong_so_luong += sl
                tong_doanh_thu += doanh_thu

                values = [
                    ma,
                    ten,
                    loai,
                    sl,
                    f"{doanh_thu:,.0f}",
                    ton_kho
                ]

                for j, value in enumerate(values):
                    self.bang.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            self.bang.resizeColumnsToContents()

            self.tong.setText(
                f"Tổng số lượng đã bán hôm nay: {tong_so_luong} | "
                f"Doanh thu hôm nay: {tong_doanh_thu:,.0f} VNĐ"
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
            QMessageBox.warning(
                self, "Thông báo",
                "Không có dữ liệu để xuất!"
            )
            return

        ten_file, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu báo cáo",
            "BaoCaoDichVu.csv",
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
                    "MaDV",
                    "TenDV",
                    "PhanLoai",
                    "SoLuongDaBan",
                    "DoanhThu",
                    "TonKhoHienTai"
                ])

                tong_so_luong = 0
                tong_doanh_thu = 0

                for row in self.du_lieu:
                    ma, ten, loai, sl, doanh_thu, ton_kho = row

                    sl = sl or 0
                    doanh_thu = doanh_thu or 0

                    tong_so_luong += sl
                    tong_doanh_thu += doanh_thu

                    writer.writerow([
                        ma, ten, loai, sl,
                        doanh_thu, ton_kho
                    ])

                writer.writerow([])
                writer.writerow([
                    "Tổng cộng", "", "",
                    tong_so_luong,
                    tong_doanh_thu,
                    ""
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
    window = BaoCaoDichVu()
    window.show()
    sys.exit(app.exec())
