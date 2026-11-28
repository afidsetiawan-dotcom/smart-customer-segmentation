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
RFM_COLUMNS = {"CustomerID", "Recency", "Frequency", "Monetary"}
EVALUATION_COLUMNS = {"K", "Inertia", "Silhouette", "Davies_Bouldin"}
TRANSACTION_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
    "TotalPrice",
}
SEGMENT_NAMES = {
    0: "High Value Customers",
    1: "At Risk Customers",
    2: "Regular Customers",
}
RFM_LABELS = {
    "Recency": "Hari sejak transaksi terakhir",
    "Frequency": "Jumlah transaksi",
    "Monetary": "Total belanja (£)",
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


def validate_required_columns(data, required_columns, source):
    """Memastikan data memiliki kolom yang dibutuhkan."""

    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{source} tidak memiliki kolom wajib: {missing}.")


def validate_data_columns(df, source):
    """Memastikan sumber data memiliki kolom yang digunakan aplikasi."""

    validate_required_columns(df, REQUIRED_COLUMNS, source)

    for column in ("Recency", "Frequency", "Monetary", "Cluster"):
        try:
            df[column] = pd.to_numeric(df[column], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Kolom {column} pada {source} harus berisi angka."
            ) from exc

    missing_values = [
        column for column in REQUIRED_COLUMNS if df[column].isna().any()
    ]
    if missing_values:
        columns = ", ".join(sorted(missing_values))
        raise ValueError(
            f"{source} memiliki nilai kosong pada kolom wajib: {columns}."
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
        "RFM Analysis",
        "Clustering Evaluation",
        "Dataset"
    ],
    key="navigation",
)
st.sidebar.caption(
    "Pilih halaman untuk berpindah antara ringkasan, analisis, dan data."
)

st.sidebar.markdown("---")
st.sidebar.caption("Machine Learning Project")
st.sidebar.caption("K-Means Clustering")


@st.cache_data(ttl=60)
def load_evaluation():
    """Membaca metrik evaluasi clustering yang sudah tersimpan."""

    evaluation_path = DATA_DIR / "cluster_evaluation.csv"
    if not evaluation_path.is_file():
        raise FileNotFoundError(
            f"File evaluasi clustering tidak ditemukan: {evaluation_path}."
        )

    evaluation = pd.read_csv(evaluation_path)
    if evaluation.empty:
        raise ValueError("File evaluasi clustering kosong.")

    validate_required_columns(
        evaluation,
        EVALUATION_COLUMNS,
        "File evaluasi clustering",
    )
    for column in EVALUATION_COLUMNS:
        try:
            evaluation[column] = pd.to_numeric(
                evaluation[column],
                errors="raise",
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Kolom {column} pada file evaluasi harus berisi angka."
            ) from exc

    if evaluation[list(EVALUATION_COLUMNS)].isna().any().any():
        raise ValueError(
            "File evaluasi clustering memiliki nilai kosong."
        )

    evaluation = evaluation[evaluation["K"].between(2, 8)].copy()
    if evaluation["K"].duplicated().any():
        raise ValueError(
            "File evaluasi clustering memiliki nilai K yang berulang."
        )

    missing_k = set(range(2, 9)).difference(
        evaluation["K"].astype(int)
    )
    if missing_k:
        missing = ", ".join(str(k) for k in sorted(missing_k))
        raise ValueError(
            f"File evaluasi clustering tidak memiliki hasil untuk K: {missing}."
        )

    return evaluation.sort_values("K")


@st.cache_data(ttl=60)
def load_rfm_data():
    """Membaca data RFM pelanggan dari CSV hasil pemrosesan."""

    rfm_path = DATA_DIR / "rfm_data.csv"
    if not rfm_path.is_file():
        raise FileNotFoundError(f"File data RFM tidak ditemukan: {rfm_path}.")

    rfm_data = pd.read_csv(rfm_path)
    if rfm_data.empty:
        raise ValueError("File data RFM kosong.")

    validate_required_columns(rfm_data, RFM_COLUMNS, "File data RFM")
    for column in ("Recency", "Frequency", "Monetary"):
        try:
            rfm_data[column] = pd.to_numeric(
                rfm_data[column],
                errors="raise",
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Kolom {column} pada file data RFM harus berisi angka."
            ) from exc

    if rfm_data[list(RFM_COLUMNS)].isna().any().any():
        raise ValueError("File data RFM memiliki nilai kosong.")

    return rfm_data


@st.cache_data(ttl=60)
def load_transaction_preview():
    """Menghitung baris transaksi dan memuat preview secara bertahap."""

    transaction_path = DATA_DIR / "cleaned_retail.csv"
    if not transaction_path.is_file():
        raise FileNotFoundError(
            f"File data transaksi tidak ditemukan: {transaction_path}."
        )

    header = pd.read_csv(transaction_path, nrows=0)
    validate_required_columns(
        header,
        TRANSACTION_COLUMNS,
        "File data transaksi",
    )

    preview = pd.read_csv(transaction_path, nrows=10)
    row_count = 0
    for chunk in pd.read_csv(
        transaction_path,
        usecols=["InvoiceNo"],
        chunksize=100_000,
    ):
        row_count += len(chunk)

    if row_count == 0 or preview.empty:
        raise ValueError("File data transaksi kosong.")

    return row_count, header.columns.tolist(), preview


def summarize_clusters(data):
    """Menghitung ukuran dan karakteristik aktual setiap cluster."""

    summary = (
        data.groupby("Cluster")
        .agg(
            Customers=("CustomerID", "nunique"),
            Recency=("Recency", "mean"),
            Frequency=("Frequency", "mean"),
            Monetary=("Monetary", "mean"),
            MonetaryTotal=("Monetary", "sum"),
        )
        .reset_index()
        .rename(columns={"MonetaryTotal": "Monetary Total"})
    )
    customer_count = data["CustomerID"].nunique()
    summary["Customer Share (%)"] = (
        summary["Customers"] / customer_count * 100
    )
    total_monetary = data["Monetary"].sum()
    summary["Monetary Contribution (%)"] = (
        summary["Monetary Total"] / total_monetary * 100
        if total_monetary != 0
        else 0
    )
    summary["Segment"] = summary["Cluster"].map(
        lambda cluster: SEGMENT_NAMES.get(
            int(cluster),
            f"Cluster {cluster}",
        )
    )
    return summary


def describe_cluster(row, profile):
    """Membuat interpretasi dan strategi dari perbandingan nilai RFM aktual."""

    def relative_position(metric):
        values = profile[metric]
        if values.nunique() == 1:
            return "setara"
        if row[metric] == values.min():
            return "terendah"
        if row[metric] == values.max():
            return "tertinggi"
        return "menengah"

    recency_position = relative_position("Recency")
    frequency_position = relative_position("Frequency")
    monetary_position = relative_position("Monetary")
    recency_text = {
        "terendah": "lebih baru bertransaksi",
        "tertinggi": "paling lama tidak bertransaksi",
        "menengah": "memiliki Recency di tingkat menengah",
        "setara": "memiliki Recency yang setara dengan cluster lain",
    }[recency_position]
    frequency_text = {
        "terendah": "paling jarang bertransaksi",
        "tertinggi": "paling sering bertransaksi",
        "menengah": "memiliki Frequency di tingkat menengah",
        "setara": "memiliki Frequency yang setara dengan cluster lain",
    }[frequency_position]
    monetary_text = {
        "terendah": "rata-rata belanja terendah",
        "tertinggi": "rata-rata belanja tertinggi",
        "menengah": "memiliki rata-rata belanja di tingkat menengah",
        "setara": "memiliki Monetary rata-rata yang setara dengan cluster lain",
    }[monetary_position]
    characteristics = (
        f"Relatif terhadap cluster lain, pelanggan di sini {recency_text}, "
        f"{frequency_text}, dan {monetary_text}."
    )

    if recency_position == "tertinggi":
        strategy = (
            "Prioritaskan kampanye win-back yang terarah; uji pengingat "
            "dan insentif pembelian kembali pada pelanggan yang lama tidak aktif."
        )
    elif monetary_position == "tertinggi":
        strategy = (
            "Pertahankan pelanggan bernilai tinggi melalui layanan loyalitas "
            "dan rekomendasi yang relevan; hindari diskon massal yang tidak perlu."
        )
    elif frequency_position == "terendah":
        strategy = (
            "Dorong transaksi berikutnya dengan pengingat yang relevan, "
            "bundel, atau manfaat loyalitas setelah pembelian."
        )
    else:
        strategy = (
            "Dorong pembelian berulang dan cross-sell yang relevan, lalu "
            "ukur respons sebelum memperluas promosi."
        )

    return characteristics, strategy


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
        '<div class="main-title">Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Ringkasan data per pelanggan: RFM merangkum kebaruan, frekuensi, '
        'dan nilai belanja; K-Means mengelompokkan pelanggan dengan pola RFM serupa.'
        '</div>',
        unsafe_allow_html=True
    )

    total_customers = df["CustomerID"].nunique()
    total_revenue = df["Monetary"].sum()
    total_clusters = df["Cluster"].nunique()
    avg_frequency = df["Frequency"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Customers",
        f"{total_customers:,}",
        help="Jumlah CustomerID unik yang tercakup dalam hasil segmentasi.",
    )
    col2.metric(
        "Total Revenue",
        f"£{total_revenue / 1_000_000:.2f}M",
        help=(
            "Jumlah Monetary seluruh pelanggan pada data segmentasi: "
            f"£{total_revenue:,.2f}."
        ),
    )
    col3.metric(
        "Customer Segments",
        total_clusters,
        help="Jumlah label cluster yang terdapat pada data segmentasi.",
    )
    col4.metric(
        "Average Frequency",
        f"{avg_frequency:.2f}",
        help="Rata-rata jumlah invoice unik per pelanggan dalam periode dataset.",
    )

    st.markdown("---")

    cluster_summary = summarize_clusters(df)
    left, right = st.columns(2)

    with left:
        st.subheader("Customer Distribution")
        fig = px.pie(
            cluster_summary,
            names="Segment",
            values="Customers",
            hole=0.55,
            title="Distribusi Pelanggan"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(
            fig,
            width="stretch",
            alt="Proporsi pelanggan pada setiap segmen",
        )

    with right:
        st.subheader("Customer Segments")
        fig = px.bar(
            cluster_summary,
            x="Segment",
            y="Monetary Total",
            color="Segment",
            title="Kontribusi Monetary per Segmen",
            labels={
                "Segment": "Segmen pelanggan",
                "Monetary Total": "Total nilai belanja (£)",
            },
            text="Monetary Total",
            hover_data={"Monetary Contribution (%)": ":.2f"},
        )
        fig.update_traces(
            texttemplate="£%{y:,.0f}",
            textposition="outside",
        )
        fig.update_yaxes(tickprefix="£", tickformat=",.0f")
        st.plotly_chart(
            fig,
            width="stretch",
            alt="Kontribusi nilai Monetary dari setiap segmen pelanggan",
        )

    st.markdown("---")
    st.subheader("RFM Overview")
    rfm_means = df[["Recency", "Frequency", "Monetary"]].mean()
    rfm_cols = st.columns(3)
    rfm_cols[0].metric(
        "Average Recency",
        f"{rfm_means['Recency']:.1f} days",
        help=(
            "Rata-rata hari sejak transaksi terakhir; lebih kecil berarti "
            "lebih baru bertransaksi."
        ),
    )
    rfm_cols[1].metric(
        "Mean Frequency per Customer",
        f"{rfm_means['Frequency']:.2f} transactions",
        help="Rata-rata jumlah invoice unik per pelanggan dalam periode dataset.",
    )
    rfm_cols[2].metric(
        "Average Monetary",
        f"£{rfm_means['Monetary']:,.2f}",
        help="Rata-rata total belanja per pelanggan.",
    )

    st.subheader("Customer Data Preview")
    st.dataframe(
        df.head(10),
        width="stretch",
        hide_index=True,
        alt="Preview data pelanggan hasil clustering",
    )

elif menu == "Customer Segmentation":
    st.title("Customer Segmentation")
    st.write(
        "K-Means mengelompokkan pelanggan berdasarkan kemiripan nilai RFM. "
        "Nilai RFM dan kontribusi Monetary di bawah dihitung langsung dari "
        "data pelanggan pada setiap cluster."
    )

    profile = summarize_clusters(df)

    st.subheader("Distribusi Cluster")
    distribution_chart = px.bar(
        profile,
        x="Segment",
        y="Customers",
        color="Segment",
        text="Customers",
        title="Jumlah dan Proporsi Pelanggan per Segmen",
        hover_data={"Customer Share (%)": ":.2f"},
    )
    distribution_chart.update_traces(textposition="outside")
    st.plotly_chart(
        distribution_chart,
        width="stretch",
        alt="Jumlah dan persentase pelanggan pada setiap cluster",
    )

    profile_table = profile[
        [
            "Cluster",
            "Segment",
            "Customers",
            "Customer Share (%)",
            "Recency",
            "Frequency",
            "Monetary",
            "Monetary Total",
            "Monetary Contribution (%)",
        ]
    ].rename(
        columns={
            "Customers": "Jumlah Pelanggan",
            "Customer Share (%)": "Porsi Pelanggan (%)",
            "Recency": "Rata-rata Recency (hari)",
            "Frequency": "Rata-rata Frequency (transaksi)",
            "Monetary": "Rata-rata Monetary (£)",
            "Monetary Total": "Total Monetary (£)",
            "Monetary Contribution (%)": "Kontribusi Monetary (%)",
        }
    ).round(2)
    for column in ("Rata-rata Monetary (£)", "Total Monetary (£)"):
        profile_table[column] = profile_table[column].map(
            lambda value: f"£{value:,.2f}"
        )
    st.subheader("Karakteristik RFM per Cluster")
    st.dataframe(
        profile_table,
        width="stretch",
        hide_index=True,
        alt="Perbandingan ukuran dan nilai RFM setiap cluster",
    )

    st.subheader("Karakteristik dan Strategi Pemasaran")
    segment_cards = st.columns(max(len(profile), 1))
    for column, (_, row) in zip(segment_cards, profile.iterrows()):
        cluster_id = int(row["Cluster"])
        characteristics, strategy = describe_cluster(row, profile)
        with column:
            with st.container(border=True):
                st.subheader(row["Segment"])
                st.caption(
                    f"Cluster {cluster_id} · "
                    f"{row['Customers']:,} pelanggan · "
                    f"{row['Customer Share (%)']:.1f}% dari pelanggan"
                )
                st.write(characteristics)
                st.write(
                    f"Rata-rata: Recency {row['Recency']:.1f} hari, "
                    f"Frequency {row['Frequency']:.2f} transaksi, "
                    f"Monetary £{row['Monetary']:,.2f}."
                )
                st.write(
                    f"Kontribusi Monetary: £{row['Monetary Total']:,.2f} "
                    f"({row['Monetary Contribution (%)']:.2f}% dari total)."
                )
                st.markdown(f"**Strategi:** {strategy}")

    selected_cluster = st.selectbox(
        "Pilih Cluster",
        sorted(df["Cluster"].unique()),
    )

    filtered = df[df["Cluster"] == selected_cluster]

    selected_name = SEGMENT_NAMES.get(
        int(selected_cluster),
        f"Cluster {selected_cluster}",
    )
    st.subheader(f"Daftar Pelanggan — {selected_name}")
    st.metric(
        "Jumlah Pelanggan",
        f"{filtered['CustomerID'].nunique():,}",
        help="Jumlah pelanggan unik di cluster yang dipilih.",
    )

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
        alt=f"Data pelanggan pada segmen {selected_name}",
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Data Cluster",
        csv,
        file_name=f"cluster_{selected_cluster}.csv",
        mime="text/csv"
    )


elif menu == "RFM Analysis":
    st.title("RFM Analysis")
    st.write(
        "RFM menyederhanakan riwayat transaksi menjadi tiga metrik per pelanggan. "
        "Grafik menggunakan data agregat yang sama dengan hasil segmentasi."
    )

    try:
        rfm_data = load_rfm_data()
    except (FileNotFoundError, OSError, ValueError) as exc:
        st.error(f"Analisis RFM tidak dapat dimuat: {exc}")
        st.stop()

    st.metric(
        "Pelanggan dianalisis",
        f"{rfm_data['CustomerID'].nunique():,}",
        help="Jumlah CustomerID unik pada file hasil perhitungan RFM.",
    )

    rfm_summary = rfm_data[
        ["Recency", "Frequency", "Monetary"]
    ].describe().T
    rfm_summary.index.name = "Metrik"
    rfm_summary = rfm_summary.reset_index()
    rfm_summary["Metrik"] = rfm_summary["Metrik"].map(RFM_LABELS)
    monetary_row = rfm_summary["Metrik"] == RFM_LABELS["Monetary"]
    for column in ("mean", "std", "min", "25%", "50%", "75%", "max"):
        rfm_summary[column] = rfm_summary[column].map(
            lambda value: f"{value:,.2f}"
        )
        rfm_summary.loc[monetary_row, column] = (
            "£" + rfm_summary.loc[monetary_row, column]
        )
    st.subheader("Ringkasan Statistik RFM")
    st.dataframe(
        rfm_summary.round(2),
        width="stretch",
        hide_index=True,
        alt="Statistik ringkasan Recency, Frequency, dan Monetary",
    )

    st.subheader("Distribusi RFM")
    chart_columns = st.columns(3)
    for column, metric in zip(
        chart_columns,
        ("Recency", "Frequency", "Monetary"),
    ):
        figure = px.histogram(
            rfm_data,
            x=metric,
            nbins=40,
            title=RFM_LABELS[metric],
            labels={metric: RFM_LABELS[metric]},
        )
        figure.update_layout(yaxis_title="Jumlah pelanggan")
        if metric in {"Frequency", "Monetary"} and (
            rfm_data[metric] > 0
        ).all():
            figure.update_xaxes(type="log")
        if metric == "Monetary":
            figure.update_xaxes(tickprefix="£", tickformat=",.0f")
        elif metric == "Frequency":
            figure.update_xaxes(title_text="Jumlah transaksi (skala log)")
        else:
            figure.update_xaxes(title_text="Hari sejak transaksi terakhir")
        figure.update_yaxes(title_text="Jumlah pelanggan")
        with column:
            st.plotly_chart(
                figure,
                width="stretch",
                alt=f"Distribusi pelanggan berdasarkan {RFM_LABELS[metric]}",
            )

    st.subheader("Arti Metrik")
    explanation_columns = st.columns(3)
    explanations = (
        (
            "Recency",
            "Jumlah hari sejak pelanggan terakhir kali bertransaksi. "
            "Nilai lebih kecil berarti pelanggan lebih baru berbelanja.",
        ),
        (
            "Frequency",
            "Jumlah transaksi pelanggan dalam periode data. "
            "Nilai lebih besar berarti pelanggan lebih sering berbelanja.",
        ),
        (
            "Monetary",
            "Total nilai belanja pelanggan. Nilai lebih besar menunjukkan "
            "kontribusi belanja yang lebih tinggi.",
        ),
    )
    for column, (metric, description) in zip(
        explanation_columns,
        explanations,
    ):
        with column:
            with st.container(border=True):
                st.markdown(f"**{metric}**")
                st.write(description)


# ==========================================
# MODEL EVALUATION
# ==========================================

elif menu == "Clustering Evaluation":
    st.title("Clustering Evaluation")
    st.write(
        "Halaman ini membandingkan hasil evaluasi yang sudah tersimpan untuk "
        "K=2 sampai K=8; tidak ada pelatihan ulang saat aplikasi dibuka."
    )

    try:
        evaluation = load_evaluation()
    except (FileNotFoundError, OSError, ValueError) as exc:
        st.error(f"Evaluasi model tidak dapat dimuat: {exc}")
        st.stop()

    st.subheader("Hasil evaluasi cluster")
    st.caption(
        "Inertia mengukur kekompakan dalam cluster (lebih rendah lebih baik, "
        "namun biasanya turun saat K bertambah). Silhouette mengukur pemisahan "
        "cluster (lebih tinggi lebih baik). Davies-Bouldin mengukur kemiripan "
        "antarcluster (lebih rendah lebih baik)."
    )
    st.dataframe(
        evaluation.round(4),
        width="stretch",
        hide_index=True,
        alt="Perbandingan metrik evaluasi untuk K dua hingga delapan",
    )

    fig = px.line(
        evaluation,
        x="K",
        y="Inertia",
        markers=True,
        title="Elbow Method",
        labels={
            "K": "Jumlah cluster (K)",
            "Inertia": "Inertia (jumlah kuadrat jarak)",
        },
    )
    fig.update_xaxes(tickmode="linear", dtick=1)
    st.plotly_chart(
        fig,
        width="stretch",
        alt="Inertia menurun saat jumlah cluster bertambah dari dua sampai delapan",
    )

    fig = px.line(
        evaluation,
        x="K",
        y="Silhouette",
        markers=True,
        title="Silhouette Score",
        labels={
            "K": "Jumlah cluster (K)",
            "Silhouette": "Silhouette score",
        },
    )
    fig.update_xaxes(tickmode="linear", dtick=1)
    st.plotly_chart(
        fig,
        width="stretch",
        alt="Silhouette score untuk setiap jumlah cluster yang diuji",
    )

    fig = px.line(
        evaluation,
        x="K",
        y="Davies_Bouldin",
        markers=True,
        title="Davies-Bouldin Index",
        labels={
            "K": "Jumlah cluster (K)",
            "Davies_Bouldin": "Davies-Bouldin Index",
        },
    )
    fig.update_xaxes(tickmode="linear", dtick=1)
    st.plotly_chart(
        fig,
        width="stretch",
        alt="Davies-Bouldin Index untuk setiap jumlah cluster yang diuji",
    )

    best_silhouette = evaluation.loc[evaluation["Silhouette"].idxmax()]
    best_davies_bouldin = evaluation.loc[
        evaluation["Davies_Bouldin"].idxmin()
    ]
    k2_inertia = evaluation.loc[evaluation["K"] == 2, "Inertia"].iloc[0]
    k3_inertia = evaluation.loc[evaluation["K"] == 3, "Inertia"].iloc[0]
    k4_inertia = evaluation.loc[evaluation["K"] == 4, "Inertia"].iloc[0]

    if (
        int(best_silhouette["K"]) == 3
        and int(best_davies_bouldin["K"]) == 3
    ):
        st.info(
            "K=3 dipilih karena hasil aktual memberikan Silhouette Score "
            f"tertinggi ({best_silhouette['Silhouette']:.4f}) dan "
            "Davies-Bouldin Index terendah "
            f"({best_davies_bouldin['Davies_Bouldin']:.4f}). "
            f"Inertia turun dari {k2_inertia:,.2f} (K=2) menjadi "
            f"{k3_inertia:,.2f} (K=3); penurunan berikutnya ke K=4 "
            f"lebih kecil ({k3_inertia - k4_inertia:,.2f})."
        )
    else:
        st.info(
            "Evaluasi aktual menunjukkan Silhouette Score tertinggi pada "
            f"K={int(best_silhouette['K'])} dan Davies-Bouldin Index "
            f"terendah pada K={int(best_davies_bouldin['K'])}. "
            "Model dan hasil clustering yang ada tetap menggunakan K=3."
        )


# ==========================================
# DATASET
# ==========================================

elif menu == "Dataset":
    st.title("Dataset")
    st.markdown(
        "Sumber transaksi: [UCI Machine Learning Repository — "
        "Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail). "
        "CSV transaksi berikut berisi baris transaksi setelah pembersihan; "
        "data pelanggan di bawahnya merupakan hasil agregasi RFM dan clustering. "
        "Gunakan bagian transaksi untuk melihat baris item, dan bagian pelanggan "
        "untuk melihat ringkasan per CustomerID."
    )

    try:
        transaction_rows, transaction_columns, transaction_preview = (
            load_transaction_preview()
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        st.error(f"Informasi data transaksi tidak dapat dimuat: {exc}")
        st.stop()

    st.subheader("Data Transaksi")
    st.caption(
        "Satu baris merepresentasikan item transaksi setelah pembersihan; "
        "data ini tetap berbeda dari agregat pelanggan."
    )
    transaction_metrics = st.columns(2)
    transaction_metrics[0].metric("Jumlah Baris Transaksi", f"{transaction_rows:,}")
    transaction_metrics[1].metric("Jumlah Kolom", len(transaction_columns))
    st.write("Kolom:", ", ".join(transaction_columns))
    st.dataframe(
        transaction_preview,
        width="stretch",
        hide_index=True,
        alt="Preview sepuluh baris data transaksi setelah pembersihan",
    )

    st.subheader("Data Agregat Pelanggan")
    st.caption(
        "Satu baris merepresentasikan satu pelanggan dengan metrik Recency, "
        "Frequency, Monetary, dan label Cluster."
    )
    customer_metrics = st.columns(3)
    customer_metrics[0].metric("Jumlah Baris Pelanggan", f"{len(df):,}")
    customer_metrics[1].metric(
        "Pelanggan Unik",
        f"{df['CustomerID'].nunique():,}",
    )
    customer_metrics[2].metric("Jumlah Kolom", len(df.columns))
    st.write("Kolom:", ", ".join(df.columns))
    st.dataframe(
        df.head(10),
        width="stretch",
        hide_index=True,
        alt="Preview sepuluh baris data pelanggan hasil clustering",
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Dataset Segmentasi",
        csv,
        file_name="customer_segments.csv",
        mime="text/csv"
    )


st.markdown("---")
st.caption("App by Afid © 2026")
