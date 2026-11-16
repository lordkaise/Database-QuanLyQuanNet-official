
-- 1. Tao database
IF DB_ID('QuanLyQuanNet') IS NULL
    CREATE DATABASE QuanLyQuanNet;
GO

USE QuanLyQuanNet;
GO

-- 2. Bang NhanVien
CREATE TABLE NhanVien (
    MaNV VARCHAR(10) PRIMARY KEY,
    TenNV NVARCHAR(100),
    NgaySinh DATE,
    DiaChi NVARCHAR(200),
    GioiTinh NVARCHAR(10),
    MucLuong DECIMAL(18,2),
    ChucVu NVARCHAR(50),
    SDT VARCHAR(15)
);

-- 3. Bang ChamCong
CREATE TABLE ChamCong (
    MaChamCong VARCHAR(10) PRIMARY KEY,
    MaNV VARCHAR(10),
    ThoiDiemChamCong DATETIME,
    FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
);

-- 4. Bang KhuVucMay
CREATE TABLE KhuVucMay (
    MaKV VARCHAR(10) PRIMARY KEY,
    TenKhuVuc NVARCHAR(100),
    CauHinh NVARCHAR(200),
    GiaTienGio DECIMAL(18,2)
);

-- 5. Bang MayTinh
CREATE TABLE MayTinh (
    MaMT VARCHAR(10) PRIMARY KEY,
    MaKV VARCHAR(10),
    TrangThai NVARCHAR(30),
    FOREIGN KEY (MaKV) REFERENCES KhuVucMay(MaKV)
);

-- 6. Bang KhachHang
CREATE TABLE KhachHang (
    ID VARCHAR(20) PRIMARY KEY,
    HoTen NVARCHAR(100),
    LoaiTK NVARCHAR(50),
    TongTienDaNap DECIMAL(18,2),
    SoDu DECIMAL(18,2),
    SDT VARCHAR(15)
);

-- 7. Bang GiaoDichNapTien
CREATE TABLE GiaoDichNapTien (
    MaGiaoDich VARCHAR(10) PRIMARY KEY,
    ID VARCHAR(20),
    MaNV VARCHAR(10),
    ThoiDiemNap DATETIME,
    SoTienNap DECIMAL(18,2),
    FOREIGN KEY (ID) REFERENCES KhachHang(ID),
    FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
);

-- 8. Bang PhienSuDung
CREATE TABLE PhienSuDung (
    MaPhien VARCHAR(10) PRIMARY KEY,
    ID VARCHAR(20),
    MaMT VARCHAR(10),
    ThoiGianBatDau DATETIME,
    ThoiGianKetThuc DATETIME,
    TongThoiGian INT,
    DonGiaApDung DECIMAL(18,2),
    SoTienTru DECIMAL(18,2),
    FOREIGN KEY (ID) REFERENCES KhachHang(ID),
    FOREIGN KEY (MaMT) REFERENCES MayTinh(MaMT)
);

-- 9. Bang DichVu
CREATE TABLE DichVu (
    MaDV VARCHAR(10) PRIMARY KEY,

    TenDV NVARCHAR(100),
    PhanLoai NVARCHAR(50),
    GiaTien DECIMAL(18,2),
    SoLuong INT
);

-- 10. Bang HoaDon
CREATE TABLE HoaDon (
    MaHD VARCHAR(10) PRIMARY KEY,
    ID VARCHAR(20),
    MaNV VARCHAR(10),
    ThoiDiemXuat DATETIME,
    TongTien DECIMAL(18,2),
    TrangThaiThanhToan NVARCHAR(30),
    PhuongThucThanhToan NVARCHAR(30),
    ThoiDiemThanhToan DATETIME,
    FOREIGN KEY (ID) REFERENCES KhachHang(ID),
    FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
);

-- 11. Bang ChiTietHoaDon
CREATE TABLE ChiTietHoaDon (
    MaHD VARCHAR(10),
    MaDV VARCHAR(10),
    SoLuong INT,
    DonGia DECIMAL(18,2),
    ThanhTien DECIMAL(18,2),
    PRIMARY KEY (MaHD, MaDV),
    FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD),
    FOREIGN KEY (MaDV) REFERENCES DichVu(MaDV)
);
GO
