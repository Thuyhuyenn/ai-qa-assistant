# Sử dụng base image Python chính thức
FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống phục vụ cho Playwright headless browser
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgl1 \
    libharfbuzz0b \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpcre3 \
    libpixman-1-0 \
    libpng16-16 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt Playwright bên trong container
RUN playwright install chromium

# Copy toàn bộ mã nguồn dự án vào container
COPY . .

# Mở cổng mặc định cho Streamlit Dashboard
EXPOSE 8501

# Lệnh mặc định khởi chạy giao diện Web Dashboard
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]