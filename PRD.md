# Product Requirements Document (PRD): KarirTrack — Job Application Tracker & Analytics

## 1. Ringkasan Produk
**KarirTrack** adalah aplikasi web *full-stack* untuk mencatat, melacak progres, menganalisis statistik, dan mengekspor laporan riwayat lamaran kerja (*job applications*). Aplikasi ini mendukung autentikasi satu klik menggunakan **Google Sign-In**, manajemen lamaran berbasis tabel & Kanban, serta fitur ekspor laporan ke format **Excel (.xlsx)** dan **PDF (.pdf)**.

## 2. Target Pengguna & Alur Utama (User Flow)
1. **Autentikasi:** Pengguna masuk ke halaman *Landing/Login* dan mengklik tombol **"Sign in with Google"**. Sistem memverifikasi token Google OAuth dan menerbitkan sesi JWT.
2. **Dashboard & Analitik:** Pengguna melihat ringkasan KPI (Total Lamaran, Sedang Diproses, Interview Rate %, Offering) serta grafik distribusi status dan sumber lowongan.
3. **Manajemen Lamaran (CRUD):** Pengguna menambah data lowongan baru, mengedit detail, memindahkan status lamaran (baik via *dropdown* di tabel maupun *drag-and-drop* di Kanban), atau menghapus data.
4. **Filter & Pencarian:** Pengguna memfilter lamaran berdasarkan kata kunci (perusahaan/posisi), status, model kerja (WFO/Hybrid/Remote), dan rentang tanggal melamar.
5. **Download Laporan:** Pengguna mengklik tombol **"Export Excel"** atau **"Export PDF"**. Sistem mengunduh file laporan yang isinya menyesuaikan dengan filter yang sedang aktif.

## 3. Tech Stack & Arsitektur
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS (Default Dark Mode UI), Lucide React (Icons), Recharts (Charts), `@react-oauth/google` (Google Sign-In).
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (Async) / Psycopg3, Pydantic v2, PyJWT, `google-auth` (verifikasi token ID Google).
- **Database:** PostgreSQL 16.
- **Report Generation (Backend):** `openpyxl` / `pandas` untuk `.xlsx` dan `reportlab` untuk `.pdf`.
- **Testing & CI:** Pytest (Backend), Vitest (Frontend), GitHub Actions CI.

## 4. Spesifikasi Fitur Fungsional (MVP)

### F1: Autentikasi Google Sign-In
- Endpoint backend menerima `credential` (Google ID Token) dari frontend.
- Backend memverifikasi token ke server Google menggunakan `google.oauth2.id_token.verify_oauth2_token`.
- Jika `google_id` belum ada di tabel `users`, buat record baru; jika sudah ada, perbarui `last_login`.
- Kembalikan `access_token` (JWT) berdurasi 24 jam beserta profil dasar user (`name`, `email`, `avatar_url`).

### F2: CRUD Manajemen Lamaran Kerja
- **Field Wajib:** `company_name`, `position_title`, `status`, `applied_date`.
- **Field Opsional:** `job_portal` (LinkedIn, Glints, JobStreet, Kalibrr, Website Perusahaan, Lainnya), `work_model` (WFO, Hybrid, Remote), `salary_range`, `job_url`, `notes`.
- **Daftar Status Valid:** `Applied`, `Screening`, `Technical Test`, `HR Interview`, `User Interview`, `Offering`, `Rejected`, `Ghosted`.
- **Aturan Isolasi Data:** Setiap query `SELECT`, `UPDATE`, dan `DELETE` pada `job_applications` WAJIB memfilter berdasarkan `user_id` dari JWT user yang sedang login.

### F3: Dashboard Analitik
- **KPI Cards:**
  1. Total Lamaran (`COUNT(*)`)
  2. Active Pipeline (Status selain `Rejected`, `Ghosted`, `Offering`)
  3. Interview Rate (`(Jumlah pernah masuk tahap Interview / Total Lamaran) * 100%`)
  4. Total Offering
- **Visualisasi:**
  1. Bar/Funnel Chart: Jumlah lamaran per tahap status.
  2. Pie/Donut Chart: Proporsi sumber portal lowongan (`job_portal`).
- **Smart Reminder:** Badge peringatan kuning pada baris lamaran yang berstatus `Applied` atau `Screening` dan `updated_at` sudah lebih dari 14 hari.

### F4: Fitur Download Laporan (Excel & PDF)
- Endpoint menerima parameter filter yang sama dengan endpoint list: `search`, `status`, `work_model`, `start_date`, `end_date`.
- **Format Excel (`.xlsx`):**
  - Sheet 1 (`Data Lamaran`): Tabel rapi dengan header tebal, auto-width kolom, format tanggal `YYYY-MM-DD`, dan warna status.
  - Sheet 2 (`Ringkasan Statistik`): Rekap total lamaran per status dan per portal lowongan.
- **Format PDF (`.pdf`):**
  - Header dokumen: Judul "Laporan Riwayat Lamaran Kerja", Nama Pengguna, Tanggal Cetak, dan Periode Filter.
  - Blok Ringkasan Angka (Total, Interview, Offering, Rejected).
  - Tabel data lamaran dengan layout *landscape* agar semua kolom terbaca jelas tanpa terpotong.
- **Nama File Otomatis:** `Laporan_Lamaran_<NamaUser>_<YYYYMMDD>.xlsx` atau `.pdf`.

## 5. Kontrak API (REST Endpoints)

| Method | Endpoint | Deskripsi | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/google` | Verifikasi Google ID Token & return JWT | Public |
| `GET` | `/api/v1/auth/me` | Ambil profil user yang sedang login | Bearer JWT |
| `GET` | `/api/v1/applications` | List lamaran + filter (`search`, `status`, `work_model`, `start_date`, `end_date`) | Bearer JWT |
| `POST` | `/api/v1/applications` | Tambah lamaran kerja baru | Bearer JWT |
| `PATCH` | `/api/v1/applications/{id}` | Update data atau status lamaran | Bearer JWT |
| `DELETE` | `/api/v1/applications/{id}` | Hapus lamaran kerja | Bearer JWT |
| `GET` | `/api/v1/analytics/summary` | Data KPI cards & chart dashboard | Bearer JWT |
| `GET` | `/api/v1/reports/export` | Download file laporan (`?format=xlsx` atau `?format=pdf` + query filter) | Bearer JWT |

## 6. Catatan Implementasi v1.0

Bagian ini mencatat keputusan teknis final yang menyempurnakan PRD di atas.

- **Sesi & token:** Access token JWT berumur 15 menit dan disimpan hanya di memori frontend. Refresh token berumur 7 hari disimpan di cookie `httpOnly` (`path=/api/v1/auth`) dan dirotasi setiap kali `POST /api/v1/auth/refresh` dipanggil. Logout menaikkan `users.token_version` sehingga seluruh token lama langsung tidak valid. Endpoint `POST /api/v1/auth/refresh` dan `POST /api/v1/auth/logout` ditambahkan.
- **Interview Rate:** Dihitung dari `application_status_history` (jumlah lamaran unik yang pernah mencapai `HR Interview`, `User Interview`, atau `Offering`) dibagi total lamaran, bukan dari status saat ini.
- **Follow-up:** Lamaran berstatus `Applied` atau `Screening` yang `updated_at`-nya lebih lama dari 14 hari ditandai `needs_follow_up` dan muncul di `/analytics/summary`.
- **Kanban drag-and-drop:** Ditunda ke Phase 2. MVP memakai tabel desktop + kartu mobile dengan perubahan status via form edit.
- **Isolasi tenant:** Akses ke resource milik user lain mengembalikan `404 Not Found`.
- **Database:** PostgreSQL dengan `gen_random_uuid()`, index komposit `(user_id, ...)`, check constraint untuk `status`, `work_model`, dan `job_portal`, serta trigger `updated_at`. Migrasi dikelola Alembic (bukan file SQL manual).
- **Portal lowongan:** Enum tetap `LinkedIn`, `Glints`, `JobStreet`, `Kalibrr`, `Website Perusahaan`, `Lainnya`.
- **Export:** Dibatasi `MAX_EXPORT_ROWS` (default 2000) dan mengembalikan `413` bila filter menghasilkan lebih banyak baris. Header `Content-Disposition` diekspos melalui CORS agar nama file terbaca frontend.
- **Deployment:** Satu project Vercel dengan Vercel Services (`frontend` Vite + `backend` FastAPI) dan rewrite `/api/*` ke backend, sehingga cookie refresh tetap same-origin. Database produksi memakai Neon free tier.
