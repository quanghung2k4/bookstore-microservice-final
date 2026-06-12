FROM python:3.10-slim

WORKDIR /app

# 1. Cài đặt các thư viện hệ thống cần thiết (PyTorch cần libgomp1 để tính toán đa luồng)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc ca-certificates libgomp1 \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. TỐI ƯU AI: Cài đặt bản PyTorch rút gọn cho CPU trước. 
# Điều này giúp giảm dung lượng Docker image từ ~4GB xuống còn vài trăm MB.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 3. Cài đặt các package còn lại trong dự án
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Giữ lại đoạn vá lỗi Underscore của bạn (nếu chưa tiện đổi tên container ở docker-compose)
RUN python -c "\
import django.http.request as m, inspect; \
src = inspect.getfile(m); \
code = open(src).read(); \
open(src, 'w').write(code.replace('raise DisallowedHost(msg)', 'pass  # allow underscore hosts'))"

COPY . .

EXPOSE 8007

# 5. THAY THẾ RUNSERVER: Sử dụng Gunicorn với số lượng worker phù hợp để xử lý 
# song song các request gọi tới mô hình AI mà không bị nghẽn luồng.
CMD ["sh", "-c", "python manage.py migrate --noinput; gunicorn cấu_hình_dự_án_của_bạn.wsgi:application --bind 0.0.0.0:8007 --workers 2 --timeout 60"]