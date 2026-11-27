
from pathlib import Path
import pandas as pd

# Lokasi dataset
DATA_PATH = Path("data/raw/Online Retail.xlsx")

print("=" * 55)
print("VALIDASI DATASET ONLINE RETAIL")
print("=" * 55)

# 1. Memeriksa keberadaan file
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset tidak ditemukan: {DATA_PATH}"
    )

print("\n[1] File ditemukan")
print("Nama:", DATA_PATH.name)
print("Ukuran:", round(DATA_PATH.stat().st_size / (1024**2), 2), "MB")

# 2. Membaca dataset
df = pd.read_excel(DATA_PATH, engine="openpyxl")

print("\n[2] Dataset berhasil dibaca")
print("Jumlah baris:", len(df))
print("Jumlah kolom:", len(df.columns))

# 3. Memeriksa kolom
expected_columns = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country"
]

print("\n[3] Pemeriksaan kolom")

missing_columns = [
    col for col in expected_columns
    if col not in df.columns
]

if missing_columns:
    print("Kolom tidak ditemukan:", missing_columns)
else:
    print("Semua 8 kolom sesuai.")

# 4. Informasi dataset
print("\n[4] Informasi tipe data")
print(df.info())

# 5. Missing values
print("\n[5] Missing Values")
print(df.isnull().sum())

# 6. Duplikasi
print("\n[6] Data duplikat")
print("Jumlah:", df.duplicated().sum())

# 7. Pemeriksaan nilai transaksi
print("\n[7] Pemeriksaan transaksi")

print(
    "Quantity negatif:",
    (df["Quantity"] < 0).sum()
)

print(
    "UnitPrice nol atau negatif:",
    (df["UnitPrice"] <= 0).sum()
)

print(
    "Invoice pembatalan:",
    df["InvoiceNo"].astype(str).str.startswith("C").sum()
)

# 8. Jumlah pelanggan
print("\n[8] Jumlah pelanggan")
print("Customer unik:", df["CustomerID"].nunique())
print("Customer kosong:", df["CustomerID"].isnull().sum())

# 9. Rentang tanggal
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce"
)

print("\n[9] Rentang tanggal")
print("Tanggal awal:", df["InvoiceDate"].min())
print("Tanggal akhir:", df["InvoiceDate"].max())

# 10. Negara
print("\n[10] Negara")
print("Jumlah negara:", df["Country"].nunique())

# 11. Kesimpulan
print("\n" + "=" * 55)
print("VALIDASI SELESAI")
print("=" * 55)
print("Jumlah baris sesuai referensi:",
      len(df) == 541909)
print("Jumlah kolom sesuai referensi:",
      len(df.columns) == 8)
