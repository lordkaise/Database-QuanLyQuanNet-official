
import csv
import io
import os

from pathlib import Path
from tempfile import NamedTemporaryFile

from PyQt6.QtWidgets import QMessageBox

from database import get_connection


def sao_luu_du_lieu(parent=None):
    # Thư mục chứa 10 file CSV
    thu_muc = Path(__file__).resolve().parent.parent / "data"

    if not thu_muc.exists():
        QMessageBox.warning(
            parent, "Thông báo",
            "Không tìm thấy thư mục data!"
        )
        return

    # Danh sách 10 bảng cần sao lưu
    cac_bang = [
        "NhanVien",
        "ChamCong",
        "KhuVucMay",
        "MayTinh",
        "KhachHang",
        "GiaoDichNapTien",
        "PhienSuDung",
        "DichVu",
        "HoaDon",
        "ChiTietHoaDon"
    ]

    conn = None
    cac_file_tam = {}
    du_lieu_cu = {}
    cac_file_da_thay = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Đọc dữ liệu từ SQL Server
        du_lieu_moi = {}

        for bang in cac_bang:
            cursor.execute(f"SELECT * FROM [{bang}]")

            ten_cot = [
                cot[0] for cot in cursor.description
            ]

            rows = cursor.fetchall()

            noi_dung = io.StringIO(newline="")
            writer = csv.writer(noi_dung)

            writer.writerow(ten_cot)

            for row in rows:
                writer.writerow(row)

            du_lieu_moi[bang] = noi_dung.getvalue().encode(
                "utf-8-sig"
            )

        conn.close()
        conn = None

        # Lưu dữ liệu cũ để có thể khôi phục nếu xảy ra lỗi
        for bang in cac_bang:
            duong_dan = thu_muc / f"{bang}.csv"

            if duong_dan.exists():
                du_lieu_cu[bang] = duong_dan.read_bytes()
            else:
                du_lieu_cu[bang] = None

        # Tạo file tạm trước khi ghi đè
        for bang in cac_bang:
            with NamedTemporaryFile(
                mode="wb",
                delete=False,
                dir=thu_muc,
                suffix=".tmp"
            ) as f:
                f.write(du_lieu_moi[bang])
                cac_file_tam[bang] = Path(f.name)

        # Ghi đè 10 file CSV
        for bang in cac_bang:
            duong_dan = thu_muc / f"{bang}.csv"

            os.replace(
                cac_file_tam[bang],
                duong_dan
            )

            cac_file_da_thay.append(bang)

        QMessageBox.information(
            parent,
            "Thông báo",
            "Sao lưu dữ liệu thành công!\n"
            "Đã cập nhật 10 file CSV."
        )

    except Exception as e:
        # Khôi phục các file cũ nếu xảy ra lỗi
        for bang in cac_file_da_thay:
            duong_dan = thu_muc / f"{bang}.csv"
            du_lieu = du_lieu_cu[bang]

            try:
                if du_lieu is None:
                    duong_dan.unlink(missing_ok=True)
                else:
                    duong_dan.write_bytes(du_lieu)
            except Exception:
                pass

        QMessageBox.critical(
            parent,
            "Lỗi sao lưu",
            f"Sao lưu thất bại!\n{str(e)}"
        )

    finally:
        if conn is not None:
            conn.close()

        # Xóa các file tạm còn sót lại
        for file in cac_file_tam.values():
            if file.exists():
                file.unlink()
