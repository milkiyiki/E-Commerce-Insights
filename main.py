import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import gdown

# Konfigurasi dashboard
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Judul Dashboard
st.title("📊 **E-Commerce Data Dashboard**")

# Load data
def load_data():
    file_id = "1BnsqMsDFyWjpEFgfB_aG_2yeIAPcg0OG" 
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    gdown.download(url, "ecommerce_cleaned_data.csv", quiet=False)

    df = pd.read_csv("ecommerce_cleaned_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_month"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
    return df

df = load_data()

# Sidebar - Filter
st.sidebar.header("📌 **Filter Data**")
selected_month = st.sidebar.selectbox("Pilih Bulan", df["order_month"].unique())

# Tambahkan filter kategori produk
selected_category = st.sidebar.multiselect("Pilih Kategori Produk", df["product_category_name"].unique(), default=df["product_category_name"].unique())

# Filter berdasarkan harga pembayaran
min_price, max_price = st.sidebar.slider("Range Harga Pembayaran (BRL)", float(df["payment_value"].min()), float(df["payment_value"].max()), (float(df["payment_value"].min()), float(df["payment_value"].max())))

# Terapkan filter
filtered_df = df[(df["order_month"] == selected_month) & 
                 (df["product_category_name"].isin(selected_category)) &
                 (df["payment_value"].between(min_price, max_price))]

# ======== SECTION 1: KPI Metrics ========
st.subheader("📌 **Statistik Utama**")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Pesanan", filtered_df["order_id"].nunique())

with col2:
    st.metric("Rata-rata Pembayaran (BRL)", round(filtered_df["payment_value"].mean(), 2))

with col3:
    st.metric("Rata-rata Rating", round(filtered_df["review_score"].mean(), 2))

# ======== SECTION 2: Tren Pesanan per Bulan (Plotly) ========
st.subheader("📊 **Tren Volume Pesanan**")

order_trend = df.groupby("order_month").size().reset_index(name="order_count")

fig = px.line(order_trend, x="order_month", y="order_count", markers=True, title="Tren Volume Pesanan per Bulan")
fig.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======== SECTION 3: Distribusi Rating Pelanggan ========
st.subheader("⭐ **Distribusi Rating Pelanggan**")

fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x="review_score", data=df, palette="viridis", ax=ax)
plt.title("Distribusi Review Score")
plt.xlabel("Review Score")
plt.ylabel("Jumlah Ulasan")
st.pyplot(fig)

# ======== SECTION 4: Top 10 Produk Terlaris ========
st.subheader("🔥 **Top 10 Produk Terlaris**")

top_products = df["product_category_name"].value_counts().reset_index()
top_products.columns = ["product_category", "total_orders"]
top_10_products = top_products.head(10)

fig = px.bar(top_10_products, x="product_category", y="total_orders", title="Top 10 Produk Terlaris", color="total_orders", text_auto=True)
fig.update_layout(xaxis_title="Kategori Produk", yaxis_title="Jumlah Pesanan", xaxis_tickangle=-45)
st.plotly_chart(fig)

# ======== SECTION 5: Word Cloud Kategori Produk ========
st.subheader("🔠 **Word Cloud Kategori Produk**")

wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(df["product_category_name"].dropna()))

fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# ======== SECTION 6: Heatmap Korelasi ========
st.subheader("📊 **Heatmap Korelasi Data**")

corr_matrix = df[["payment_value", "review_score"]].corr()

fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
plt.title("Korelasi Antar Variabel")
st.pyplot(fig)

# Footer
st.markdown("📌 **Dibuat oleh Risqienursalsabilailman**")
