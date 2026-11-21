# AGENTS.md — Engineering Rules & Execution Guidelines

## 1. Struktur Direktori Monorepo
Patuhi struktur folder berikut secara ketat:
```text
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py      # get_current_user + filter query helpers
│   │   │   └── v1/          # Route handlers (auth.py, applications.py, analytics.py, reports.py)
│   │   ├── core/            # config.py, enums.py, security.py (JWT & Google OAuth verification)
│   │   ├── db/              # session.py, base.py
│   │   ├── models/          # SQLAlchemy models (User, JobApplication, StatusHistory)
│   │   ├── schemas/         # Pydantic v2 request/response schemas
│   │   ├── services/        # Business logic & report generators (excel_service.py, pdf_service.py)
│   │   └── main.py          # FastAPI entrypoint + CORS setup
│   ├── alembic/             # Migrasi database (source of truth, lihat versions/0001_initial_schema.py)
│   ├── tests/               # Pytest unit & integration tests
│   ├── requirements.txt     # Runtime deps (dipakai Vercel)
│   └── requirements-dev.txt # + uvicorn, alembic, pytest, ruff
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components (Navbar, StatusBadge, ApplicationModal, ExportMenu)
│   │   ├── context/         # AuthContext (access token in-memory + refresh)
│   │   ├── pages/           # LoginPage.tsx, DashboardPage.tsx
│   │   ├── services/        # Axios API client & auth interceptors
│   │   ├── types/           # TypeScript interfaces
│   │   ├── test/            # Vitest + Testing Library
│   │   └── App.tsx
│   └── package.json
├── .github/workflows/ci.yml # Automated lint, test & build workflow
├── .env.example
├── docker-compose.yml
├── vercel.json              # Vercel Services (frontend + backend, satu domain)
├── PRD.md
└── AGENTS.md
```

## 2. Aturan Coding & Kualitas (Strict Constraints)
1. **Keamanan & Isolasi Tenant:** DILARANG keras mengembalikan atau memodifikasi data milik `user_id` lain. Setiap endpoint terproteksi wajib menggunakan dependency `get_current_user`.
2. **Validasi Input:** Semua payload masuk di FastAPI wajib divalidasi dengan Pydantic v2 (termasuk validasi enum `status` dan `work_model`).
3. **Penanganan File Download (Frontend):** Saat memanggil `/api/v1/reports/export`, frontend wajib menggunakan `responseType: 'blob'`, membaca header `Content-Disposition` untuk nama file, dan memicu download via temporary `<a>` element lalu membersihkan object URL (`URL.revokeObjectURL`).
4. **UI/UX Standard:**
   - Gunakan tema **Dark Mode** bersih secara default (`bg-slate-950`, card `bg-slate-900`, border `border-slate-800`).
   - Pastikan seluruh halaman responsif (mobile & desktop).
   - Tampilkan *loading state* (spinner/skeleton) saat proses login Google, fetch data, dan generate file laporan berlangsung.
   - Jangan biarkan *hardcoded secrets* atau `GOOGLE_CLIENT_ID` langsung di kode; wajib baca dari `.env` (`VITE_GOOGLE_CLIENT_ID` di frontend, `GOOGLE_CLIENT_ID` & `JWT_SECRET_KEY` di backend).
5. **Autentikasi & Sesi:** Access token JWT hanya disimpan di memori frontend (tidak di `localStorage`). Refresh token wajib berupa cookie `httpOnly`, `Secure` di produksi, `SameSite=Lax`, dengan `path=/api/v1/auth`, dan dirotasi setiap refresh. Logout wajib menaikkan `users.token_version`.
6. **Akses Lintas Tenant:** Kembalikan `404` (bukan `403`) untuk resource milik user lain agar keberadaan data tidak bocor.
7. **Testing Wajib Sebelum Selesai:**
   - Buat test di `backend/tests/test_applications.py` yang menguji: (a) auth guard 401 tanpa token, (b) create & list aplikasi, (c) isolasi antar user, dan (d) endpoint export mengembalikan status 200 dengan `content-type` `.xlsx` dan `.pdf` yang valid.
   - Jalankan `ruff check`, `ruff format --check`, `pytest`, `npm run lint`, `npm run test:run`, dan `npm run build` untuk memastikan nol error kompilasi maupun runtime sebelum menyatakan tugas selesai.

## 3. Urutan Kerja Agent (Step-by-Step)
- **Fase 1:** Inisialisasi struktur folder `backend/` dan `frontend/`, gunakan Alembic (`alembic/versions/0001_initial_schema.py`) sebagai sumber kebenaran migrasi database & buat model SQLAlchemy.
- **Fase 2:** Implementasikan modul autentikasi Google Sign-In (`POST /api/v1/auth/google`), refresh token cookie, dan dependency JWT (`get_current_user`).
- **Fase 3:** Bangun endpoint CRUD `applications` dan `analytics/summary`.
- **Fase 4:** Implementasikan `excel_service.py` (openpyxl) dan `pdf_service.py` (reportlab) pada endpoint `/api/v1/reports/export`.
- **Fase 5:** Bangun antarmuka React (Halaman Login Google, Dashboard KPI + Chart, Tabel Lamaran + Filter + Modal Form + Tombol Download Laporan).
- **Fase 6:** Tulis automated tests, jalankan verifikasi build & test, lalu rapikan dokumentasi `README.md`.
