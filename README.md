# Smart Customer Segmentation

**Penyusun:** Afid Setiawan

Dashboard analitik untuk memahami perilaku pelanggan pada dataset Online Retail melalui metrik Recency, Frequency, Monetary (RFM) dan segmentasi K-Means. Aplikasi menyediakan ringkasan KPI, profil cluster, analisis RFM, evaluasi jumlah cluster, serta preview data transaksi dan agregat pelanggan.

## Latar belakang dan tujuan

Pelanggan memiliki pola belanja yang berbeda. Ringkasan transaksi dan segmentasi membantu melihat kelompok pelanggan yang perlu dipertahankan, diaktifkan kembali, atau didorong untuk bertransaksi lagi. Proyek ini bertujuan:

- mengubah transaksi menjadi metrik RFM per pelanggan;
- mengelompokkan pelanggan berdasarkan kemiripan perilaku belanja;
- menyajikan profil cluster dan evaluasi model dalam dashboard yang mudah dipahami.

Hasil ini adalah alat bantu analisis, bukan prediksi atau keputusan pemasaran otomatis.

## Dataset dan sumber

Dataset sumber adalah [Online Retail dari UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail). Data transaksi mentah tersedia di `data/raw/Online Retail.xlsx`. Setelah pembersihan, `data/processed/cleaned_retail.csv` berisi 392.692 baris item transaksi. Proses agregasi menghasilkan data untuk 4.338 pelanggan.

Data transaksi dan data agregat pelanggan memiliki tingkat detail berbeda:

- **Transaksi**: satu baris per item pada invoice, termasuk tanggal, kuantitas, harga, pelanggan, dan negara.
- **Pelanggan**: satu baris per CustomerID, dengan metrik RFM dan label cluster.

## Metodologi

### Pembersihan dan agregasi RFM

Proses pada `src/data_cleaning.py` menghapus transaksi tanpa CustomerID, duplikat, invoice pembatalan (InvoiceNo berawalan `C`), kuantitas tidak positif, dan harga satuan tidak positif. Nilai transaksi dihitung sebagai `Quantity × UnitPrice`.

Untuk setiap pelanggan, `src/rfm_analysis.py` menghitung:

- **Recency**: jumlah hari dari transaksi terakhir sampai satu hari setelah tanggal transaksi terakhir di seluruh dataset.
- **Frequency**: jumlah invoice unik.
- **Monetary**: total nilai transaksi pelanggan dalam pound sterling (£).

### K-Means

`src/train_final_model.py` mengubah Frequency dan Monetary menggunakan `log1p`, kemudian menstandarkan Recency, Frequency, dan Monetary menggunakan `StandardScaler`. Model final menggunakan K-Means dengan `K=3`, `random_state=42`, dan `n_init=10`. Aplikasi membaca hasil yang sudah tersimpan; membuka dashboard tidak melatih ulang model.

## Hasil evaluasi clustering

File `data/processed/cluster_evaluation.csv` berisi evaluasi untuk K=2 sampai K=8. Untuk K=3, Silhouette Score adalah **0,4157** (tertinggi dalam perbandingan) dan Davies-Bouldin Index **0,8250** (terendah). Inertia turun dari **6.874,93** pada K=2 menjadi **4.299,07** pada K=3 dan **3.243,03** pada K=4. Pemilihan K=3 mengutamakan dua metrik kualitas pemisahan yang terbaik sambil mempertahankan jumlah cluster yang dapat ditafsirkan; inertia sendiri terus turun ketika K bertambah.

Profil data yang digunakan aplikasi:

| Cluster | Segmen | Pelanggan | Rata-rata Recency (hari) | Rata-rata Frequency | Rata-rata Monetary | Total Monetary | Kontribusi Monetary |
|---|---|---:|---:|---:|---:|---:|---:|
| 0 | High Value Customers | 1.320 | 30,10 | 9,84 | £5.492,04 | £7.249.492,37 | 81,57% |
| 1 | At Risk Customers | 981 | 255,11 | 1,39 | £397,17 | £389.626,80 | 4,38% |
| 2 | Regular Customers | 2.037 | 54,70 | 2,05 | £612,71 | £1.248.089,72 | 14,04% |

Nilai kontribusi adalah pembagian jumlah Monetary cluster dengan Monetary seluruh pelanggan. Nama dan rekomendasi segmen dibaca bersama karakteristik RFM aktual; rekomendasi bukan hasil eksperimen kausal.

## Teknologi

- Python dan pandas untuk pengolahan data.
- scikit-learn untuk StandardScaler, K-Means, dan metrik evaluasi.
- Streamlit untuk dashboard interaktif.
- Plotly untuk visualisasi.
- Django REST Framework untuk API lokal opsional.

## Struktur proyek

```text
.
├── .devcontainer/
│   └── devcontainer.json           # Environment pengembangan Python
├── .gitignore                      # File lokal dan cache yang diabaikan Git
├── app.py                         # Aplikasi Streamlit
├── README.md                       # Deskripsi proyek dan instruksi penggunaan
├── requirements.txt               # Dependensi dashboard
├── validate_dataset.py            # Pemeriksaan dataset
├── backend/
│   ├── manage.py                   # Django management
│   ├── requirements.txt            # Dependensi backend
│   ├── config/                     # Konfigurasi Django
│   └── segmentation_api/           # Endpoint data segmentasi
├── data/
│   ├── raw/                        # Dataset sumber UCI
│   └── processed/                  # CSV hasil proses dan grafik evaluasi
├── docs/
│   ├── final_release_checklist.md  # Checklist finalisasi dan langkah manual
│   ├── panduan_presentasi.md       # Panduan presentasi UAS
│   └── skenario_demo_uas.md        # Urutan demo dan tanya-jawab teknis
├── models/                         # Model K-Means dan scaler tersimpan
└── src/
    ├── data_cleaning.py
    ├── rfm_analysis.py
    ├── clustering.py
    └── train_final_model.py
```

## Instalasi dan menjalankan aplikasi

Gunakan Python 3.11 seperti konfigurasi dev container proyek. Buka terminal di direktori root repository:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:APP_MODE = "direct"
streamlit run app.py
```

Jika aktivasi virtual environment dibatasi oleh policy PowerShell, jalankan interpreter environment secara langsung:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mode `direct` adalah default: Streamlit membaca `data/processed/customer_segments.csv` tanpa backend Django. Semua path aplikasi dibangun relatif terhadap lokasi `app.py`; jalankan perintah dari root repository. Halaman lain juga menggunakan CSV di `data/processed/`. File model di `models/` dipakai oleh skrip training, bukan dimuat oleh dashboard saat runtime.

Untuk integrasi lokal dengan Django, pasang dependensi `backend/requirements.txt`, jalankan backend dari direktori `backend` dengan `python manage.py runserver`, lalu jalankan Streamlit dari direktori root dengan `APP_MODE=django`. Mode Django mengakses `http://127.0.0.1:8000/api/segments/` dan memerlukan backend yang berjalan di mesin yang sama.

## Deployment Streamlit Community Cloud

Pilih repository GitHub ini, branch `main`, dan file utama `app.py` pada Streamlit Community Cloud. Dependensi dashboard diambil dari `requirements.txt` di root; biarkan `APP_MODE` tidak disetel atau set nilainya ke `direct`.

**Aplikasi:** [Smart Customer Segmentation di Streamlit Community Cloud](https://smart-customer-segmentation-appzpvusko2vz82nlfikbki.streamlit.app/)

URL di atas dikonfirmasi oleh pemilik proyek. Akses langsung dari sesi validasi ini belum terverifikasi; endpoint Cloud mengarahkan permintaan ke halaman autentikasi.
