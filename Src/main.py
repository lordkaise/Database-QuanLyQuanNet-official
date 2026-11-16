
import sys
from sao_luu import sao_luu_du_lieu

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from nhan_vien import QuanLyNhanVien
from khach_hang import QuanLyKhachHang
from dich_vu import QuanLyDichVu
from khu_vuc_may import QuanLyKhuVuc
from may_tinh import QuanLyMayTinh
from nap_tien import NapTien
from phien_su_dung import PhienSuDung
from cham_cong import ChamCong
from hoa_don import HoaDon

from tim_kiem import TimKiem
from bao_cao_doanh_thu import BaoCaoDoanhThu
from bao_cao_dich_vu import BaoCaoDichVu
from bao_cao_may_bao_tri import BaoCaoMayBaoTri


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QUẢN LÝ QUÁN NET")
        self.resize(700, 750)

        self.cua_so = {}

        layout = QVBoxLayout()

        title = QLabel("HỆ THỐNG QUẢN LÝ QUÁN NET")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )
        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(title)

        # Quản lý
        nhom_quan_ly = QGroupBox("QUẢN LÝ")
        ql_layout = QGridLayout()

        self.them_nut(
            ql_layout, "Nhân viên",
            QuanLyNhanVien, 0, 0
        )
        self.them_nut(
            ql_layout, "Khách hàng",
            QuanLyKhachHang, 0, 1
        )
        self.them_nut(
            ql_layout, "Dịch vụ",
            QuanLyDichVu, 1, 0
        )
        self.them_nut(
            ql_layout, "Khu vực máy",
            QuanLyKhuVuc, 1, 1
        )
        self.them_nut(
            ql_layout, "Máy tính",
            QuanLyMayTinh, 2, 0
        )

        nhom_quan_ly.setLayout(ql_layout)
        layout.addWidget(nhom_quan_ly)

        # Vận hành
        nhom_van_hanh = QGroupBox("VẬN HÀNH")
        vh_layout = QGridLayout()

        self.them_nut(
            vh_layout, "Phiên sử dụng",
            PhienSuDung, 0, 0
        )
        self.them_nut(
            vh_layout, "Chấm công",
            ChamCong, 0, 1
        )

        nhom_van_hanh.setLayout(vh_layout)
        layout.addWidget(nhom_van_hanh)

        # Giao dịch
        nhom_giao_dich = QGroupBox("GIAO DỊCH")
        gd_layout = QGridLayout()

        self.them_nut(
            gd_layout, "Nạp tiền",
            NapTien, 0, 0
        )
        self.them_nut(
            gd_layout, "Hóa đơn",
            HoaDon, 0, 1
        )

        nhom_giao_dich.setLayout(gd_layout)
        layout.addWidget(nhom_giao_dich)

        # Tìm kiếm
        nhom_tim_kiem = QGroupBox("TÌM KIẾM")
        tk_layout = QVBoxLayout()

        self.them_nut(
            tk_layout, "Tìm kiếm thông tin",
            TimKiem
        )

        nhom_tim_kiem.setLayout(tk_layout)
        layout.addWidget(nhom_tim_kiem)

        # Báo cáo
        nhom_bao_cao = QGroupBox("BÁO CÁO")
        bc_layout = QGridLayout()

        self.them_nut(
            bc_layout, "Báo cáo doanh thu",
            BaoCaoDoanhThu, 0, 0
        )
        self.them_nut(
            bc_layout, "Báo cáo dịch vụ",
            BaoCaoDichVu, 0, 1
        )
        self.them_nut(
            bc_layout, "Máy tính bảo trì",
            BaoCaoMayBaoTri, 1, 0
        )

        nhom_bao_cao.setLayout(bc_layout)
        layout.addWidget(nhom_bao_cao)
        btn_sao_luu = QPushButton("SAO LƯU DỮ LIỆU")
        btn_sao_luu.setMinimumHeight(40)
        btn_sao_luu.clicked.connect(
            lambda: sao_luu_du_lieu(self)
        )

        layout.addWidget(btn_sao_luu)

        # Thoát
        btn_thoat = QPushButton("THOÁT")
        btn_thoat.clicked.connect(self.close)

        layout.addWidget(btn_thoat)

        self.setLayout(layout)

    # Tạo nút mở form
    def them_nut(self, layout, ten, lop, hang=None, cot=None):
        btn = QPushButton(ten)
        btn.setMinimumHeight(40)

        btn.clicked.connect(
            lambda checked=False, l=lop: self.mo_form(l)
        )

        if hang is None:
            layout.addWidget(btn)
        else:
            layout.addWidget(btn, hang, cot)

    # Mở form
    # Mở form
    def mo_form(self, lop):
        ten_lop = lop.__name__

        if ten_lop in self.cua_so:

            cua_so = self.cua_so[ten_lop]

            # Nếu mở lại form máy tính thì tải dữ liệu mới
            if lop is QuanLyMayTinh:
                cua_so.tai_lai()

            cua_so.show()
            cua_so.raise_()
            cua_so.activateWindow()

        else:
            cua_so = lop()

            # Kết nối tín hiệu từ form phiên sử dụng
            if lop is PhienSuDung:
                cua_so.trang_thai_may_changed.connect(
                    self.cap_nhat_may_tinh
                )

            self.cua_so[ten_lop] = cua_so

            cua_so.destroyed.connect(
                lambda: self.cua_so.pop(ten_lop, None)
            )

            cua_so.show()
    # Cập nhật trạng thái máy tính
    def cap_nhat_may_tinh(self):

        # Kiểm tra cửa sổ quản lý máy tính đã được mở chưa
        cua_so = self.cua_so.get("QuanLyMayTinh")

        if cua_so is not None:
            cua_so.tai_lai()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
