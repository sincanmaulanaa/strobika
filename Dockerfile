# 🐍 Gunakan base image ringan
FROM python:3.11-slim-bookworm

# ✅ Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 🚀 Buat working directory
WORKDIR /app

# 🔒 Salin dan install dependency Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 📂 Salin semua source code ke dalam container
COPY . .

# 🗂️ Pastikan direktori upload dan result tersedia
RUN mkdir -p /tmp/uploads /tmp/results /app/static/results

# 🌍 Expose port 8080 (Cloud Run default)
EXPOSE 8080

# 🚦 Jalankan aplikasi Flask dengan Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
