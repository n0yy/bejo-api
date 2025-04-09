# Bejo API

API untuk Bejo, asisten AI PT Bintang Toedjoe yang dapat membantu menjawab pertanyaan tentang perusahaan.

## Fitur

- **Autentikasi Pengguna**: Registrasi dan login dengan JWT
- **Chatbot AI**: Integrasi dengan Gemini untuk menjawab pertanyaan
- **Caching dengan Redis**: Mempertahankan performa tinggi
- **Vektor Database dengan Pinecone**: Pencarian similarity untuk konteks

## Cara Menjalankan Aplikasi

### Cara 1: Tanpa Docker

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Buat file `.env` dari `.env.example` dan isi dengan kredensial yang diperlukan

3. Pastikan Redis berjalan:

   - **Ubuntu**: `sudo service redis-server start`
   - **Windows**: Jalankan Redis Windows service
   - **MacOS**: `brew services start redis`

4. Jalankan server:

```bash
uvicorn app.main:app --reload
```

### Cara 2: Dengan Docker

1. Buat file `.env` dari `.env.example` dan isi dengan kredensial yang diperlukan

2. Pastikan file kredensial Firebase tersedia (biasanya `firebase-credentials.json`)

3. Build dan jalankan dengan Docker Compose:

```bash
docker-compose up -d
```

4. Untuk melihat logs:

```bash
docker-compose logs -f api
```

5. Untuk menghentikan aplikasi:

```bash
docker-compose down
```

## Akses API

- API Documentation: http://localhost:8000/docs
- API Endpoints:
  - POST `/auth/register`: Registrasi pengguna baru
  - POST `/auth/login`: Login pengguna
  - POST `/api/asking`: Tanyakan pertanyaan ke Bejo

## Struktur Project

```
bejo-api/
├── app/
│   ├── auth/
│   │   ├── models.py       # Model data untuk autentikasi
│   │   ├── utils.py        # Fungsi utilitas (hash password, JWT)
│   │   ├── database.py     # Fungsi interaksi database
│   │   ├── register.py     # Endpoint registrasi
│   │   ├── login.py        # Endpoint login
│   │   ├── dependencies.py # Dependency untuk autentikasi
│   │   └── __init__.py     # Inisialisasi modul auth
│   ├── main.py             # Aplikasi FastAPI utama
│   ├── ai.py               # Integrasi AI (Gemini & Pinecone)
│   └── firebase.py         # Konfigurasi Firebase
├── requirements.txt        # Dependency Python
├── .env.example           # Contoh variabel lingkungan
├── Dockerfile             # Konfigurasi Docker
├── docker-compose.yml     # Konfigurasi Docker Compose
└── .dockerignore          # File yang diabaikan Docker
```
