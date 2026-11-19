
import sys
import csv
from datetime import datetime, timedelta

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate

from database import get_connection


class BaoCaoDoanhThu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Báo cáo doanh thu")
        self.resize(1000, 650)

        self.du_lieu = []

        layout = QVBoxLayout()

        title = QLabel("BÁO CÁO DOANH THU")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(title)

        # Chọn khoảng thời gian
        form = QHBoxLayout()

        self.tu_ngay = QDateEdit()
        self.tu_ngay.setCalendarPopup(True)
        self.tu_ngay.setDisplayFormat("dd/MM/yyyy")

        self.den_ngay = QDateEdit()
        self.den_ngay.setCalendarPopup(True)
        self.den_ngay.setDisplayFormat("dd/MM/yyyy")

        hom_nay = QDate.currentDate()

        self.tu_ngay.setDate(
            QDate(hom_nay.year(), hom_nay.month(), 1)
        )
        self.den_ngay.setDate(hom_nay)

        self.btn_thong_ke = QPushButton("Thống kê")
        self.btn_thong_ke.clicked.connect(self.thong_ke)

        form.addWidget(QLabel("Từ ngày:"))
        form.addWidget(self.tu_ngay)
        form.addWidget(QLabel("Đến ngày:"))
        form.addWidget(self.den_ngay)
        form.addWidget(self.btn_thong_ke)

        layout.addLayout(form)

        # Tổng hợp doanh thu theo nguồn
        tong_theo_nguon = QHBoxLayout()

        self.doanh_thu_phien = QLabel(
            "Doanh thu phiên sử dụng: 0 VNĐ"
        )
        self.doanh_thu_phien.setStyleSheet(
            "font-size: 16px; font-weight: bold; "
            "padding: 10px; border: 1px solid #999; border-radius: 5px;"
        )

        self.doanh_thu_hoa_don = QLabel(
            "Doanh thu hóa đơn dịch vụ: 0 VNĐ"
        )
        self.doanh_thu_hoa_don.setStyleSheet(
            "font-size: 16px; font-weight: bold; "
            "padding: 10px; border: 1px solid #999; border-radius: 5px;"
        )

        tong_theo_nguon.addWidget(self.doanh_thu_phien)
        tong_theo_nguon.addWidget(self.doanh_thu_hoa_don)
        layout.addLayout(tong_theo_nguon)

        # Bảng doanh thu
        self.bang = QTableWidget()
        self.bang.setColumnCount(4)

        self.bang.setHorizontalHeaderLabels([
            "Nguồn doanh thu",
            "Mã giao dịch",
            "Thời điểm",
            "Số tiền"
        ])

        self.bang.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.bang.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.bang.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        layout.addWidget(self.bang)

        # Xem chi tiết
        self.btn_chi_tiet = QPushButton("Xem chi tiết")
        self.btn_chi_tiet.clicked.connect(self.xem_chi_tiet)

        layout.addWidget(self.btn_chi_tiet)

        # Tổng doanh thu
        self.tong = QLabel("Tổng doanh thu: 0 VNĐ")
        self.tong.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        layout.addWidget(self.tong)

        # Xuất báo cáo
        self.btn_xuat = QPushButton("Xuất báo cáo CSV")
        self.btn_xuat.clicked.connect(self.xuat_bao_cao)

        layout.addWidget(self.btn_xuat)

        self.setLayout(layout)

    # Thống kê doanh thu
    def thong_ke(self):
        ngay_bd = self.tu_ngay.date().toPyDate()
        ngay_kt = self.den_ngay.date().toPyDate()

        if ngay_bd > ngay_kt:
            QMessageBox.warning(
                self, "Thông báo",
                "Ngày bắt đầu không được lớn hơn ngày kết thúc!"
            )
            return

        ngay_sau = ngay_kt + timedelta(days=1)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    N'Phiên sử dụng',
                    MaPhien,
                    ThoiGianKetThuc AS ThoiDiem,
                    SoTienTru AS SoTien
                FROM PhienSuDung
                WHERE ThoiGianKetThuc >= ?
                  AND ThoiGianKetThuc < ?
                  AND ThoiGianKetThuc IS NOT NULL

                UNION ALL

                SELECT
                    N'Hóa đơn dịch vụ',
                    MaHD,
                    ThoiDiemThanhToan,
                    TongTien
                FROM HoaDon
                WHERE TrangThaiThanhToan = N'Da thanh toan'
                  AND ThoiDiemThanhToan >= ?
                  AND ThoiDiemThanhToan < ?

                ORDER BY ThoiDiem DESC
            """,
                ngay_bd,
                ngay_sau,
                ngay_bd,
                ngay_sau
            )

            rows = cursor.fetchall()

            self.du_lieu = rows
            self.bang.setRowCount(len(rows))

            tong_tien = 0
            tong_phien = 0
            tong_hoa_don = 0

            for i, row in enumerate(rows):
                nguon, ma, thoi_diem, so_tien = row

                so_tien = so_tien or 0
                tong_tien += so_tien

                if nguon == "Phiên sử dụng":
                    tong_phien += so_tien
                elif nguon == "Hóa đơn dịch vụ":
                    tong_hoa_don += so_tien

                values = [
                    nguon,
                    ma,
                    thoi_diem.strftime("%d/%m/%Y %H:%M:%S"),
                    f"{so_tien:,.0f}"
                ]

                for j, value in enumerate(values):
                    self.bang.setItem(
                        i, j,
                        QTableWidgetItem(str(value))
                    )

            self.bang.resizeColumnsToContents()

            self.doanh_thu_phien.setText(
                f"Doanh thu phiên sử dụng: {tong_phien:,.0f} VNĐ"
            )
            self.doanh_thu_hoa_don.setText(
                f"Doanh thu hóa đơn dịch vụ: {tong_hoa_don:,.0f} VNĐ"
            )

            self.tong.setText(
                f"Tổng doanh thu: {tong_tien:,.0f} VNĐ"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )

        finally:
            conn.close()

    # Xem chi tiết doanh thu
    def xem_chi_tiet(self):
        dong = self.bang.currentRow()

        if dong < 0:
            QMessageBox.warning(
                self, "Thông báo",
                "Hãy chọn một giao dịch cần xem!"
            )
            return

        nguon = self.bang.item(dong, 0).text()
        ma = self.bang.item(dong, 1).text()

        conn = get_connection()
        cursor = conn.cursor()

        try:
            dialog = QDialog(self)
            dialog.resize(750, 500)

            layout = QVBoxLayout()

            if nguon == "Phiên sử dụng":
                cursor.execute("""
                    SELECT
                        ps.MaPhien,
                        kh.ID,
                        kh.HoTen,
                        mt.MaMT,
                        ps.ThoiGianBatDau,
                        ps.ThoiGianKetThuc,
                        ps.TongThoiGian,
                        ps.DonGiaApDung,
                        ps.SoTienTru
                    FROM PhienSuDung ps
                    JOIN KhachHang kh ON ps.ID = kh.ID
                    JOIN MayTinh mt ON ps.MaMT = mt.MaMT
                    WHERE ps.MaPhien = ?
                """, (ma,))

                row = cursor.fetchone()

                if row is None:
                    QMessageBox.warning(
                        self, "Thông báo",
                        "Không tìm thấy phiên sử dụng!"
                    )
                    return

                title = QLabel("CHI TIẾT PHIÊN SỬ DỤNG")
                title.setStyleSheet(
                    "font-size: 20px; font-weight: bold;"
                )
                layout.addWidget(title)

                thong_tin = [
                    ("Mã phiên", row[0]),
                    ("Mã khách hàng", row[1]),
                    ("Tên khách hàng", row[2]),
                    ("Mã máy tính", row[3]),
                    ("Thời gian bắt đầu", row[4]),
                    ("Thời gian kết thúc", row[5]),
                    ("Tổng thời gian (phút)", row[6]),
                    ("Đơn giá áp dụng (VNĐ/giờ)", row[7]),
                    ("Số tiền trừ (VNĐ)", row[8])
                ]

                for ten, gia_tri in thong_tin:
                    if isinstance(gia_tri, datetime):
                        gia_tri = gia_tri.strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )

                    if gia_tri is None:
                        gia_tri = ""

                    layout.addWidget(
                        QLabel(f"{ten}: {gia_tri}")
                    )

            else:
                cursor.execute("""
                    SELECT
                        hd.MaHD,
                        kh.ID,
                        kh.HoTen,
                        nv.MaNV,
                        nv.TenNV,
                        hd.ThoiDiemXuat,
                        hd.ThoiDiemThanhToan,
                        hd.TongTien,
                        hd.PhuongThucThanhToan
                    FROM HoaDon hd
                    JOIN KhachHang kh ON hd.ID = kh.ID
                    JOIN NhanVien nv ON hd.MaNV = nv.MaNV
                    WHERE hd.MaHD = ?
                """, (ma,))

                row = cursor.fetchone()

                if row is None:
                    QMessageBox.warning(
                        self, "Thông báo",
                        "Không tìm thấy hóa đơn!"
                    )
                    return

                title = QLabel("CHI TIẾT HÓA ĐƠN DỊCH VỤ")
                title.setStyleSheet(
                    "font-size: 20px; font-weight: bold;"
                )
                layout.addWidget(title)

                thong_tin = [
                    ("Mã hóa đơn", row[0]),
                    ("Mã khách hàng", row[1]),
                    ("Tên khách hàng", row[2]),
                    ("Mã nhân viên", row[3]),
                    ("Tên nhân viên", row[4]),
                    ("Thời điểm xuất", row[5]),
                    ("Thời điểm thanh toán", row[6]),
                    ("Tổng tiền (VNĐ)", row[7]),
                    ("Phương thức thanh toán", row[8])
                ]

                for ten, gia_tri in thong_tin:
                    if isinstance(gia_tri, datetime):
                        gia_tri = gia_tri.strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )

                    if gia_tri is None:
                        gia_tri = ""

                    layout.addWidget(
                        QLabel(f"{ten}: {gia_tri}")
                    )

                layout.addWidget(QLabel("DANH SÁCH DỊCH VỤ"))

                bang_dv = QTableWidget()
                bang_dv.setColumnCount(4)

                bang_dv.setHorizontalHeaderLabels([
                    "Tên dịch vụ",
                    "Số lượng",
                    "Đơn giá",
                    "Thành tiền"
                ])

                cursor.execute("""
                    SELECT
                        dv.TenDV,
                        ct.SoLuong,
                        ct.DonGia,
                        ct.ThanhTien
                    FROM ChiTietHoaDon ct
                    JOIN DichVu dv ON ct.MaDV = dv.MaDV
                    WHERE ct.MaHD = ?
                """, (ma,))

                ds_dv = cursor.fetchall()

                bang_dv.setRowCount(len(ds_dv))

                for i, dv in enumerate(ds_dv):
                    for j, value in enumerate(dv):
                        if isinstance(value, (int, float)):
                            value = f"{value:,.0f}"

                        bang_dv.setItem(
                            i, j,
                            QTableWidgetItem(str(value))
                        )

                bang_dv.resizeColumnsToContents()
                layout.addWidget(bang_dv)

            btn_dong = QPushButton("Đóng")
            btn_dong.clicked.connect(dialog.close)

            layout.addWidget(btn_dong)

            dialog.setLayout(layout)
            dialog.exec()

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
            "BaoCaoDoanhThu.csv",
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
                    "Nguồn doanh thu",
                    "Mã giao dịch",
                    "Thời điểm",
                    "Số tiền"
                ])

                tong_tien = 0
                tong_phien = 0
                tong_hoa_don = 0

                for row in self.du_lieu:
                    nguon, ma, thoi_diem, so_tien = row
                    so_tien = so_tien or 0
                    tong_tien += so_tien

                    if nguon == "Phiên sử dụng":
                        tong_phien += so_tien
                    elif nguon == "Hóa đơn dịch vụ":
                        tong_hoa_don += so_tien

                    writer.writerow([
                        nguon,
                        ma,
                        thoi_diem.strftime("%d/%m/%Y %H:%M:%S"),
                        so_tien
                    ])

                writer.writerow([])
                writer.writerow([
                    "Doanh thu phiên sử dụng",
                    "",
                    "",
                    tong_phien
                ])
                writer.writerow([
                    "Doanh thu hóa đơn dịch vụ",
                    "",
                    "",
                    tong_hoa_don
                ])
                writer.writerow([
                    "Tổng doanh thu",
                    "",
                    "",
                    tong_tien
                ])

            QMessageBox.information(
                self, "Thông báo",
                "Xuất báo cáo thành công!"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi", str(e)
            )


if __name__ == "__main__":#Giáp đẹp trai vcl
    app = QApplication(sys.argv)
    window = BaoCaoDoanhThu()
    window.show()
    sys.exit(app.exec())
