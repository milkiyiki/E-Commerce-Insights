import streamlit as st
import pandas as pd
import plotly.express as px
import gdown
import os

# Konfigurasi dashboard
st.set_page_config(page_title="E-Commerce Dashboard Baru", layout="wide")
st.title("📊 **E-Commerce Data Dashboard Baru**")

# Fungsi untuk load data
@st.cache_data
def load_data():
    file_id = "1yVmRLqssLDDnxPnRGzrjvELuZ4u49Gvx"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "ecommerce_cleaned_data.csv"

    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    df = pd.read_csv(output)

    # Mengubah kolom tanggal
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    df = df.dropna(subset=["order_purchase_timestamp"])

    # Kolom tambahan untuk mempermudah analisis
    df["order_month"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["year"] = df["order_purchase_timestamp"].dt.year
    return df

# Load Data
df = load_data()

# Sidebar - Filter
st.sidebar.header("📌 **Filter Data**")

# Filter Tanggal
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [df["order_purchase_timestamp"].min(), df["order_purchase_timestamp"].max()]
)

# Pastikan ada dua tanggal yang dipilih
if isinstance(date_range, list) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_filtered = df[(df["order_purchase_timestamp"] >= start_date) & (df["order_purchase_timestamp"] <= end_date)]
else:
    st.sidebar.warning("Harap pilih dua tanggal untuk melakukan filter.")
    df_filtered = df

# ======= METRIK UTAMA =======
st.subheader("📌 **Statistik Utama**")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan", df_filtered["order_id"].nunique())
with col2:
    st.metric("Rata-rata Pembayaran (BRL)", round(df_filtered["payment_value"].mean(), 2))
with col3:
    st.metric("Rata-rata Rating", round(df_filtered["review_score"].mean(), 2))

# ======= TREN VOLUME PESANAN =======
st.subheader("📊 **Tren Volume Pesanan**")
order_trend = df_filtered.groupby("order_month").size().reset_index(name="order_count")
fig = px.line(order_trend, x="order_month", y="order_count", markers=True, title="Tren Volume Pesanan per Bulan")
fig.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======= MUSIMAN =======
st.subheader("📅 **Pola Musiman Pesanan**")
seasonality = df_filtered.groupby("month").size().reset_index(name="avg_order_count")
fig = px.bar(seasonality, x="month", y="avg_order_count", title="Rata-rata Pesanan per Bulan",
             labels={"month": "Bulan", "avg_order_count": "Rata-rata Jumlah Pesanan"}, color="avg_order_count", text_auto=True)
fig.update_xaxes(tickmode="array", tickvals=list(range(1, 13)),
                 ticktext=["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"])
st.plotly_chart(fig)

# ======= HUBUNGAN RATING & PEMBAYARAN =======
st.subheader("💰 **Hubungan Pembayaran dan Rating**")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df_filtered, x="review_score", y="payment_value", palette="viridis")
plt.xlabel("Rating Ulasan")
plt.ylabel("Nilai Pembayaran (BRL)")
plt.title("Distribusi Pembayaran Berdasarkan Skor Ulasan")
st.pyplot(fig)

# ======= DISTRIBUSI RATING =======
st.subheader("⭐ **Distribusi Rating Pelanggan**")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="review_score", data=df_filtered, palette="coolwarm", ax=ax)
plt.title("Distribusi Review Score")
plt.xlabel("Review Score")
plt.ylabel("Jumlah Ulasan")
st.pyplot(fig)

# ======= TOP 10 PRODUK =======
st.subheader("🔥 **Top 10 Produk Terlaris**")
top_products = df_filtered["product_category_name"].value_counts().reset_index()
top_products.columns = ["product_category", "total_orders"]
top_10_products = top_products.head(10)
fig = px.bar(top_10_products, x="product_category", y="total_orders", title="Top 10 Produk Terlaris",
             color="total_orders", text_auto=True)
fig.update_layout(xaxis_title="Kategori Produk", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======= WORD CLOUD =======
st.subheader("🔠 **Word Cloud Kategori Produk**")
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(df_filtered["product_category_name"].dropna()))
fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# ======= HEATMAP KORELASI =======
st.subheader("📊 **Heatmap Korelasi Data**")
corr_matrix = df_filtered[["payment_value", "review_score"]].corr()
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
plt.title("Korelasi Antar Variabel")
st.pyplot(fig)

# Footer
st.markdown("📌 **Dibuat oleh Risqienursalsabilailman**")
