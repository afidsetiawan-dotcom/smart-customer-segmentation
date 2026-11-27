
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_data.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "customer_segments.csv"

MODEL_DIR = BASE_DIR / "models"


def train_final_model():
    print("Membaca data RFM...")

    df = pd.read_csv(INPUT_PATH)

    features = ["Recency", "Frequency", "Monetary"]

    # Transformasi log
    X = df[features].copy()
    X["Frequency"] = np.log1p(X["Frequency"])
    X["Monetary"] = np.log1p(X["Monetary"])

    # Standardisasi
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Model final K-Means
    model = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )

    df["Cluster"] = model.fit_predict(X_scaled)

    # Membuat folder model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Menyimpan model dan scaler
    joblib.dump(model, MODEL_DIR / "kmeans_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")

    # Menyimpan hasil segmentasi
    df.to_csv(OUTPUT_PATH, index=False)

    # Profil cluster
    profile = df.groupby("Cluster").agg(
        Jumlah_Pelanggan=("CustomerID", "count"),
        Rata_Rata_Recency=("Recency", "mean"),
        Rata_Rata_Frequency=("Frequency", "mean"),
        Rata_Rata_Monetary=("Monetary", "mean"),
        Total_Monetary=("Monetary", "sum")
    ).round(2)

    print("\n=== PROFIL CLUSTER ===")
    print(profile.to_string())

    print("\n=== HASIL TRAINING ===")
    print("Jumlah pelanggan:", len(df))
    print("Jumlah cluster:", df["Cluster"].nunique())
    print("Model tersimpan:", MODEL_DIR / "kmeans_model.pkl")
    print("Scaler tersimpan:", MODEL_DIR / "scaler.pkl")
    print("Data segmentasi:", OUTPUT_PATH)


if __name__ == "__main__":
    train_final_model()
