from pathlib import Path
from datetime import datetime, date
import pyodbc
import csv

# Sua SERVER cho dung voi ten instance SQL Server tren may.
SERVER = r".\SQLEXPRESS"
DATABASE = "QuanLyQuanNet"
DRIVER = "ODBC Driver 18 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)

# Bang cha truoc, bang con sau.
IMPORT_CONFIG = [
    ("NhanVien.csv", "NhanVien",
     ["MaNV", "TenNV", "NgaySinh", "DiaChi", "GioiTinh", "MucLuong", "ChucVu", "SDT"]),

    ("KhuVucMay.csv", "KhuVucMay",
     ["MaKV", "TenKhuVuc", "CauHinh", "GiaTienGio"]),

    ("KhachHang.csv", "KhachHang",
     ["ID", "HoTen", "LoaiTK", "TongTienDaNap", "SoDu","SDT"]),

    ("DichVu.csv", "DichVu",
     ["MaDV", "TenDV", "PhanLoai", "GiaTien", "SoLuong"]),

    ("MayTinh.csv", "MayTinh",
     ["MaMT", "MaKV", "TrangThai"]),

    ("ChamCong.csv", "ChamCong",
     ["MaChamCong", "MaNV", "ThoiDiemChamCong"]),

    ("GiaoDichNapTien.csv", "GiaoDichNapTien",
     ["MaGiaoDich", "ID", "MaNV", "ThoiDiemNap", "SoTienNap"]),

    ("PhienSuDung.csv", "PhienSuDung",
     ["MaPhien", "ID", "MaMT", "ThoiGianBatDau", "ThoiGianKetThuc",
      "TongThoiGian", "DonGiaApDung", "SoTienTru"]),

    ("HoaDon.csv", "HoaDon",
     ["MaHD", "ID", "MaNV", "ThoiDiemXuat", "TongTien",
      "TrangThaiThanhToan", "PhuongThucThanhToan", "ThoiDiemThanhToan"]),

    ("ChiTietHoaDon.csv", "ChiTietHoaDon",
     ["MaHD", "MaDV", "SoLuong", "DonGia", "ThanhTien"]),
]

def clean_value(value):
    if value == "":
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    if isinstance(value, (datetime, date)):
        return value
    return value


def read_csv(file_path, expected_columns):
    if not file_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {file_path}")

    rows = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)

        if headers and headers[0].strip().upper() == "STT":
            headers = headers[1:]

        headers = [h.strip() for h in headers]

        if headers != expected_columns:
            raise ValueError(
                f"Sai cot trong {file_path.name}.\n"
                f"Can: {expected_columns}\n"
                f"Dang co: {headers}"
            )

        for row in reader:
            if row and row[0].strip().isdigit() and len(row) == len(expected_columns) + 1:
                row = row[1:]

            if not any(value.strip() for value in row):
                continue

            values = [value.strip() if value.strip() else None for value in row]

            if len(values) != len(expected_columns):
                raise ValueError(f"Sai so cot trong {file_path.name}: {row}")

            rows.append(tuple(values))

    return rows

def import_table(cursor, data_folder, file_name, table_name, columns):
    rows = read_csv(data_folder / file_name, columns)
    if not rows:
        print(f"[BO QUA] {file_name}: khong co du lieu.")
        return

    col_sql = ", ".join(f"[{col}]" for col in columns)
    marks = ", ".join("?" for _ in columns)
    sql = f"INSERT INTO [{table_name}] ({col_sql}) VALUES ({marks})"

    cursor.executemany(sql, rows)
    print(f"[OK] {table_name}: {len(rows)} dong.")


def main():
    project_folder = Path(__file__).resolve().parent.parent
    data_folder = project_folder / "data"

    if not data_folder.exists():
        print(f"Khong tim thay thu muc data: {data_folder}")
        return

    connection = None
    try:
        connection = pyodbc.connect(CONNECTION_STRING)
        connection.autocommit = False
        cursor = connection.cursor()
        print(f"Da ket noi {DATABASE}.\n")

        for file_name, table_name, columns in IMPORT_CONFIG:
            import_table(cursor, data_folder, file_name, table_name, columns)
            connection.commit()

        cursor.close()
        connection.close()
        print("\nDA IMPORT XONG CAC FILE EXCEL.")

    except Exception as error:
        if connection is not None:
            connection.rollback()
            connection.close()
        print("\nIMPORT THAT BAI!")
        print("Chi tiet loi:", error)
        print("Kiem tra ten instance SQL Server, ten cot, khoa ngoai "
              "va xem cac bang da co du lieu tu truoc chua.")


if __name__ == "__main__":
    main()
