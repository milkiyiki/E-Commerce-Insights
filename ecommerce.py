import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import os
import gdown

# Konfigurasi dashboard
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")
st.title("📊 **E-Commerce Data Dashboard**")

# Fungsi untuk load data
@st.cache_data
def load_data():
    file_id = "1yVmRLqssLDDnxPnRGzrjvELuZ4u49Gvx"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "ecommerce_cleaned_data.csv"

    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)

    df = pd.read_csv(output)

    # Lebih fleksibel dan aman
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    df = df.dropna(subset=["order_purchase_timestamp"])

    # Kolom tambahan
    df["order_month"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["year"] = df["order_purchase_timestamp"].dt.year
    return df

df = load_data()

# Sidebar - Filter
st.sidebar.header("📌 **Filter Data**")

# Filter Kategori Produk
selected_category = st.sidebar.multiselect(
    "Pilih Kategori Produk",
    df["product_category_name"].unique(),
    default=df["product_category_name"].unique()
)

# Filter Harga
min_price, max_price = st.sidebar.slider(
    "Range Harga Pembayaran (BRL)",
    float(df["payment_value"].min()),
    float(df["payment_value"].max()),
    (float(df["payment_value"].min()), float(df["payment_value"].max()))
)

# Gabungan semua filter
filtered_df = df[
    (df["product_category_name"].isin(selected_category)) &
    (df["payment_value"].between(min_price, max_price))
]

# ======= METRIK UTAMA =======
st.subheader("📌 **Statistik Utama**")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan", filtered_df["order_id"].nunique())
with col2:
    st.metric("Rata-rata Pembayaran (BRL)", round(filtered_df["payment_value"].mean(), 2))
with col3:
    st.metric("Rata-rata Rating", round(filtered_df["review_score"].mean(), 2))

# ======= TREN VOLUME PESANAN =======
st.subheader("📊 **Tren Volume Pesanan**")
order_trend = filtered_df.groupby("order_month").size().reset_index(name="order_count")
fig = px.line(order_trend, x="order_month", y="order_count", markers=True, title="Tren Volume Pesanan per Bulan")
fig.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======= MUSIMAN =======
st.subheader("📅 **Pola Musiman Pesanan**")
seasonality = filtered_df.groupby("month").size().reset_index(name="avg_order_count")
fig = px.bar(seasonality, x="month", y="avg_order_count", title="Rata-rata Pesanan per Bulan",
             labels={"month": "Bulan", "avg_order_count": "Rata-rata Jumlah Pesanan"}, color="avg_order_count", text_auto=True)
fig.update_xaxes(tickmode="array", tickvals=list(range(1, 13)),
                 ticktext=["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"])
st.plotly_chart(fig)

# ======= HUBUNGAN RATING & PEMBAYARAN =======
st.subheader("💰 **Hubungan Pembayaran dan Rating**")
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=filtered_df, x="review_score", y="payment_value", palette="viridis")
plt.xlabel("Rating Ulasan")
plt.ylabel("Nilai Pembayaran (BRL)")
plt.title("Distribusi Pembayaran Berdasarkan Skor Ulasan")
st.pyplot(fig)

fig = px.scatter(filtered_df, x="review_score", y="payment_value", title="Hubungan antara Rating dan Nilai Pembayaran",
                 labels={"review_score": "Rating", "payment_value": "Nilai Pembayaran (BRL)"},
                 color="review_score", opacity=0.6)
st.plotly_chart(fig)

# ======= DISTRIBUSI RATING =======
st.subheader("⭐ **Distribusi Rating Pelanggan**")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="review_score", data=filtered_df, palette="coolwarm", ax=ax)
plt.title("Distribusi Review Score")
plt.xlabel("Review Score")
plt.ylabel("Jumlah Ulasan")
st.pyplot(fig)

# ======= TOP 10 PRODUK =======
st.subheader("🔥 **Top 10 Produk Terlaris**")
top_products = filtered_df["product_category_name"].value_counts().reset_index()
top_products.columns = ["product_category", "total_orders"]
top_10_products = top_products.head(10)
fig = px.bar(top_10_products, x="product_category", y="total_orders", title="Top 10 Produk Terlaris",
             color="total_orders", text_auto=True)
fig.update_layout(xaxis_title="Kategori Produk", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======= WORD CLOUD =======
st.subheader("🔠 **Word Cloud Kategori Produk**")
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(filtered_df["product_category_name"].dropna()))
fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# ======= HEATMAP KORELASI =======
st.subheader("📊 **Heatmap Korelasi Data**")
corr_matrix = filtered_df[["payment_value", "review_score"]].corr()
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
plt.title("Korelasi Antar Variabel")
st.pyplot(fig)

# Footer
st.markdown("📌 **Dibuat oleh Risqienursalsabilailman**")
