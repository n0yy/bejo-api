# Gunakan base image Python official yang ringan
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Hindari buffer output Python
ENV PYTHONUNBUFFERED=1 \
    # Hindari pembuatan file bytecode
    PYTHONDONTWRITEBYTECODE=1 \
    # Aktifkan mode optimisasi Python
    PYTHONOPTIMIZE=1 \
    # Pastikan pip cache tidak disimpan dalam image
    PIP_NO_CACHE_DIR=1 \
    # Nonaktifkan perintah interaktif pada pip
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Salin requirements.txt terlebih dahulu untuk memanfaatkan layer caching
COPY requirements.txt .

# Upgrade pip dan install dependensi
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage kedua untuk membuat image yang lebih kecil
FROM python:3.11-slim AS final

# Set working directory
WORKDIR /app

# Tetapkan variabel lingkungan
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

# Buat user non-root untuk keamanan
RUN addgroup --system app && \
    adduser --system --group app && \
    mkdir -p /app/logs && \
    chown -R app:app /app

# Salin paket Python dari stage sebelumnya
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Salin kode aplikasi
COPY --chown=app:app . .

# Beralih ke user non-root
USER app

# Ekspos port yang digunakan oleh aplikasi (default FastAPI = 8000)
EXPOSE 8000

# Perintah untuk menjalankan aplikasi menggunakan Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Healthcheck untuk memastikan aplikasi berjalan dengan baik
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1 