# P4 — Final Release Checklist

Daftar ini memisahkan pemeriksaan yang sudah dilakukan dari langkah yang masih perlu dilakukan di mesin presentasi atau akun Streamlit Community Cloud. Status tidak menyatakan pengujian manual selesai bila belum ada bukti.

## 1. Persiapan environment

- **PASS** — Root repository memuat `app.py`, `requirements.txt`, data hasil proses, model tersimpan, dan `.gitignore`.
- **PASS** — `app.py` membangun path data dari `Path(__file__).resolve().parent`; tidak ada path absolut komputer pengembang di aplikasi atau skrip pipeline.
- **PASS** — Dataset runtime (`customer_segments.csv`, `rfm_data.csv`, `cluster_evaluation.csv`, `cleaned_retail.csv`) dan `models/kmeans_model.pkl` serta `models/scaler.pkl` tersedia dan terlacak Git.
- **PASS** — Virtual environment yang diperiksa memakai Python 3.14.10 dan Streamlit 1.67.0; `pip check` pada proses pemeriksaan dengan bypass WMI sementara tidak menemukan dependensi rusak.
- **NOT TESTED** — Instalasi baru dari environment kosong. Mesin ini tidak memiliki Python 3.11, yaitu versi yang ditetapkan konfigurasi dev container. Belum membuat environment baru atau menginstal ulang paket.
- **NOT TESTED** — Pastikan Python 3.11 tersedia di mesin presentasi atau gunakan dev container proyek.

## 2. Instalasi dependensi

- **PASS** — `requirements.txt` root berisi dependensi dashboard (`streamlit`, `pandas`, `plotly`, `requests`, dan paket pengolahan data); tidak mengunci versi baru.
- **PASS** — `backend/requirements.txt` terpisah untuk Django lokal; backend tidak dibutuhkan oleh mode direct.
- **PASS** — Dependency check pada environment yang tersedia: `No broken requirements found` (dijalankan setelah bypass WMI khusus proses pemeriksaan).
- **NOT TESTED** — Instalasi bersih dengan `python -m pip install -r requirements.txt` di mesin presentasi.

## 3. Menjalankan aplikasi dari terminal baru

- **FAILED** — Import/CLI Streamlit tanpa workaround pada Windows host ini tertahan di `platform.system()` saat Python menjalankan query WMI. Stack trace menunjuk ke Python standard library `platform.py` dan `streamlit/env_util.py`, bukan ke import aplikasi.
- **PASS** — Dengan `platform._wmi = None` hanya di proses uji, Streamlit terimpor, CLI berjalan, dan server lokal memberi HTTP 200 pada health endpoint serta halaman utama.
- **PASS** — `APP_MODE` default `direct`; semua halaman lulus AppTest tanpa koneksi ke Django localhost.
- **NOT TESTED** — Menjalankan perintah biasa pada terminal bersih di mesin presentasi yang sebenarnya:

  ```powershell
  py -3.11 -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  $env:APP_MODE = "direct"
  streamlit run app.py
  ```

- **NOT TESTED** — Jika perintah di atas macet pada Windows, catat pesan/stack trace dan pastikan WMI Windows berfungsi; jangan mengubah dependensi sebagai percobaan tanpa diagnosis.

## 4. Pengujian halaman dan hasil

- **PASS** — Dashboard: 4.338 pelanggan, total Monetary sekitar £8.89M, 3 cluster, rata-rata Frequency 4,27.
- **PASS** — Customer Segmentation: tiga cluster dengan jumlah 1.320 / 981 / 2.037 dan profil Monetary.
- **PASS** — RFM Analysis: ringkasan statistik dan tiga visualisasi tampil.
- **PASS** — Clustering Evaluation: K=2–8 dan tiga visualisasi tampil.
- **PASS** — Dataset: 392.692 baris transaksi dan 4.338 pelanggan agregat.
- **PASS** — Footer `App by Afid © 2026` tampil pada semua halaman dalam AppTest.
- **PASS** — Machine Learning: Silhouette K=3 0,415697; Davies-Bouldin K=3 0,824996; kontribusi Monetary 81,57% / 4,38% / 14,04%.
- **PASS** — RFM table Arrow serialization issue yang ditemukan saat uji telah diperbaiki; pengujian ulang semua halaman lulus.

## 5. Responsivitas HP

- **NOT TESTED** — Pemeriksaan manual melalui browser perangkat HP belum dilakukan.
- **NOT TESTED** — Buka halaman Dashboard, Customer Segmentation, RFM Analysis, Clustering Evaluation, dan Dataset pada layar sempit. Pastikan kartu bertumpuk, tabel dapat digeser/dibaca, chart tidak terpotong, dan sidebar/navigation dapat digunakan.

## 6. Deployment Streamlit Community Cloud

- **PASS** — Entry point `app.py` dan `requirements.txt` berada di root; file CSV yang dibutuhkan mode direct terlacak Git.
- **PASS** — Jika `APP_MODE` tidak ditetapkan, kode menggunakan `direct`; tidak ada ketergantungan pada Django localhost untuk deployment.
- **PASS** — Tidak ada `.streamlit/config.toml`; konfigurasi tampilan tambahan tidak diperlukan untuk menjalankan aplikasi saat ini.
- **PASS** — URL README cocok dengan URL yang dikonfirmasi pemilik proyek: https://smart-customer-segmentation-appzpvusko2vz82nlfikbki.streamlit.app/
- **NOT TESTED** — Akses aplikasi dari sesi validasi ini: root dan health endpoint Cloud mengembalikan HTTP 303 ke autentikasi. Ini tidak membuktikan halaman dashboard berhasil dimuat atau dapat diakses publik.
- **NOT TESTED** — Pengaturan aktual pada dashboard Community Cloud, termasuk branch/file utama, nilai `APP_MODE`, versi Python, dan commit yang sedang dideploy. Perubahan lokal belum dipush.
- **NOT TESTED** — Buka URL di atas menggunakan browser/perangkat yang akan dipakai saat presentasi, lalu pastikan dashboard terbuka dan data tampil.

## 7. Pemeriksaan GitHub dan repository

- **PASS** — `git diff --check` bersih.
- **PASS** — `.venv`, `__pycache__`, `*.pyc`, `.env`, dan `backend/db.sqlite3` diabaikan Git; tidak terdeteksi pola assignment kredensial pada file sumber terlacak.
- **PASS** — Data sumber, CSV hasil proses, dan file model tetap ada; tidak ada dataset/model yang dihapus atau diubah pada P4.
- **NOT TESTED** — Perubahan lokal muncul di `git status` dan belum ada di GitHub/Cloud. Tinjau semua perubahan sebelum melakukan commit/push sendiri.

## 8. Checklist sebelum presentasi UAS

- **NOT TESTED** — Jalankan aplikasi dari terminal baru dengan mode `direct` dan pastikan server siap sebelum presentasi.
- **NOT TESTED** — Buka URL Cloud dari browser presentasi; pastikan autentikasi tidak menghalangi akses.
- **NOT TESTED** — Coba semua halaman dan footer sekali lagi setelah versi yang akan dipresentasikan ditentukan.
- **NOT TESTED** — Uji tampilan pada HP/proyektor, ukuran teks, navigasi, serta kemampuan membaca tabel dan grafik.
- **NOT TESTED** — Pastikan koneksi internet, charger, browser, dan salinan dataset/artifact tersedia sebagai rencana cadangan.

Tidak ada commit, push, atau deployment yang dilakukan dalam validasi ini.
