# Visualisasi dataset E-Commerce (Streamlit)

Instruksi singkat untuk menjalankan aplikasi visualisasi yang terhubung ke database Supabase.

---

## Penjelasan Modul/Library yang Digunakan

| Library | Fungsi |
|---------|--------|
| **streamlit** | Framework web app untuk membuat dashboard interaktif dengan Python. Otomatis render UI dari kode Python tanpa perlu HTML/CSS/JS. |
| **pandas** | Library untuk manipulasi dan analisis data (DataFrame). Digunakan untuk memproses hasil query SQL sebelum divisualisasi. |
| **sqlalchemy** | ORM (Object Relational Mapper) dan toolkit database. Berfungsi sebagai "jembatan" antara Python dan PostgreSQL — mengelola koneksi, pooling, dan eksekusi query dengan aman. |
| **psycopg2-binary** | Driver PostgreSQL untuk Python. SQLAlchemy membutuhkan driver ini untuk berkomunikasi dengan database Postgres/Supabase. |
| **python-dotenv** | Membaca variabel environment dari file `.env`. Digunakan untuk menyimpan `DATABASE_URL` agar tidak hardcode credential di kode. |
| **altair** | Library visualisasi deklaratif. Digunakan untuk membuat chart (line, bar, dll) dengan syntax yang bersih dan mudah dibaca. |

---

## Persyaratan
- Python 3.8+ tersedia
- Akses internet untuk menghubungkan ke Supabase
- Supabase project dengan tabel: `customers`, `products`, `orders`, `order_items`, `product_reviews`

## Langkah Konfigurasi

### PENTING: Gunakan Session Pooler (bukan Direct Connection)

Jaringan rumah/kampus biasanya hanya support **IPv4**, sedangkan Supabase direct connection membutuhkan **IPv6**. Solusinya adalah menggunakan **Session Pooler**.

File `.env` sudah dikonfigurasi dengan Session Pooler:
```
DATABASE_URL=postgresql://postgres.lokizaoluolkdetelmfd:PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

**Perbedaan:**
| Metode | Host | IPv4 Support |
|--------|------|-------------|
| Direct Connection | `db.lokizaoluolkdetelmfd.supabase.co` | ❌ Tidak |
| Session Pooler | `aws-1-ap-southeast-1.pooler.supabase.com` | ✅ Ya |

## Instal & Jalankan

**1. Install dependency (PowerShell):**
```powershell
cd "d:\Data\Documents\Semester 5\Administrasi Basis Data\Tugas Besar\visualisasi"
pip install -r requirements.txt
```

**2. Jalankan aplikasi:**
```powershell
streamlit run app.py
```

Aplikasi akan terbuka di browser: `http://localhost:8501`

## Fitur Dashboard

| Fitur | Deskripsi |
|-------|----------|
| **Overview Metrics** | Jumlah customers, orders, total revenue, rata-rata rating |
| **Orders per Day** | Line chart tren pesanan harian |
| **Top 10 Products** | Bar chart produk dengan revenue tertinggi |
| **Rating Distribution** | Bar chart distribusi rating 1-5 |
| **Table Preview** | Lihat & download CSV untuk setiap tabel |

---

## Troubleshooting

**Error: "could not translate host name"**
→ Pastikan `.env` menggunakan Session Pooler (host: `aws-1-ap-southeast-1.pooler.supabase.com`), bukan direct connection.

**Error: "password authentication failed"**
→ Cek ulang password di `.env`. Password Supabase case-sensitive.

**Error: "connection refused"**
→ Pastikan project Supabase tidak dalam status paused. Buka dashboard Supabase untuk mengaktifkan kembali.
