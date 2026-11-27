
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "cleaned_retail.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_data.csv"


def create_rfm():
    print("Membaca data transaksi bersih...")

    df = pd.read_csv(INPUT_PATH)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Tanggal acuan satu hari setelah transaksi terakhir
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    # Menghitung RFM per pelanggan
    rfm = df.groupby("CustomerID").agg(
        Recency=(
            "InvoiceDate",
            lambda x: (reference_date - x.max()).days
        ),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("TotalPrice", "sum")
    ).reset_index()

    # Membulatkan Monetary
    rfm["Monetary"] = rfm["Monetary"].round(2)

    # Menyimpan hasil
    rfm.to_csv(OUTPUT_PATH, index=False)

    print("\n=== HASIL RFM ANALYSIS ===")
    print("Jumlah pelanggan:", len(rfm))

    print("\nStatistik RFM:")
    print(rfm[["Recency", "Frequency", "Monetary"]].describe())

    print("\nContoh data:")
    print(rfm.head(10).to_string(index=False))

    print("\nFile tersimpan:", OUTPUT_PATH)


if __name__ == "__main__":
    create_rfm()
