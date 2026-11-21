# KarirTrack — Job Application Tracker & Analytics

Aplikasi full-stack untuk mencatat, memantau progres, menganalisis statistik, dan mengekspor laporan riwayat lamaran kerja (`.xlsx` & `.pdf`) dengan autentikasi **Google Sign-In**.

- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS (dark mode default) + Recharts
- **Backend:** FastAPI + SQLAlchemy 2 (async) + Pydantic v2 + Psycopg 3
- **Database:** PostgreSQL 16 (lokal via Docker, produksi via Neon)
- **Auth:** Google ID token → access token JWT (in-memory, 15 menit) + refresh token httpOnly cookie (7 hari, rotating)
- **Deploy:** satu project Vercel dengan **Vercel Services** (frontend Vite + backend FastAPI, satu domain)

---

## Daftar Isi

1. [Fitur](#fitur)
2. [Struktur Proyek](#struktur-proyek)
3. [Menjalankan Secara Lokal](#menjalankan-secara-lokal)
4. [Environment Variables](#environment-variables)
5. [Database & Migrasi](#database--migrasi)
6. [Testing & Lint](#testing--lint)
7. [Kontrak API](#kontrak-api)
8. [Deploy ke Vercel + Neon](#deploy-ke-vercel--neon)
9. [Catatan Keamanan](#catatan-keamanan)
10. [Troubleshooting](#troubleshooting)

---

## Fitur

- **Google Sign-In** tanpa password, dengan verifikasi ID token di backend.
- **Dashboard KPI:** Total Lamaran, Active Pipeline, Interview Rate, Offering, Rejected, Ghosted.
- **Grafik:** distribusi status lamaran dan proporsi sumber lowongan (portal).
- **CRUD lamaran** lengkap: perusahaan, posisi, status, portal, model kerja, gaji, URL, catatan.
- **Filter & pencarian** berdasarkan kata kunci, status, model kerja, portal, dan rentang tanggal.
- **Penanda follow-up** otomatis untuk lamaran berstatus `Applied`/`Screening` yang tidak diperbarui lebih dari 14 hari.
- **Interview Rate akurat** dihitung dari riwayat status (`application_status_history`), bukan hanya status saat ini.
- **Export laporan** `.xlsx` (data + sheet ringkasan) dan `.pdf` (landscape, siap cetak) sesuai filter aktif.
- **Isolasi tenant ketat:** seluruh query selalu difilter `user_id`; akses lintas tenant mengembalikan `404`.
- **UI responsif** dengan tabel di desktop dan kartu di mobile, plus loading state di setiap aksi.

---

## Struktur Proyek

```text
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py              # Auth guard + filter query
│   │   │   └── v1/                  # auth, applications, analytics, reports
│   │   ├── core/                    # config.py, enums.py, security.py
│   │   ├── db/                      # base.py, session.py
│   │   ├── models/                  # User, JobApplication, StatusHistory
│   │   ├── schemas/                 # Pydantic v2 schemas
│   │   ├── services/                # business logic + excel/pdf generator
│   │   └── main.py                  # FastAPI entrypoint + CORS
│   ├── alembic/                     # Migrasi database (source of truth)
│   ├── tests/                       # Pytest (auth, CRUD, analytics, export)
│   ├── requirements.txt             # Runtime deps (dipakai Vercel)
│   ├── requirements-dev.txt         # + uvicorn, alembic, pytest, ruff
│   └── pyproject.toml               # Konfigurasi ruff & pytest
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, FilterBar, Modal, Tabel, Chart, dll.
│   │   ├── context/                 # AuthContext
│   │   ├── pages/                   # LoginPage, DashboardPage
│   │   ├── services/                # Axios client, interceptor refresh, export
│   │   ├── types/                   # TypeScript interfaces
│   │   └── test/                    # Vitest + Testing Library
│   └── vite.config.ts               # envDir: '..' (membaca .env di root)
├── .github/workflows/ci.yml         # Lint, test, build otomatis
├── vercel.json                      # Vercel Services + rewrites
├── docker-compose.yml               # PostgreSQL lokal
├── .env.example                     # Template environment variables
└── README.md
```

---

## Menjalankan Secara Lokal

### Prasyarat

- Python **3.11+**
- Node.js **20+** dan npm
- PostgreSQL 16 — paling mudah lewat Docker Desktop
- Google OAuth **Web Client ID** dari [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### 1. Clone & siapkan environment

```bash
git clone https://github.com/hayyanjpg/karir-oyyy.git
cd karir-oyyy
cp .env.example .env
```

Isi `.env` minimal:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/karirtrack
DATABASE_URL_DIRECT=postgresql+psycopg://postgres:postgres@localhost:5432/karirtrack
JWT_SECRET_KEY=<random-string-minimal-32-karakter>
GOOGLE_CLIENT_ID=<client-id>.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=<client-id>.apps.googleusercontent.com
```

> Di Google Cloud Console, tambahkan `http://localhost:5173` ke **Authorized JavaScript origins** dan `http://localhost:5173` ke **Authorized redirect URIs** (untuk mode popup cukup origin).

### 2. Jalankan database

```bash
docker compose up -d
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API: <http://localhost:8000/api/v1>
- Swagger UI: <http://localhost:8000/api/docs>
- Health check: <http://localhost:8000/api/health>

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka <http://localhost:5173>. Vite mem-proxy `/api` ke `http://localhost:8000`, jadi tidak perlu konfigurasi CORS tambahan saat development.

---

## Environment Variables

| Variable | Wajib | Contoh / Default | Keterangan |
| --- | --- | --- | --- |
| `APP_ENV` | tidak | `development` | Set `production` saat deploy. |
| `DATABASE_URL` | ya | `postgresql+psycopg://...` | Koneksi aplikasi. Gunakan host **pooled** Neon. |
| `DATABASE_URL_DIRECT` | disarankan | `postgresql+psycopg://...` | Koneksi langsung untuk Alembic (host tanpa `-pooler`). |
| `JWT_SECRET_KEY` | ya | random ≥ 32 karakter | Kunci tanda tangan JWT. |
| `JWT_ALGORITHM` | tidak | `HS256` | Algoritma JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | tidak | `15` | Umur access token. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | tidak | `7` | Umur refresh token. |
| `GOOGLE_CLIENT_ID` | ya | `...apps.googleusercontent.com` | Client ID untuk verifikasi token. |
| `CORS_ORIGINS` | ya | `http://localhost:5173` | Pisahkan dengan koma jika lebih dari satu. |
| `FRONTEND_URL` | tidak | `http://localhost:5173` | URL frontend (dokumentasi/redirect). |
| `COOKIE_SECURE` | produksi | `true` | Wajib `true` di HTTPS. |
| `COOKIE_SAMESITE` | tidak | `lax` | `lax` aman karena frontend & API satu domain. |
| `COOKIE_DOMAIN` | tidak | kosong | Biarkan kosong di Vercel. |
| `COOKIE_PATH` | tidak | `/api/v1/auth` | Refresh cookie hanya dikirim ke endpoint auth. |
| `MAX_EXPORT_ROWS` | tidak | `2000` | Batas baris export (respons Vercel maks 4,5 MB). |
| `VITE_API_BASE_URL` | ya | `/api/v1` | Base URL API untuk frontend. |
| `VITE_GOOGLE_CLIENT_ID` | ya | sama dengan `GOOGLE_CLIENT_ID` | Client ID untuk tombol Google. |

---

## Database & Migrasi

Alembic adalah **satu-satunya sumber kebenaran** skema database.

```bash
cd backend

# Terapkan semua migrasi
alembic upgrade head

# Rollback satu revisi
alembic downgrade -1

# Buat migrasi baru setelah mengubah model
alembic revision --autogenerate -m "add something"
```

Skema awal (`0001_initial_schema`) membuat:

- `users` — profil Google + `token_version` untuk revokasi sesi.
- `job_applications` — data lamaran dengan check constraint untuk `status`, `work_model`, dan `job_portal`, plus index komposit per tenant.
- `application_status_history` — jejak perubahan status, dipakai untuk Interview Rate.
- Trigger `updated_at` otomatis.

> `DATABASE_URL_DIRECT` dipakai Alembic agar DDL tidak melewati connection pooler Neon.

---

## Testing & Lint

### Backend

Butuh PostgreSQL yang berjalan (CI menyediakan service container).

```bash
cd backend
# Windows
.venv\Scripts\activate

ruff check .
ruff format --check .
pytest -v
```

Test di `backend/tests/` mencakup:

- Auth guard `401` tanpa token, login Google (mock), refresh, logout.
- Create/list/detail/update/delete lamaran.
- Validasi payload (enum status, work model, portal, URL, tanggal).
- Isolasi antar user (list kosong, detail/patch/delete lintas tenant → `404`).
- Filter, pagination, status history, dan Interview Rate.
- Export `.xlsx` & `.pdf` (status `200`, `content-type` benar, file valid).
- CORS `Content-Disposition` terekspos untuk download di browser.

### Frontend

```bash
cd frontend
npm run lint
npm run test:run
npm run build
```

---

## Kontrak API

Base URL: `/api/v1` · Autentikasi: `Authorization: Bearer <access_token>`

| Method | Endpoint | Keterangan |
| --- | --- | --- |
| `POST` | `/auth/google` | Tukar Google credential → access token + refresh cookie. |
| `POST` | `/auth/refresh` | Rotasi access token dari refresh cookie. |
| `POST` | `/auth/logout` | Revokasi sesi (`token_version++`) + hapus cookie. |
| `GET` | `/auth/me` | Profil user aktif. |
| `GET` | `/applications` | List + filter + pagination + sorting. |
| `POST` | `/applications` | Buat lamaran baru. |
| `GET` | `/applications/{id}` | Detail lamaran. |
| `PATCH` | `/applications/{id}` | Update parsial (mencatat riwayat status). |
| `DELETE` | `/applications/{id}` | Hapus lamaran. |
| `GET` | `/analytics/summary` | KPI, distribusi status/portal, daftar follow-up. |
| `GET` | `/reports/export?format=xlsx\|pdf` | Unduh laporan sesuai filter aktif. |

Query filter yang didukung: `search`, `status`, `work_model`, `job_portal`, `start_date`, `end_date`, `page`, `page_size`, `sort`, `order`.

---

## Deploy ke Vercel + Neon

Deploy memakai **satu project Vercel** dengan dua service:

- `frontend` — Vite (static build)
- `backend` — FastAPI (Vercel Function)

`vercel.json` sudah mengarahkan `/api/*` ke backend dan sisanya ke frontend, sehingga cookie refresh tetap same-origin.

### 1. Siapkan Neon (gratis)

1. Buat project di [Neon](https://console.neon.tech).
2. Buat branch: `production`, `development`, `test`.
3. Salin connection string dari branch `production`:
   - **Pooled** (host mengandung `-pooler`) → `DATABASE_URL`
   - **Direct** (host tanpa `-pooler`) → `DATABASE_URL_DIRECT`
4. Tambahkan `?sslmode=require` bila belum ada.

### 2. Jalankan migrasi ke Neon

```bash
cd backend
# set DATABASE_URL_DIRECT ke connection string direct Neon
alembic upgrade head
```

### 3. Import repo ke Vercel

1. **Add New → Project**, pilih repo `karir-oyyy`.
2. Vercel membaca `vercel.json` dan menampilkan dua service.
3. Tambahkan environment variables (Production + Preview):

```env
APP_ENV=production
DATABASE_URL=<pooled-neon-url>
DATABASE_URL_DIRECT=<direct-neon-url>
JWT_SECRET_KEY=<random-32+-chars>
GOOGLE_CLIENT_ID=<client-id>
CORS_ORIGINS=https://karir-oyyy.vercel.app
FRONTEND_URL=https://karir-oyyy.vercel.app
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
MAX_EXPORT_ROWS=2000
VITE_API_BASE_URL=/api/v1
VITE_GOOGLE_CLIENT_ID=<client-id>
```

4. Deploy.
5. Tambahkan domain Vercel (`https://karir-oyyy.vercel.app`) ke **Authorized JavaScript origins** di Google Cloud Console.
6. Smoke test: login → tambah lamaran → filter → export Excel & PDF → refresh halaman (sesi harus pulih dari cookie).

> Catatan Vercel Hobby: fungsi default 10 detik (di `vercel.json` dinaikkan ke 60), respons maksimum 4,5 MB, dan paket Hobby hanya untuk penggunaan non-komersial.

---

## Catatan Keamanan

- Access token **tidak** disimpan di `localStorage`; hanya di memori tab.
- Refresh token disimpan di cookie `httpOnly` + `Secure` (produksi) + `SameSite=Lax`, path dibatasi ke `/api/v1/auth`.
- Refresh token **rotating**: setiap refresh menerbitkan token baru.
- Logout menaikkan `users.token_version`, sehingga seluruh token lama langsung ditolak.
- Setiap endpoint terproteksi memakai dependency `get_current_user`.
- Semua query lamaran memfilter `user_id`; akses data user lain → `404` (bukan `403`) agar keberadaan data tidak bocor.
- `JWT_SECRET_KEY` dan `GOOGLE_CLIENT_ID` dibaca dari environment, tidak pernah di-hardcode.
- Filter `search` meng-escape karakter `%`, `_`, dan `\` sebelum `ILIKE`.

---

## Troubleshooting

| Gejala | Penyebab umum | Solusi |
| --- | --- | --- |
| `401 Not authenticated` terus-menerus | Access token kedaluwarsa & refresh gagal | Pastikan cookie `karirtrack_refresh` terkirim (`COOKIE_SECURE=true` hanya di HTTPS) dan `COOKIE_PATH=/api/v1/auth`. |
| Login Google error `origin_mismatch` | Origin belum terdaftar | Tambahkan URL aplikasi ke Authorized JavaScript origins. |
| `alembic upgrade head` gagal connect | Memakai host pooled | Gunakan `DATABASE_URL_DIRECT`. |
| Export `413` | Lebih dari `MAX_EXPORT_ROWS` | Persempit filter atau naikkan batas (perhatikan limit respons Vercel). |
| `Tidak dapat terhubung ke server` | `VITE_API_BASE_URL` salah | Gunakan `/api/v1` (relatif) di produksi. |
| Build frontend gagal di CI | `package-lock.json` tidak sinkron | Jalankan `npm install` lalu commit lockfile. |
