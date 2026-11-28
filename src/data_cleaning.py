from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "cleaned_retail.csv"


def clean_online_retail():
    print("Membaca dataset...")
    df = pd.read_excel(RAW_PATH, engine="openpyxl")

    initial_rows = len(df)

    print("Jumlah data awal:", initial_rows)

    # Menghapus CustomerID kosong
    df = df.dropna(subset=["CustomerID"])

    # Menghapus data duplikat
    df = df.drop_duplicates()

    # Mengubah tipe data CustomerID
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)

    # Menghapus invoice pembatalan
    df = df[
        ~df["InvoiceNo"].astype(str).str.startswith("C")
    ]

    # Mengambil transaksi dengan Quantity positif
    df = df[df["Quantity"] > 0]

    # Mengambil transaksi dengan UnitPrice positif
    df = df[df["UnitPrice"] > 0]

    # Membuat total harga transaksi
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    # Menyimpan hasil
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(OUTPUT_PATH, index=False)

    print("\n=== HASIL DATA CLEANING ===")
    print("Data awal:", initial_rows)
    print("Data setelah cleaning:", len(df))
    print("Pelanggan unik:", df["CustomerID"].nunique())
    print("Total penjualan:", round(df["TotalPrice"].sum(), 2))
    print("File tersimpan:", OUTPUT_PATH)


if __name__ == "__main__":
    clean_online_retail()
