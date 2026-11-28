# Skenario Demo UAS — Smart Customer Segmentation

**Penyusun:** Afid Setiawan

Dokumen ini berisi alur demo dan ringkasan teknis untuk presentasi. Angka hasil menggunakan data yang tersimpan di proyek; jangan melatih ulang model atau mengubah dataset hanya untuk presentasi.

## 1. Urutan membuka aplikasi

1. Pastikan browser presentasi dapat membuka [aplikasi Streamlit Community Cloud](https://smart-customer-segmentation-appzpvusko2vz82nlfikbki.streamlit.app/). URL tersebut dikonfirmasi pemilik proyek, tetapi sesi validasi ini menerima pengalihan autentikasi; akses aktual harus diuji dari perangkat presentasi terlebih dahulu.
2. Jika menggunakan aplikasi lokal, buka terminal pada root repository dan gunakan Python 3.11 seperti environment dev container:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   $env:APP_MODE = "direct"
   streamlit run app.py
   ```

3. Jika environment sudah tersedia, aktifkan environment tersebut dan jalankan `streamlit run app.py` dari root proyek. Mode `direct` adalah default dan tidak memerlukan Django.
4. Konfirmasi judul aplikasi, navigasi lima halaman, dan footer `App by Afid © 2026` sebelum mulai menjelaskan.

**Catatan teknis:** Pada host Windows yang digunakan untuk validasi, import Streamlit normal tertahan saat Python meminta informasi sistem melalui WMI. Jangan mengandalkan host tersebut sebagai mesin demo sebelum masalah WMI diperiksa. AppTest semua halaman dan HTTP lokal pernah lulus dengan bypass WMI sementara khusus proses uji; bypass itu bukan perubahan atau instruksi untuk aplikasi rilis.

## 2. Dashboard

**Yang ditunjukkan:** KPI pelanggan, total Monetary, jumlah segmen, rata-rata Frequency, distribusi jumlah pelanggan, dan kontribusi Monetary.

**Penjelasan:** Angka berasal dari data pelanggan hasil segmentasi, bukan jumlah baris transaksi. Dataset ini berisi 4.338 pelanggan, tiga cluster, total Monetary sekitar £8,89 juta, dan rata-rata Frequency 4,27 invoice per pelanggan. Monetary dinyatakan dalam pound sterling (£).

## 3. Customer Segmentation

1. Tunjukkan distribusi tiga cluster dan tabel profil RFM.
2. Buka kartu segmen untuk menjelaskan jumlah pelanggan, rata-rata Recency/Frequency/Monetary, total Monetary, kontribusi, dan strategi.
3. Pilih cluster pada filter untuk memperlihatkan daftar pelanggan. Jika perlu, tunjukkan fitur unduh CSV tanpa mengubah file sumber.

| Cluster | Nama | Pelanggan | Rata-rata Recency | Rata-rata Frequency | Rata-rata Monetary | Kontribusi Monetary |
|---|---|---:|---:|---:|---:|---:|
| 0 | High Value Customers | 1.320 | 30,10 hari | 9,84 invoice | £5.492,04 | 81,57% |
| 1 | At Risk Customers | 981 | 255,11 hari | 1,39 invoice | £397,17 | 4,38% |
| 2 | Regular Customers | 2.037 | 54,70 hari | 2,05 invoice | £612,71 | 14,04% |

Cluster 0 lebih baru aktif dan memiliki nilai rata-rata serta kontribusi Monetary terbesar. Cluster 1 paling lama tidak bertransaksi dan memiliki rata-rata Frequency/Monetary terendah. Cluster 2 berada di antara profil keduanya. Rekomendasi pemasaran adalah hipotesis berdasarkan pola observasi, bukan bukti sebab-akibat.

## 4. RFM Analysis

Jelaskan metrik dengan bahasa sederhana:

- **Recency**: jumlah hari sejak transaksi terakhir; lebih kecil berarti lebih baru berbelanja.
- **Frequency**: jumlah invoice unik dalam periode data; lebih besar berarti lebih sering bertransaksi.
- **Monetary**: total nilai belanja per pelanggan dalam pound sterling.

Tunjukkan tabel statistik dan tiga histogram. Jika Frequency atau Monetary memakai skala log, jelaskan bahwa skala tersebut membantu membaca sebaran yang menceng; nilai data tidak diubah oleh tampilan grafik.

## 5. Clustering Evaluation

Tampilkan hasil K=2 sampai K=8, lalu jelaskan:

- Inertia mengukur kekompakan terhadap centroid dan biasanya turun saat K bertambah.
- Silhouette yang lebih tinggi menunjukkan cluster lebih kompak dan terpisah.
- Davies-Bouldin yang lebih rendah menunjukkan cluster lebih berbeda.

Pada evaluasi tersimpan, K=3 memiliki Silhouette Score **0,415697** (tertinggi) dan Davies-Bouldin Index **0,824996** (terendah). Inertia turun dari **6.874,93** pada K=2 ke **4.299,07** pada K=3 dan **3.243,03** pada K=4. K=3 dipilih berdasarkan gabungan indikator evaluasi dan kemudahan interpretasi; inertia saja tidak cukup karena nilainya turun ketika jumlah cluster ditambah.

## 6. Dataset

1. Sebutkan sumber [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail).
2. Tunjukkan preview transaksi bersih: satu baris mewakili item transaksi, bukan satu pelanggan.
3. Tunjukkan preview agregat pelanggan: satu baris per CustomerID dengan metrik RFM dan label cluster.
4. Sebutkan jumlah yang tersedia: 392.692 baris transaksi bersih dan 4.338 pelanggan agregat.

Jangan menyamakan baris transaksi dengan pelanggan unik. CSV dashboard adalah snapshot yang sudah diproses.

## 7. Contoh penjelasan hasil kepada dosen

> “Saya mengubah transaksi menjadi Recency, Frequency, dan Monetary per pelanggan. Frequency dan Monetary ditransformasi `log1p`, kemudian ketiga fitur distandarkan sebelum K-Means. Saya membandingkan K=2 sampai K=8; K=3 memperoleh Silhouette tertinggi, 0,415697, dan Davies-Bouldin terendah, 0,824996. Hasilnya menunjukkan cluster 0 berisi 1.320 pelanggan dengan kontribusi Monetary 81,57%; cluster 1 memiliki 981 pelanggan dan profil paling berisiko berdasarkan Recency yang tinggi serta Frequency dan Monetary yang rendah; cluster 2 berisi 2.037 pelanggan dengan profil menengah. Hasil ini deskriptif, bukan prediksi atau bukti dampak kampanye.”

## 8. Pertanyaan yang mungkin diajukan

### Mengapa menggunakan RFM?

RFM merangkum tiga aspek perilaku yang mudah ditafsirkan: kapan pelanggan terakhir membeli, seberapa sering membeli, dan berapa nilai belanjanya. Metrik tersebut mendukung profil pelanggan, tetapi tidak menjelaskan sebab perilaku.

### Mengapa menggunakan K-Means?

Ketiga fitur RFM numerik dan dapat dikelompokkan berdasarkan jarak setelah transformasi dan standardisasi. K-Means memberi centroid dan label cluster yang mudah diringkas. Metode ini memerlukan K yang ditentukan dan peka terhadap skala, outlier, serta bentuk cluster.

### Mengapa K=3, bukan K=2 atau K=4?

Di rentang K=2–8, K=3 memiliki Silhouette tertinggi (0,415697) dan Davies-Bouldin terendah (0,824996). Inertia memang lebih rendah pada K=4, tetapi metrik itu cenderung turun saat K bertambah dan tidak menjadi dasar tunggal pemilihan.

### Apakah cluster 0 selalu lebih baik daripada cluster 1?

Tidak. Angka cluster adalah label arbitrer, bukan peringkat. Nama segmen diberikan setelah membandingkan profil aktual RFM.

### Apa arti kontribusi Monetary 81,57% pada cluster 0?

Itu adalah bagian jumlah Monetary pelanggan cluster 0 terhadap jumlah Monetary seluruh pelanggan pada snapshot data ini. Angka tersebut bukan profit, bukan persentase pelanggan, dan tidak membuktikan strategi tertentu menyebabkan penjualan.

### Apakah sistem memprediksi pelanggan yang akan berhenti membeli?

Tidak. Sistem melakukan segmentasi deskriptif pada data historis. Label “At Risk” membantu mengidentifikasi kelompok dengan Recency tinggi dan Frequency/Monetary rendah, bukan probabilitas churn.

### Mengapa aplikasi tidak melatih ulang model saat dibuka?

Aplikasi membaca CSV hasil proses yang telah disimpan agar dashboard cepat dan hasilnya konsisten. Pelatihan dilakukan oleh skrip pipeline terpisah; perubahan data harus melalui preprocessing, evaluasi, dan pembaruan artefak secara terkontrol.

### Apa keterbatasan yang paling penting?

Data bersifat historis dan berdenominasi GBP; hasil K-Means dipengaruhi pemilihan fitur, transformasi, skala, outlier, dan K. Evaluasi matematis belum membuktikan manfaat bisnis, sehingga strategi perlu diuji dengan data terbaru dan eksperimen.

## 9. Ringkasan presentasi teknis

### Alur sistem

`Online Retail.xlsx` dari UCI → pembersihan transaksi → `cleaned_retail.csv` → agregasi RFM per CustomerID → transformasi dan standardisasi fitur → evaluasi K=2–8 → label cluster final K=3 → CSV hasil segmentasi → dashboard Streamlit mode direct.

### Metode dan alasan

- **RFM** merangkum kebaruan, frekuensi, dan nilai pembelian per pelanggan dengan interpretasi langsung.
- **K-Means** digunakan untuk mengelompokkan vektor fitur numerik berdasarkan kedekatan centroid. Frequency dan Monetary diubah dengan `log1p`; semua fitur RFM distandarkan memakai `StandardScaler`.
- Model final menggunakan `K=3`, `random_state=42`, dan `n_init=10`.
- **K=3** dipilih karena Silhouette 0,415697 tertinggi dan Davies-Bouldin 0,824996 terendah pada K=2–8; jumlah cluster juga masih mudah dijelaskan.

### Profil cluster aktual

- **Cluster 0 — High Value Customers:** 1.320 pelanggan; rata-rata Recency 30,10 hari, Frequency 9,84 invoice, Monetary £5.492,04; kontribusi Monetary 81,57%.
- **Cluster 1 — At Risk Customers:** 981 pelanggan; rata-rata Recency 255,11 hari, Frequency 1,39 invoice, Monetary £397,17; kontribusi Monetary 4,38%.
- **Cluster 2 — Regular Customers:** 2.037 pelanggan; rata-rata Recency 54,70 hari, Frequency 2,05 invoice, Monetary £612,71; kontribusi Monetary 14,04%.

### Kelebihan, keterbatasan, dan pengembangan berikutnya

**Kelebihan:** hasil dapat ditelusuri ke CSV, profil mudah dijelaskan, dan dashboard mode direct tidak membutuhkan Django.

**Keterbatasan:** snapshot historis, rentan terhadap outlier dan pilihan K/fitur, metrik cluster tidak mengukur dampak bisnis, serta rekomendasi belum diuji secara kausal.

**Pengembangan selanjutnya:** perbarui data secara berkala dengan validasi skema; evaluasi kestabilan cluster pada periode berbeda; uji strategi dengan eksperimen terkontrol; dan pantau perubahan distribusi RFM sebelum memakai segmen untuk keputusan operasional.
