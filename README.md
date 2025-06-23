# BeKind Internal

Ứng dụng nội bộ dựa trên Streamlit với xác thực người dùng sử dụng Supabase.

## Tính năng

- Xác thực người dùng qua số điện thoại
- Đăng ký và đăng nhập tài khoản
- Quản lý dữ liệu lưu trữ cục bộ
- Tích hợp Supabase để lưu trữ dữ liệu

## Cài đặt

1. **Clone repository**

   ```bash
   git clone <repository-url>
   cd bekind-internal
   ```

2. **Cài đặt các gói phụ thuộc**

   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình biến môi trường**

   - Sao chép `.env.example` thành `.env`
   - Điền thông tin xác thực Supabase của bạn:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     ```

4. **Thiết lập cơ sở dữ liệu Supabase**
   Tạo bảng có tên `accounts` với cấu trúc sau:

   ```sql
   CREATE TABLE accounts (
     id SERIAL PRIMARY KEY,
     phone_number VARCHAR(20) UNIQUE NOT NULL,
     name VARCHAR(100),
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

5. **Chạy ứng dụng**
   ```bash
   streamlit run main.py
   ```

## Sử dụng

1. **Đăng nhập/Đăng ký**: Nhập số điện thoại của bạn

   - Nếu tài khoản tồn tại, bạn sẽ được đăng nhập
   - Nếu tài khoản không tồn tại, nhấp vào "Đăng ký" để tạo tài khoản mới

2. **Bảng điều khiển**: Sau khi đăng nhập, bạn sẽ thấy bảng điều khiển chính với:
   - Thông báo chào mừng kèm thông tin tài khoản
   - Chức năng đăng xuất
   - Chi tiết tài khoản

## Cấu trúc dự án

```
bekind-internal/
├── main.py                 # Điểm khởi chạy ứng dụng chính
├── config.py               # Cài đặt cấu hình
├── requirements.txt        # Các gói phụ thuộc Python
├── lib/
│   ├── __init__.py
│   ├── local_storage.py    # Quản lý bộ nhớ cục bộ
│   └── supabase.py         # Thiết lập kết nối Supabase
├── page/
│   ├── __init__.py
│   └── login_page.py       # Trang đăng nhập/đăng ký
└── service/
    ├── __init__.py
    ├── base_srv.py         # Lớp dịch vụ cơ sở
    └── account_srv.py      # Dịch vụ tài khoản
```

## Phát triển

Ứng dụng tuân theo mô hình kiến trúc sạch:

- **Services**: Xử lý logic nghiệp vụ và thao tác cơ sở dữ liệu
- **Pages**: Các thành phần giao diện người dùng Streamlit
- **Lib**: Thư viện tiện ích và tích hợp dịch vụ bên ngoài

## Phụ thuộc

Các phụ thuộc chính bao gồm:

- `streamlit`: Framework phát triển ứng dụng web
- `supabase`: Client cơ sở dữ liệu
- `streamlit-local-storage`: Tích hợp bộ nhớ cục bộ của trình duyệt
- `python-dotenv`: Quản lý biến môi trường
