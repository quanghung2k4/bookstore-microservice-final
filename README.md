# E-commerce Microservices Platform

Một hệ thống thương mại điện tử hoàn chỉnh được xây dựng với kiến trúc microservices sử dụng Django và React.

## 🏗️ Kiến trúc hệ thống

### Services
- **API Gateway** (Port 8000) - Điều hướng và proxy requests
- **Product Service** (Port 8001) - Quản lý sản phẩm và danh mục
- **Cart Service** (Port 8002) - Quản lý giỏ hàng
- **Order Service** (Port 8003) - Xử lý đơn hàng và checkout
- **User Service** (Port 8004) - Quản lý người dùng và xác thực
- **Payment Service** (Port 8005) - Xử lý thanh toán
- **Frontend Service** (Port 3000) - Giao diện React

### Tính năng chính
- ✅ Quản lý sản phẩm với danh mục, thương hiệu, variants
- ✅ Hệ thống giỏ hàng với quản lý số lượng
- ✅ Quy trình checkout hoàn chỉnh với kiểm tra tồn kho
- ✅ Quản lý đơn hàng và lịch sử
- ✅ Hệ thống thanh toán mô phỏng
- ✅ Giao diện người dùng responsive
- ✅ Quản lý tồn kho tự động
- ✅ Xóa giỏ hàng sau khi checkout thành công

## 🚀 Cài đặt và chạy

### Yêu cầu
- Docker và Docker Compose
- Python 3.11+
- Node.js 18+

### Chạy toàn bộ hệ thống
```bash
docker-compose up --build
```

Product service sẽ tự seed dữ liệu mẫu khi database sản phẩm đang rỗng.

### Truy cập ứng dụng
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- Các services: Ports 8001-8005

## 📱 Sử dụng Frontend

### 1. Tạo người dùng
- Điền form tạo user với username, email, tên
- Chọn role: customer, staff, hoặc admin
- Lưu User ID được tạo

### 2. Quản lý giỏ hàng
- Tạo cart mới với User ID
- Thêm sản phẩm vào giỏ từ catalog
- Điều chỉnh số lượng hoặc xóa sản phẩm
- Xem tổng tiền giỏ hàng

### 3. Mua hàng
- Checkout giỏ hàng với User ID và Cart ID
- Hệ thống tự động kiểm tra tồn kho
- Tạo đơn hàng và thanh toán
- Giỏ hàng được xóa sau khi thành công

### 4. Xem chi tiết sản phẩm
- Click "View Details" để xem thông tin đầy đủ
- Xem specifications, variants, tồn kho
- Thêm số lượng tùy chọn vào giỏ

## 🔧 API Endpoints

### Product Service
- `GET /api/products/` - Danh sách sản phẩm (có filter, search)
- `GET /api/products/{id}/` - Chi tiết sản phẩm
- `POST /api/products/{id}/reserve_stock/` - Đặt trước tồn kho
- `POST /api/products/check_stock/` - Kiểm tra tồn kho

### Cart Service  
- `POST /api/carts/` - Tạo giỏ hàng
- `GET /api/carts/{id}/summary/` - Thông tin giỏ hàng
- `POST /api/carts/{id}/items/` - Thêm sản phẩm
- `POST /api/carts/{id}/clear/` - Xóa giỏ hàng

### Order Service
- `POST /api/orders/checkout/` - Checkout giỏ hàng
- `GET /api/orders/` - Danh sách đơn hàng

### User Service
- `POST /api/users/` - Tạo người dùng
- `POST /api/users/login/` - Đăng nhập

### Payment Service
- `GET /api/payments/` - Danh sách thanh toán

## 🛠️ Phát triển

### Cấu trúc thư mục mỗi service
```
service_name/
├── config/          # Django settings
├── app_name/
│   ├── domain/      # Business logic
│   ├── application/ # Use cases
│   ├── infrastructure/ # Models, repositories, clients
│   └── presentation/   # Views, serializers, URLs
├── requirements.txt
└── Dockerfile
```

### Chạy service riêng lẻ
```bash
cd product_service
python manage.py migrate
python manage.py seed_products
python manage.py runserver 8001
```

### Seed dữ liệu mẫu
```bash
cd product_service
python manage.py seed_products
```

### Lưu ý về Docker Compose
`docker compose restart` chỉ khởi động lại container hiện có. Với cấu hình hiện tại, SQLite của từng service được lưu trong Docker volume riêng để không bị mất khi restart/recreate container.

Nếu muốn xóa toàn bộ dữ liệu hiện tại và nạp lại dữ liệu mẫu từ đầu:
```bash
docker compose down -v
docker compose up --build
```

## 🔄 Luồng xử lý Checkout

1. **Kiểm tra user và cart** - Validate user tồn tại và cart không rỗng
2. **Kiểm tra tồn kho** - Gọi Product Service kiểm tra stock
3. **Đặt trước tồn kho** - Reserve stock cho tất cả items
4. **Tạo đơn hàng** - Tính tổng tiền và tạo order
5. **Xử lý thanh toán** - Tạo payment record
6. **Xóa giỏ hàng** - Clear cart sau khi thành công
7. **Rollback nếu lỗi** - Release stock nếu có lỗi xảy ra

## 🎯 Tính năng nâng cao

- **Stock Management**: Tự động quản lý tồn kho với reserve/release
- **Error Handling**: Rollback transaction khi checkout thất bại  
- **Product Details**: Modal xem chi tiết sản phẩm với variants
- **Order History**: Lịch sử đơn hàng với filter theo status
- **Responsive UI**: Giao diện tối ưu cho mobile và desktop
- **Real-time Updates**: Cập nhật giỏ hàng và tồn kho real-time

## 📊 Monitoring

Các service logs được hiển thị trong Docker Compose. Để xem logs:

```bash
docker-compose logs -f [service_name]
```

## 🔐 Bảo mật

- Input validation trên tất cả endpoints
- Error handling với thông báo phù hợp
- Timeout protection cho inter-service calls
- Stock reservation để tránh overselling

---

Hệ thống đã sẵn sàng cho production với đầy đủ tính năng ecommerce cơ bản và có thể mở rộng thêm AI service cho recommendation trong tương lai.
"# bookstore-microservice-final" 
