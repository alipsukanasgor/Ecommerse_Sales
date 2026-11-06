
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Superstore | Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# THEME & CUSTOM CSS
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(145deg, #071426 0%, #0b1c31 55%, #10263c 100%);
    color: #edf5ff;
}

section[data-testid="stSidebar"] {
    background: #0b1a2c;
    border-right: 1px solid #1e3850;
}

section[data-testid="stSidebar"] * {
    color: #dce9f6;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: #f4f8fc;
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2.5rem;
    max-width: 1550px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #132b43, #10243a);
    border: 1px solid #24445d;
    padding: 17px 13px;
    border-radius: 16px;
    box-shadow: 0 8px 24px #00000020;
    min-width: 0;
    overflow: hidden;
}

div[data-testid="stMetricLabel"] {
    color: #9db4c9;
    font-size: 13px;
}

div[data-testid="stMetricValue"] {
    color: #f5fbff;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(17px, 1.6vw, 27px);
    white-space: nowrap;
}

div[data-testid="stMetricDelta"] {
    color: #35d6b2;
}

div[data-testid="stPlotlyChart"] {
    background: #10243a;
    border: 1px solid #203e57;
    border-radius: 16px;
    padding: 8px;
}

div[data-testid="stMultiSelect"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stSelectbox"] label {
    color: #c6d8e8;
}

hr {
    border-color: #24445d;
}

.small-muted {
    color: #91a9bf;
    font-size: 0.88rem;
}

.insight {
    background: #102a40;
    border: 1px solid #24506a;
    border-left: 4px solid #2dd4bf;
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: #dcebf6;
}

[data-testid="stExpander"] {
    background: #10243a;
    border: 1px solid #24445d;
    border-radius: 12px;
}

.stDownloadButton button {
    background: #0d9488;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

.stDownloadButton button:hover {
    background: #14b8a6;
    color: white;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATA LOADING
# =====================================================

BASE_DIR = Path(__file__).parent

# Automatically locate CSV in main folder or data folder
possible_files = [
    BASE_DIR / "superstore_clean.csv",
    BASE_DIR / "superstoreclean.csv",
    BASE_DIR / "Superstore_clean.csv",
    BASE_DIR / "data" / "superstore_clean.csv",
    BASE_DIR / "data" / "superstoreclean.csv"
]

DATA_PATH = next(
    (p for p in possible_files if p.exists()),
    None
)

if DATA_PATH is None:
    st.error(
        "Dataset tidak ditemukan. Letakkan file CSV di folder yang sama "
        "dengan app.py atau di dalam folder data."
    )
    st.stop()


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    required_columns = [
        "Order_Date", "Ship_Date", "Order_ID",
        "Customer_ID", "Customer_Name", "Region",
        "Category", "Sub-Category", "Product_Name",
        "Sales", "Quantity", "Discount", "Profit",
        "Segment"
    ]

    missing = [col for col in required_columns if col not in data.columns]

    if missing:
        raise ValueError(
            "Kolom dataset tidak lengkap: " + ", ".join(missing)
        )

    data["Order_Date"] = pd.to_datetime(
        data["Order_Date"], errors="coerce"
    )
    data["Ship_Date"] = pd.to_datetime(
        data["Ship_Date"], errors="coerce"
    )

    data = data.dropna(subset=["Order_Date"])

    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["Year"] = data["Order_Date"].dt.year
    data["Month"] = data["Order_Date"].dt.to_period("M").astype(str)
    data["Order_Month"] = (
        data["Order_Date"].dt.to_period("M").dt.to_timestamp()
    )

    return data


try:
    df = load_data(str(DATA_PATH))
except Exception as e:
    st.error(f"Gagal membaca dataset: {e}")
    st.stop()


# =====================================================
# SIDEBAR FILTERS
# =====================================================

with st.sidebar:

    st.markdown("## ◈ SUPERSTORE")
    st.caption("SALES INTELLIGENCE")

    st.markdown("---")
    st.markdown("### Filter Dashboard")

    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()

    date_range = st.date_input(
        "Periode pesanan",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    years = sorted(df["Year"].dropna().unique())

    selected_years = st.multiselect(
        "Tahun",
        years,
        default=years
    )

    all_categories = sorted(df["Category"].dropna().unique())

    categories = st.multiselect(
        "Kategori produk",
        all_categories,
        default=all_categories
    )

    all_subcategories = sorted(
        df["Sub-Category"].dropna().unique()
    )

    subcategories = st.multiselect(
        "Subkategori produk",
        all_subcategories,
        default=all_subcategories
    )

    all_regions = sorted(df["Region"].dropna().unique())

    regions = st.multiselect(
        "Wilayah",
        all_regions,
        default=all_regions
    )

    all_segments = sorted(df["Segment"].dropna().unique())

    segments = st.multiselect(
        "Segmen pelanggan",
        all_segments,
        default=all_segments
    )

    st.markdown("---")

    st.caption("Dataset: Sample Superstore")
    st.caption(
        f"Periode sumber: {min_date.year}–{max_date.year}"
    )
    st.caption(f"Total transaksi: {len(df):,}")


# =====================================================
# FILTER PROCESSING
# =====================================================

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])
else:
    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date)

f = df[
    df["Order_Date"].between(
        start_date,
        end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    )
    & df["Year"].isin(selected_years)
    & df["Category"].isin(categories)
    & df["Sub-Category"].isin(subcategories)
    & df["Region"].isin(regions)
    & df["Segment"].isin(segments)
].copy()


# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<div class='small-muted'>BUSINESS PERFORMANCE / OVERVIEW</div>",
    unsafe_allow_html=True
)

st.title("E-Commerce Sales Performance")

st.markdown(
    "<div class='small-muted'>"
    "Dashboard analisis penjualan, profitabilitas, produk, "
    "pelanggan, dan wilayah."
    "</div>",
    unsafe_allow_html=True
)

st.markdown("")


# =====================================================
# KPI CALCULATION
# =====================================================

sales = f["Sales"].sum()
profit = f["Profit"].sum()
orders = f["Order_ID"].nunique()
qty = f["Quantity"].sum()
customers = f["Customer_ID"].nunique()

margin = (profit / sales * 100) if sales != 0 else 0


# =====================================================
# KPI DISPLAY
# =====================================================

st.markdown("### Performance Overview")

k1, k2, k3, k4, k5 = st.columns(5, gap="medium")

with k1:
    st.metric("Total Sales", f"${sales:,.0f}")

with k2:
    st.metric("Total Profit", f"${profit:,.0f}")

with k3:
    st.metric("Unique Orders", f"{orders:,}")

with k4:
    st.metric("Units Sold", f"{qty:,.0f}")

with k5:
    st.metric("Profit Margin", f"{margin:.1f}%")

st.markdown("")


# =====================================================
# CUSTOMER SUMMARY
# =====================================================

c1, c2 = st.columns(2)

with c1:
    st.metric("Unique Customers", f"{customers:,}")

with c2:
    st.metric("Average Order Value",
              f"${sales / orders:,.2f}" if orders else "$0.00")


# =====================================================
# CHARTS
# =====================================================

if f.empty:

    st.warning(
        "Tidak ada data untuk kombinasi filter ini. "
        "Silakan ubah filter pada sidebar."
    )

else:

    # -------------------------------------------------
    # SALES TREND & REGION
    # -------------------------------------------------

    st.markdown("## Sales Performance")

    left, right = st.columns([1.65, 1])

    monthly = (
        f.groupby("Order_Month", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        )
    )

    with left:

        fig = px.line(
            monthly,
            x="Order_Month",
            y="Sales",
            markers=True,
            title="Sales Trend Over Time",
            labels={
                "Order_Month": "Bulan",
                "Sales": "Penjualan"
            }
        )

        fig.update_traces(
            line_color="#2dd4bf",
            marker_color="#8be9df",
            line_width=3,
            hovertemplate="%{x|%B %Y}<br>Sales: $%{y:,.2f}<extra></extra>"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=55, b=20),
            height=370
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        reg = (
            f.groupby("Region", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
        )

        fig = px.pie(
            reg,
            names="Region",
            values="Sales",
            hole=0.62,
            title="Sales by Region",
            color_discrete_sequence=[
                "#2dd4bf",
                "#60a5fa",
                "#f6bd60",
                "#a78bfa"
            ]
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=55, b=10),
            height=370,
            legend=dict(orientation="h", y=-0.12)
        )

        st.plotly_chart(fig, use_container_width=True)


    # -------------------------------------------------
    # CATEGORY & DISCOUNT
    # -------------------------------------------------

    st.markdown("## Product Analysis")

    left, right = st.columns(2)

    with left:

        cat = (
            f.groupby("Category", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        fig = px.bar(
            cat,
            x="Category",
            y="Sales",
            color="Category",
            title="Sales by Product Category",
            color_discrete_sequence=[
                "#2dd4bf",
                "#60a5fa",
                "#f6bd60"
            ],
            text_auto=",.0f"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=15, r=15, t=55, b=20),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        fig = px.scatter(
            f,
            x="Discount",
            y="Profit",
            color="Category",
            size="Sales",
            hover_name="Product_Name",
            title="Discount vs Profit",
            opacity=0.65,
            color_discrete_sequence=[
                "#2dd4bf",
                "#60a5fa",
                "#f6bd60"
            ]
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#f6bd60"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=55, b=20),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)


    # -------------------------------------------------
    # SUBCATEGORY & CUSTOMER SEGMENT
    # -------------------------------------------------

    st.markdown("## Profitability & Customer Analysis")

    left, right = st.columns(2)

    with left:

        sub = (
            f.groupby("Sub-Category", as_index=False)
            .agg(Profit=("Profit", "sum"))
            .sort_values("Profit")
        )

        fig = px.bar(
            sub,
            x="Profit",
            y="Sub-Category",
            orientation="h",
            title="Profit by Sub-Category",
            color="Profit",
            color_continuous_scale=[
                "#fb7185",
                "#f6bd60",
                "#2dd4bf"
            ]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=10, r=15, t=55, b=20),
            height=480
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        seg = (
            f.groupby("Segment", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        fig = px.bar(
            seg,
            x="Segment",
            y=["Sales", "Profit"],
            barmode="group",
            title="Sales & Profit by Customer Segment",
            color_discrete_sequence=[
                "#2dd4bf",
                "#f6bd60"
            ]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=15, r=15, t=55, b=20),
            height=480
        )

        st.plotly_chart(fig, use_container_width=True)


    # -------------------------------------------------
    # TOP PRODUCTS
    # -------------------------------------------------

    st.markdown("## Top Product Performance")

    top1, top2 = st.columns(2)

    product_sales = (
        f.groupby("Product_Name", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
        .head(10)
    )

    product_profit = (
        f.groupby("Product_Name", as_index=False)
        .agg(Profit=("Profit", "sum"))
        .sort_values("Profit", ascending=False)
        .head(10)
    )

    with top1:

        fig = px.bar(
            product_sales.sort_values("Sales"),
            x="Sales",
            y="Product_Name",
            orientation="h",
            title="Top 10 Products by Sales",
            color="Sales",
            color_continuous_scale=["#60a5fa", "#2dd4bf"]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            height=430,
            margin=dict(l=10, r=15, t=55, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    with top2:

        fig = px.bar(
            product_profit.sort_values("Profit"),
            x="Profit",
            y="Product_Name",
            orientation="h",
            title="Top 10 Products by Profit",
            color="Profit",
            color_continuous_scale=["#60a5fa", "#2dd4bf"]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            height=430,
            margin=dict(l=10, r=15, t=55, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)


    # =================================================
    # KEY INSIGHTS
    # =================================================

    st.markdown("## Key Business Insights")

    best_region = f.groupby("Region")["Sales"].sum().idxmax()
    worst_region = f.groupby("Region")["Sales"].sum().idxmin()

    best_cat = f.groupby("Category")["Sales"].sum().idxmax()

    sub_profit = f.groupby("Sub-Category")["Profit"].sum()

    best_sub = sub_profit.idxmax()
    worst_sub = sub_profit.idxmin()

    best_product = (
        f.groupby("Product_Name")["Sales"].sum().idxmax()
    )

    worst_product = (
        f.groupby("Product_Name")["Profit"].sum().idxmin()
    )

    insights = [
        f"<b>Wilayah terkuat:</b> {best_region} mencatat penjualan tertinggi.",
        f"<b>Kategori unggulan:</b> {best_cat} menjadi kontributor penjualan terbesar.",
        f"<b>Produk paling menguntungkan:</b> {best_sub} merupakan subkategori dengan profit tertinggi.",
        f"<b>Perlu evaluasi:</b> {worst_sub} memiliki total profit terendah (${sub_profit.min():,.2f}).",
        f"<b>Produk terlaris:</b> {best_product} memiliki nilai penjualan tertinggi.",
        f"<b>Produk dengan profit terendah:</b> {worst_product}. Perlu evaluasi strategi penjualan.",
        f"<b>Wilayah terendah:</b> {worst_region} mencatat penjualan paling rendah."
    ]

    for insight in insights:
        st.markdown(
            f"<div class='insight'>{insight}</div>",
            unsafe_allow_html=True
        )


# =====================================================
# TRANSACTION DETAILS & DOWNLOAD
# =====================================================

st.markdown("---")
st.markdown("## Transaction Details")

with st.expander("Lihat detail data transaksi"):

    cols = [
        "Order_ID",
        "Order_Date",
        "Customer_Name",
        "Region",
        "Category",
        "Sub-Category",
        "Product_Name",
        "Sales",
        "Quantity",
        "Discount",
        "Profit"
    ]

    detail = f[cols].sort_values(
        "Order_Date",
        ascending=False
    )

    st.dataframe(
        detail,
        use_container_width=True,
        hide_index=True
    )

    csv = detail.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇ Download Data Hasil Filter (CSV)",
        data=csv,
        file_name="superstore_filtered.csv",
        mime="text/csv"
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div class='small-muted' style='text-align:center;'>
        E-Commerce Sales Performance Dashboard
        <br>
        UTS Visualisasi Data • Sample Superstore
        <br>
        Built with Python, Streamlit & Plotly
    </div>
    """,
    unsafe_allow_html=True
)
