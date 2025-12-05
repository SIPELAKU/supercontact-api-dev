# 🚀 FastAPI Project Setup Guide

Dokumentasi ini menjelaskan cara menjalankan project FastAPI mulai dari persiapan virtual environment, instalasi
dependencies, hingga menjalankan server — mendukung **Windows** dan **Linux/MacOS**.

---

## 📦 1. Persyaratan Sistem

Pastikan sudah terpasang:

- Python **3.9+**
- Git

Cek versi Python:

```bash
python --version
# atau
python3 --version
```

---

## 🧰 2. Setup Virtual Environment (.venv)

### 🔹 Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 🔹 Linux / MacOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Jika berhasil, terminal akan menampilkan prefix:

```
(.venv) user@computer:~/project$
```

---

## 📥 3. Install Dependencies

Pastikan `requirements.txt` berisi:

```
fastapi
uvicorn[standard]
dan dependncies lainnya....
```

Lalu jalankan:

### Windows

```bash
pip install -r requirements.txt
```

### Linux / MacOS

```bash
pip3 install -r requirements.txt
```

### Jalankan migrasi database dan seed user dummy

```bash
alembic upgrade head

python -m app.db.seeds.user_seed
```

---

## 🛠️ 4. Menjalankan Server FastAPI

### Windows

```bash
uvicorn app.main:app --reload
```

### Linux / MacOS

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Akses dokumentasi otomatis:

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

---

## 📄 5. Contoh File `main.py`

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "FastAPI is running!"}
```

---

## 🔑 6. Environment Variables (Opsional)

Buat file `.env` untuk menyimpan konfigurasi:

```
PROJECT_NAME=My FastAPI App
SECRET_KEY=your-secret-key
```

---

## 🧹 7. Menonaktifkan Virtual Environment

Cukup jalankan:

```bash
deactivate
```

Berlaku untuk Windows, Linux, dan MacOS.

---

## 🐳 8. (Opsional) Menjalankan Menggunakan Docker

Jika ingin menjalankan lewat Docker:

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

---

## 🎉 Selesai