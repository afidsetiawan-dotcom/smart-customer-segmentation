
from pathlib import Path

import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# Lokasi dataset hasil segmentasi
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed" / "customer_segments.csv"


@api_view(["GET"])
def customer_segments(request):
    """
    Mengambil data hasil segmentasi pelanggan.
    """

    if not DATA_PATH.exists():
        return Response(
            {
                "success": False,
                "message": "File customer_segments.csv tidak ditemukan."
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        df = pd.read_csv(DATA_PATH)

        # Mengubah NaN menjadi None agar bisa dikirim sebagai JSON
        df = df.astype(object).where(pd.notna(df), None)

        # Filter berdasarkan CustomerID jika tersedia
        customer_id = request.query_params.get("customer_id")

        if customer_id and "CustomerID" in df.columns:
            df = df[
                df["CustomerID"].astype(str) == customer_id
            ]

        # Filter berdasarkan cluster jika tersedia
        cluster = request.query_params.get("cluster")

        if cluster and "Cluster" in df.columns:
            df = df[
                df["Cluster"].astype(str) == cluster
            ]

        return Response({
            "success": True,
            "total": len(df),
            "data": df.to_dict(orient="records")
        })

    except Exception as e:
        return Response(
            {
                "success": False,
                "message": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
