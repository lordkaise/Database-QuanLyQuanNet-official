# QUẢN LÝ QUÁN NET

Giới thiệu
Phần mềm quản lý quán net được xây dựng bằng Python, sử dụng giao diện PyQt6 và cơ sở dữ liệu SQL Server.

Các chức năng chính:
- Quản lý nhân viên.
- Quản lý khách hàng.
- Quản lý dịch vụ.
- Quản lý khu vực máy.
- Quản lý máy tính.
- Quản lý phiên sử dụng máy.
- Quản lý chấm công.
- Quản lý nạp tiền.
- Quản lý hóa đơn.
- Tìm kiếm thông tin.
- Báo cáo doanh thu.
- Báo cáo dịch vụ.
- Báo cáo máy bảo trì.
- Sao lưu dữ liệu ra các file CSV.

 Thư viện cần cài đặt

Chương trình sử dụng các thư viện Python sau:

| Thư viện | Chức năng |
|----------|-----------|
| `PyQt6`  | Xây dựng giao diện đồ họa |
| `pyodbc` | Kết nối và truy vấn SQL Server |

### Cài đặt thư viện

Mở Terminal tại thư mục dự án và chạy lệnh:

pip install PyQt6 pyodbc

Lần lượt chạy file QuanLyQuanNet.sql, import_data.py, main.py. Các lần sau chỉ cần chạy main.py
Nếu máy tính sử dụng tên SQL Server Instance khác, cần thay đổi giá trị `SERVER` cho phù hợp.

Đảm bảo cơ sở dữ liệu `QuanLyQuanNet` đã được tạo và các bảng đã được khởi tạo trước khi chạy chương trình.

|| Lưu ý
- SQL Server Express phải được cài đặt và hoạt động.
- Cần cài đúng ODBC Driver 18 for SQL Server.
- Thông tin kết nối trong `database.py` phải phù hợp với SQL Server trên máy tính.
- Không xóa hoặc đổi tên các file Python trong thư mục `Src` nếu chưa cập nhật các câu lệnh import liên quan.
- Nên sao lưu dữ liệu trước khi thực hiện các thao tác ảnh hưởng đến cơ sở dữ liệu.
