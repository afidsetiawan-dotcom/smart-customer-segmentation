# Panduan Presentasi UAS — Smart Customer Segmentation

**Penyusun:** Afid Setiawan

## 1. Gambaran umum sistem

Smart Customer Segmentation adalah dashboard analitik pelanggan dari data Online Retail. Sistem merangkum transaksi menjadi RFM per pelanggan, menjalankan clustering K-Means pada tahap pemrosesan, lalu menyajikan data hasil segmentasi melalui Streamlit.

Demo aplikasi memiliki lima halaman:

1. **Dashboard** — KPI dan ringkasan distribusi pelanggan serta Monetary.
2. **Customer Segmentation** — ukuran, profil RFM, kontribusi Monetary, dan strategi per cluster.
3. **RFM Analysis** — statistik dan distribusi Recency, Frequency, dan Monetary.
4. **Clustering Evaluation** — perbandingan metrik untuk K=2 sampai K=8.
5. **Dataset** — sumber data, preview transaksi bersih, dan preview agregat pelanggan.

Mode default `APP_MODE=direct` membaca CSV hasil proses dari disk. Mode `django` tersedia untuk demonstrasi API lokal, tetapi tidak dibutuhkan saat demo Streamlit Community Cloud.

## 2. Alur preprocessing data

1. Membaca `data/raw/Online Retail.xlsx` dari UCI.
2. Menghapus baris tanpa CustomerID dan transaksi duplikat.
3. Menghapus invoice pembatalan yang nomor invoice-nya berawalan `C`.
4. Mempertahankan transaksi dengan Quantity dan UnitPrice positif.
5. Menghitung `TotalPrice = Quantity × UnitPrice`; hasilnya disimpan ke `data/processed/cleaned_retail.csv`.
6. Mengagregasi transaksi per CustomerID menjadi RFM dan menyimpan `rfm_data.csv`.
7. Mentransformasi fitur, menjalankan evaluasi K=2–8, lalu menyimpan label cluster final ke `customer_segments.csv`.

Data bersih yang tersedia di proyek berisi 392.692 baris item transaksi. Data hasil agregasi berisi 4.338 pelanggan. Jadi, satu baris pada tabel transaksi tidak sama dengan satu baris pada tabel pelanggan.

## 3. Perhitungan RFM

Perhitungan dilakukan untuk setiap CustomerID:

- **Recency**: hari sejak transaksi terakhir pelanggan. Tanggal acuan adalah satu hari setelah tanggal transaksi maksimum seluruh data, sehingga pelanggan dengan nilai lebih kecil lebih baru bertransaksi.
- **Frequency**: jumlah InvoiceNo unik milik pelanggan, bukan jumlah item/baris.
- **Monetary**: penjumlahan TotalPrice milik pelanggan, dalam pound sterling (£).

Ketiga metrik merangkum kebaruan, frekuensi, dan nilai pembelian. RFM tidak dengan sendirinya menjelaskan alasan pelanggan berperilaku demikian.

## 4. Cara kerja K-Means

K-Means mengelompokkan titik yang berdekatan berdasarkan jarak pada fitur yang dipakai. Dalam proyek ini:

1. Frequency dan Monetary ditransformasi dengan `log1p` untuk mengurangi pengaruh sebaran yang sangat menceng.
2. Recency, Frequency, dan Monetary distandarkan dengan `StandardScaler` agar perbedaan skala tidak mendominasi jarak.
3. K-Means mencari centroid dan menempatkan setiap pelanggan ke cluster terdekat.
4. Model final menggunakan `K=3`, `random_state=42`, dan `n_init=10`.

Angka cluster (0, 1, 2) hanyalah label; tidak menunjukkan urutan kualitas. Nama segmen diberikan setelah membandingkan profil RFM aktualnya.

## 5. Alasan memilih jumlah cluster

Hasil evaluasi aktual pada `data/processed/cluster_evaluation.csv`:

| K | Inertia | Silhouette | Davies-Bouldin |
|---:|---:|---:|---:|
| 2 | 6.874,93 | 0,4062 | 0,9154 |
| 3 | 4.299,07 | **0,4157** | **0,8250** |
| 4 | 3.243,03 | 0,3795 | 0,8595 |
| 5 | 2.760,79 | 0,3435 | 0,9415 |
| 6 | 2.396,85 | 0,3299 | 0,9816 |
| 7 | 2.166,96 | 0,3008 | 1,0195 |
| 8 | 1.961,09 | 0,2999 | 1,0012 |

K=3 dipilih karena memberikan Silhouette Score tertinggi dan Davies-Bouldin Index terendah pada rentang yang diuji. Inertia terus turun saat K bertambah, jadi penurunan inertia saja tidak cukup untuk memilih jumlah cluster. K=3 juga menjaga hasil tetap ringkas dan bisa dijelaskan untuk kebutuhan presentasi.

## 6. Interpretasi cluster

Angka berikut diringkas langsung dari `customer_segments.csv`. Recency yang lebih rendah berarti transaksi lebih baru; Frequency dan Monetary yang lebih tinggi menunjukkan pembelian lebih sering dan nilai belanja rata-rata lebih besar.

| Cluster dan nama | Jumlah pelanggan | Rata-rata Recency | Rata-rata Frequency | Rata-rata Monetary | Total Monetary / kontribusi |
|---|---:|---:|---:|---:|---:|
| 0 — High Value Customers | 1.320 | 30,10 hari | 9,84 invoice | £5.492,04 | £7.249.492,37 / 81,57% |
| 1 — At Risk Customers | 981 | 255,11 hari | 1,39 invoice | £397,17 | £389.626,80 / 4,38% |
| 2 — Regular Customers | 2.037 | 54,70 hari | 2,05 invoice | £612,71 | £1.248.089,72 / 14,04% |

### Cluster 0 — High Value Customers

Rata-rata Recency paling rendah dan Frequency serta Monetary paling tinggi pada data ini. Kelompok ini berjumlah 1.320 pelanggan dan menyumbang 81,57% dari total Monetary. Strategi yang disarankan: menjaga loyalitas dan memberi rekomendasi relevan; hindari diskon massal yang tidak diperlukan.

### Cluster 1 — At Risk Customers

Rata-rata Recency paling tinggi, sedangkan Frequency dan Monetary paling rendah. Kelompok ini berjumlah 981 pelanggan dan menyumbang 4,38% dari total Monetary. Strategi yang disarankan: kampanye win-back terarah, pengingat yang relevan, dan uji insentif pembelian kembali.

### Cluster 2 — Regular Customers

Rata-rata Recency berada di antara cluster lain dan profil Frequency serta Monetary berada di tingkat menengah. Kelompok ini berjumlah 2.037 pelanggan dan menyumbang 14,04% dari total Monetary. Strategi yang disarankan: mendorong pembelian berulang atau cross-sell yang relevan, kemudian mengukur respons.

Rekomendasi tersebut adalah hipotesis pemasaran berdasarkan profil observasi, bukan bukti bahwa intervensi tertentu pasti meningkatkan penjualan.

## 7. Evaluasi model

- **Inertia**: jumlah kuadrat jarak titik ke centroid cluster; turun ketika cluster ditambah dan perlu dibaca bersama metrik lain.
- **Silhouette Score**: menilai kekompakan dan keterpisahan cluster; nilai lebih tinggi lebih baik. K=3 memperoleh 0,4157.
- **Davies-Bouldin Index**: menilai kemiripan antarcluster; nilai lebih rendah lebih baik. K=3 memperoleh 0,8250.

Ketiga metrik menyajikan aspek berbeda; hasil evaluasi tidak menjamin cluster sempurna atau bermanfaat tanpa validasi bisnis.

## 8. Menjalankan dan mengakses aplikasi

### Menjalankan lokal

Dari terminal baru yang dibuka pada root repository, gunakan Python 3.11 seperti konfigurasi dev container:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:APP_MODE = "direct"
streamlit run app.py
```

Jika PowerShell tidak mengizinkan aktivasi environment, setelah instalasi gunakan `.\.venv\Scripts\python.exe -m streamlit run app.py`. Jalankan dari root proyek agar aplikasi menemukan `data/processed/`; aplikasi menggunakan mode `direct` secara default dan tidak memerlukan Django. Tidak ada pelatihan ulang saat startup.

### Mengakses versi online

Buka [Smart Customer Segmentation di Streamlit Community Cloud](https://smart-customer-segmentation-appzpvusko2vz82nlfikbki.streamlit.app/). URL ini dikonfirmasi oleh pemilik proyek, tetapi akses langsung belum dapat diverifikasi dari sesi ini karena permintaan dialihkan ke autentikasi Streamlit Cloud. Pastikan akses berhasil dari browser/perangkat presentasi sebelum hari UAS.

## 9. Alur demonstrasi aplikasi

1. Buka aplikasi dengan `APP_MODE=direct` agar demo tidak bergantung pada server Django.
2. **Dashboard**: jelaskan jumlah pelanggan, total Monetary, banyak cluster, rata-rata Frequency, dan perbedaan distribusi jumlah pelanggan dengan kontribusi Monetary.
3. **Customer Segmentation**: tunjukkan distribusi, nilai RFM, jumlah pelanggan, kontribusi Monetary, rekomendasi, lalu pilih cluster untuk melihat daftar pelanggan.
4. **RFM Analysis**: jelaskan definisi ketiga metrik dan bentuk distribusinya; catat bahwa Frequency dan Monetary dapat memakai skala log pada histogram.
5. **Clustering Evaluation**: bandingkan K=2–8 dan tunjukkan Silhouette tertinggi serta Davies-Bouldin terendah pada K=3.
6. **Dataset**: bandingkan beberapa baris transaksi tingkat item dengan agregat per CustomerID, lalu jelaskan sumber UCI.

Setelah aplikasi lokal atau tautan online terbuka, demonstrasikan halaman sesuai urutan di atas. Jika demo lokal gagal dijalankan di Windows, gunakan versi online setelah akses browser dikonfirmasi; jangan mengandalkan server Django localhost untuk mode `direct`.

## 10. Kelebihan dan keterbatasan

**Kelebihan**

- Menyajikan transaksi dan agregat pelanggan secara terpisah.
- Menggabungkan profil perilaku, visualisasi, metrik evaluasi, dan contoh strategi dalam satu aplikasi.
- Hasil dashboard dapat direproduksi dari CSV dan parameter model tersimpan di proyek.
- Mode direct membuat aplikasi tidak bergantung pada API backend saat deploy.

**Keterbatasan**

- Hasil bersifat snapshot dari periode dataset sumber; bukan pemantauan transaksi langsung.
- Nilai Monetary menggunakan pound sterling dan periode historis dataset, bukan nilai uang terkini.
- K-Means sensitif pada fitur, skala, outlier, dan pilihan K; transformasi log serta standardisasi mengurangi sebagian masalah, tetapi tidak menghapusnya.
- Silhouette dan Davies-Bouldin mengukur struktur matematis, bukan dampak bisnis.
- Rata-rata cluster dapat dipengaruhi pelanggan dengan nilai belanja sangat besar.
- Strategi pemasaran perlu diuji dengan eksperimen dan data terbaru sebelum diterapkan.
