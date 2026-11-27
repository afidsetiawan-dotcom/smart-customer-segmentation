import os
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

import requests


# ==========================================
# KONFIGURASI APLIKASI
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data" / "processed"
APP_MODE = os.environ.get("APP_MODE", "direct").strip().lower()
REQUIRED_COLUMNS = {
    "CustomerID",
    "Recency",
    "Frequency",
    "Monetary",
    "Cluster",
}

st.set_page_config(
    page_title="Smart Customer Segmentation",
    page_icon="🐦‍🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #17243A;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #17243A;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 14px;
        color: #718096;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E5EAF2;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
    }

    div[data-testid="stMetricValue"] {
        color: #17243A;
        font-weight: 700;
    }

    h2, h3 {
        color: #17243A;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# MEMBACA DATA
# ==========================================


class EmptyAPIDataError(ValueError):
    """Menandai respons API valid yang belum berisi data pelanggan."""


def validate_data_columns(df, source):
    """Memastikan sumber data memiliki kolom yang digunakan aplikasi."""

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"{source} tidak memiliki kolom wajib: {missing}."
        )


@st.cache_data(ttl=60)
def load_data(mode):
    """Memuat data segmentasi melalui API Django atau CSV lokal."""

    if mode == "direct":
        csv_path = DATA_DIR / "customer_segments.csv"
        if not csv_path.is_file():
            raise FileNotFoundError(
                f"File data segmentasi tidak ditemukan: {csv_path}."
            )

        df = pd.read_csv(csv_path)
        validate_data_columns(df, "File CSV")
        return df

    if mode != "django":
        raise ValueError(
            "APP_MODE harus bernilai 'direct' atau 'django'."
        )

    api_url = "http://127.0.0.1:8000/api/segments/"
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()

    try:
        result = response.json()
    except ValueError as exc:
        raise ValueError(
            "Respons Django API bukan JSON yang valid."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Format respons Django API tidak valid.")

    if result.get("success") is not True:
        message = result.get("message") or "API Django gagal mengambil data."
        raise RuntimeError(message)

    if "data" not in result:
        raise ValueError("Respons Django API tidak memiliki field 'data'.")

    data = result["data"]
    if not isinstance(data, list) or any(
        not isinstance(row, dict) for row in data
    ):
        raise ValueError(
            "Field 'data' pada respons Django API harus berupa daftar objek."
        )

    if not data:
        raise EmptyAPIDataError(
            "Data pelanggan dari Django API masih kosong."
        )

    df = pd.DataFrame.from_records(data)
    validate_data_columns(df, "Respons Django API")
    return df


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.markdown("## SMART SEGMENT")
st.sidebar.caption("Customer Analytics System")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Customer Segmentation",
        "Model Evaluation",
        "Dataset"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Machine Learning Project")
st.sidebar.caption("K-Means Clustering")


@st.cache_data(ttl=60)
def load_evaluation():
    """Membaca metrik evaluasi clustering yang sudah tersimpan."""

    evaluation_path = DATA_DIR / "cluster_evaluation.csv"
    if not evaluation_path.is_file():
        raise FileNotFoundError("File evaluasi clustering tidak ditemukan.")

    evaluation = pd.read_csv(evaluation_path)
    if evaluation.empty:
        raise ValueError("File evaluasi clustering kosong.")

    required_columns = {"K", "Inertia", "Silhouette", "Davies_Bouldin"}
    missing_columns = required_columns.difference(evaluation.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"File evaluasi tidak memiliki kolom wajib: {missing}."
        )

    return evaluation


df = None
try:
    df = load_data(APP_MODE)
except requests.exceptions.Timeout:
    st.error("Permintaan ke Django API melewati batas waktu.")
    st.stop()
except requests.exceptions.HTTPError as exc:
    status_code = (
        exc.response.status_code
        if exc.response is not None
        else "tidak diketahui"
    )
    st.error(f"Django API mengembalikan HTTP {status_code}.")
    st.stop()
except requests.exceptions.ConnectionError:
    st.error(
        "Django API tidak tersedia. Pastikan backend berjalan "
        "di http://127.0.0.1:8000."
    )
    st.stop()
except requests.exceptions.RequestException as exc:
    st.error(f"Gagal menghubungi Django API: {exc}")
    st.stop()
except EmptyAPIDataError as exc:
    st.warning(str(exc))
    st.stop()
except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
    source = "Django API" if APP_MODE == "django" else "file CSV"
    st.error(f"Gagal membaca data dari {source}: {exc}")
    st.stop()

if df is None:
    source = "Django API" if APP_MODE == "django" else "file CSV"
    st.error(f"Data pelanggan tidak berhasil dimuat dari {source}.")
    st.stop()

if df.empty:
    source = "Django API" if APP_MODE == "django" else "file CSV"
    st.warning(f"Data pelanggan dari {source} masih kosong.")
    st.stop()


if menu == "Dashboard":
    st.markdown(
        '<div class="main-title">Dashboard Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Analisis dan segmentasi perilaku pelanggan '
        'berdasarkan transaksi e-commerce.'
        '</div>',
        unsafe_allow_html=True
    )

    total_customers = df["CustomerID"].nunique()
    total_revenue = df["Monetary"].sum()
    total_clusters = df["Cluster"].nunique()
    avg_frequency = df["Frequency"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric(
        "Total Revenue",
        f"£{total_revenue / 1_000_000:.2f}M",
        help=f"Total penjualan: £{total_revenue:,.2f}"
    )
    col3.metric("Customer Segments", total_clusters)
    col4.metric("Average Frequency", f"{avg_frequency:.2f}")

    st.markdown("---")

    left, right = st.columns(2)
    cluster_counts = (
        df["Cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    cluster_counts.columns = ["Cluster", "Customers"]
    cluster_counts["Segment"] = cluster_counts["Cluster"].map(
        lambda cluster: f"Cluster {cluster}"
    )

    with left:
        st.subheader("Customer Distribution")
        fig = px.pie(
            cluster_counts,
            names="Segment",
            values="Customers",
            hole=0.55,
            title="Distribusi Pelanggan"
        )
        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("Customer Segments")
        fig = px.bar(
            cluster_counts,
            x="Segment",
            y="Customers",
            color="Segment",
            title="Jumlah Pelanggan per Segmen",
            text="Customers"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.subheader("RFM Overview")
    rfm_summary = df[
        ["Recency", "Frequency", "Monetary"]
    ].mean().reset_index()
    rfm_summary.columns = ["Metric", "Average"]

    fig = px.bar(
        rfm_summary,
        x="Metric",
        y="Average",
        color="Metric",
        title="Rata-rata Nilai RFM"
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Customer Data Preview")
    st.dataframe(df.head(10), width="stretch", hide_index=True)

elif menu == "Customer Segmentation":
    st.title("Customer Segmentation")
    st.write(
        "Analisis karakteristik pelanggan berdasarkan "
        "hasil algoritma K-Means."
    )

    profile = df.groupby("Cluster").agg(
        Jumlah_Pelanggan=("CustomerID", "count"),
        Recency=("Recency", "mean"),
        Frequency=("Frequency", "mean"),
        Monetary=("Monetary", "mean")
    ).round(2)

    st.subheader("Cluster Profile")
    st.dataframe(profile, width="stretch")

    selected_cluster = st.selectbox(
        "Pilih Cluster",
        sorted(df["Cluster"].unique())
    )

    filtered = df[df["Cluster"] == selected_cluster]

    st.metric(
        "Jumlah Pelanggan",
        f"{len(filtered):,}"
    )

    st.dataframe(filtered, width="stretch", hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Data Cluster",
        csv,
        file_name=f"cluster_{selected_cluster}.csv",
        mime="text/csv"
    )


# ==========================================
# MODEL EVALUATION
# ==========================================

elif menu == "Model Evaluation":
    st.title("Model Evaluation")

    try:
        evaluation = load_evaluation()
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
        st.error(f"Evaluasi model tidak dapat dimuat: {exc}")
        st.stop()

    st.subheader("Cluster Evaluation Results")
    st.dataframe(evaluation, width="stretch", hide_index=True)

    fig = px.line(
        evaluation,
        x="K",
        y="Inertia",
        markers=True,
        title="Elbow Method"
    )

    st.plotly_chart(fig, width="stretch")

    fig = px.line(
        evaluation,
        x="K",
        y="Silhouette",
        markers=True,
        title="Silhouette Score"
    )

    st.plotly_chart(fig, width="stretch")

    fig = px.line(
        evaluation,
        x="K",
        y="Davies_Bouldin",
        markers=True,
        title="Davies-Bouldin Index"
    )

    st.plotly_chart(fig, width="stretch")

    st.info(
        "Model final menggunakan K=3 berdasarkan "
        "Silhouette Score tertinggi dan "
        "Davies-Bouldin Index terendah."
    )


# ==========================================
# DATASET
# ==========================================

elif menu == "Dataset":
    st.title("Dataset Information")

    st.write(
        "Dataset Online Retail dari UCI Machine Learning Repository."
    )

    st.metric("Total Records", f"{len(df):,}")

    st.metric(
        "Total Customers",
        f"{df['CustomerID'].nunique():,}"
    )

    st.subheader("Dataset Preview")
    st.dataframe(df, width="stretch", hide_index=True)

    st.subheader("Statistical Description")

    st.dataframe(
        df[["Recency", "Frequency", "Monetary"]]
        .describe(),
        width="stretch"
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Dataset Segmentasi",
        csv,
        file_name="customer_segments.csv",
        mime="text/csv"
    )
