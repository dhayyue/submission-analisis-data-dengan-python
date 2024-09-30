import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
import math
from babel.numbers import format_currency
sns.set(style='dark')
from func import DataAnalyzer, MapPlotter

#dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_data = pd.read_csv("all_data.csv")
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

geolocation = pd.read_csv("D:/kuliah/stupen/Dicoding/Submission/proyek_analisis_data/geolocation_dataset.csv")
data = geolocation

for col in datetime_cols:
    all_data[col] = pd.to_datetime(all_data[col])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

#sidebar
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("logo.jpeg"
                 , width=250)
    with col2:
        st.write(' ')
    
    with col3:
        st.write(' ')
        
 # Date Range
    start_date, end_date = st.date_input(
        label="Masukkan Rentang Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_data[(all_data["order_approved_at"] >= str(start_date)) & 
                 (all_data["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = MapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
rfm_df = function.create_rfm_df()
state, most_common_state = function.create_bystate_df()

# Define your Streamlit app
st.title("E-Commerce Public Data Analysis")

# Membuat kolom untuk menampilkan Total Penjualan dan Total Pelanggan
st.subheader("Ringkasan Penjualan")

# Judul utama untuk dashboard
st.write("**Dashboard Analisis Penjualan E-Commerce**")

st.subheader("Total Pemesanan")
col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df["order_count"].sum()
    formatted_total_order = "{:.2f}".format(total_order)
    st.markdown(f"Total Pemesanan: **{formatted_total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    formatted_total_revenue = "{:.2f}".format(total_revenue)
    st.markdown(f"Total Penghasilan: **{formatted_total_revenue}**")
    
fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(
    daily_orders_df['order_count'], 
    bins=20, 
    kde=True,  # Tambahkan garis density
    color='#90CAF9',
    ax=ax
)
ax.set_title("Distribusi Total Pesanan (Histogram)", fontsize=16)
ax.set_xlabel("Total Pesanan", fontsize=15)
ax.set_ylabel("Frekuensi", fontsize=15)
st.pyplot(fig)


# Customer Spend Money
st.subheader("Jumlah Uang yang Dibelanjakan oleh Konsumen")
col1, col2 = st.columns(2)

with col1:
    total_spend = sum_spend_df["total_spend"].sum()
    formatted_total_spend = "{:.2f}".format(total_spend)  # Mengonversi angka dengan dua digit di belakang koma
    st.markdown(f"Total Pengeluaran: **{formatted_total_spend}**")

with col2:
    avg_spend = sum_spend_df["total_spend"].mean()
    formatted_avg_spend = "{:.2f}".format(avg_spend)
    st.markdown(f"Rata-rata Pengeluaran: **{formatted_avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=sum_spend_df,
    x="order_approved_at",
    y="total_spend",
    marker="o",
    linewidth=2,
    color="#90CAF9"
)

ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel("Tanggal Pemesanan", fontsize=15)
ax.set_ylabel("Total Pengeluaran", fontsize=15)
st.pyplot(fig)

# Order Items
st.subheader("Item yang Dipesan")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Item Dipesan: **{total_items}**")

with col2:
    avg_items = math.ceil(sum_order_items_df["product_count"].mean())
    st.markdown(f"Rata-rata Item Dipesan: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="viridis", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=80)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=90)
ax[0].tick_params(axis ='y', labelsize=55)
ax[0].tick_params(axis ='x', labelsize=50)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="viridis", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=80)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

st.pyplot(fig)

# Visualisasi Pesanan Harian
st.header("Grafik Pesanan Harian")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(
    x=daily_orders_df['order_approved_at'], 
    y=daily_orders_df['order_count'], 
    marker='o', 
    ax=ax, 
    color='#FF6F61'
)
ax.set_title("Pesanan Harian", fontsize=16)
ax.set_xlabel("Tanggal", fontsize=12)
ax.set_ylabel("Jumlah Pesanan", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

# Review Score
st.subheader("Nilai Review")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = math.ceil(review_score.mean())
    st.markdown(f"Rata-rata Nilai Review: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().idxmax()
    st.markdown(f"Nilai review paling banyak: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("viridis", len(review_score))

sns.barplot(x=review_score.index,
            y=review_score.values,
            order=review_score.index,
            palette=colors)

plt.title("Nilai review pelanggan untuk pelayanan", fontsize=15)
plt.xlabel("Nilai")
plt.ylabel("Jumlah")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Bagian Ringkasan
st.header("Ringkasan Penjualan")
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df['order_count'].sum()
    formatted_orders = "{:,}".format(total_orders)
    st.metric(label="Total Pesanan", value=formatted_orders)

with col2:
    total_revenue = daily_orders_df['revenue'].sum()
    formatted_revenue = "Rp {:,.2f}".format(total_revenue)
    st.metric(label="Total Pendapatan", value=formatted_revenue)