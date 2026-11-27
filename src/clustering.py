
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "rfm_data.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "customer_segments.csv"
MODEL_DIR = BASE_DIR / "models"


def run_clustering():
    print("Membaca data RFM...")

    df = pd.read_csv(INPUT_PATH)

    features = ["Recency", "Frequency", "Monetary"]

    # Transformasi log untuk mengurangi kemencengan distribusi
    X = df[features].copy()
    X["Frequency"] = np.log1p(X["Frequency"])
    X["Monetary"] = np.log1p(X["Monetary"])

    # Standardisasi fitur
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Pengujian jumlah cluster K=2 sampai K=8
    results = []

    for k in range(2, 9):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(X_scaled)

        results.append({
            "K": k,
            "Inertia": model.inertia_,
            "Silhouette": silhouette_score(X_scaled, labels),
            "Davies_Bouldin": davies_bouldin_score(
                X_scaled, labels
            )
        })

        print(f"K={k} selesai")

    results_df = pd.DataFrame(results)

    print("\n=== HASIL EVALUASI CLUSTER ===")
    print(results_df.to_string(index=False))

    # Grafik Elbow
    plt.figure(figsize=(8, 5))
    plt.plot(
        results_df["K"],
        results_df["Inertia"],
        marker="o"
    )
    plt.title("Elbow Method")
    plt.xlabel("Jumlah Cluster (K)")
    plt.ylabel("Inertia")
    plt.xticks(range(2, 9))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        BASE_DIR / "data" / "processed" / "elbow_method.png"
    )
    plt.show()

    # Grafik Silhouette
    plt.figure(figsize=(8, 5))
    plt.plot(
        results_df["K"],
        results_df["Silhouette"],
        marker="o"
    )
    plt.title("Silhouette Score")
    plt.xlabel("Jumlah Cluster (K)")
    plt.ylabel("Silhouette Score")
    plt.xticks(range(2, 9))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        BASE_DIR / "data" / "processed" / "silhouette_score.png"
    )
    plt.show()

    # Simpan hasil evaluasi
    results_df.to_csv(
        BASE_DIR / "data" / "processed" / "cluster_evaluation.csv",
        index=False
    )

    print("\nGrafik dan hasil evaluasi berhasil disimpan.")


if __name__ == "__main__":
    run_clustering()
