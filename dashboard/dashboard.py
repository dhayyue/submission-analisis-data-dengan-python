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

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_data = pd.read_csv("https://media.githubusercontent.com/media/desikanra/submission-analisis-data-dengan-python/main/dashboard/all_data.csv")
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

geolocation = pd.read_csv("https://media.githubusercontent.com/media/desikanra/submission-analisis-data-dengan-python/main/data/geolocation_dataset.csv")
data = geolocation

for col in datetime_cols:
    all_data[col] = pd.to_datetime(all_data[col])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

# Sidebar
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://raw.githubusercontent.com/desikanra/submission-analisis-data-dengan-python/main/dashboard/logo.png"
                 , width=100)
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

# Add text or descriptions
st.write("**Dashboard untuk analisis Data Publik E-Commerce.**")

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
sns.lineplot(
    x=daily_orders_df["order_approved_at"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel("Tanggal Pemesanan", fontsize=15)
ax.set_ylabel("Total Pemesanan", fontsize=15)
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

# Menambahkan label di atas setiap bar
for i, v in enumerate(review_score.values):
    ax.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=12, color='black')

st.pyplot(fig)

st.subheader("Pelanggan Terbaik Berdasarkan Analisis RFM")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rata-rata Recency (hari)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Rata-rata Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Rata-Rata Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(rotation=45, axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(rotation=45, axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(rotation=45, axis='x', labelsize=35)
 
st.pyplot(fig)

# Customer Demographic
st.subheader("Demografi Pelanggan")
tab1, tab2 = st.tabs(["State", "Geolocation"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"State Paling Umum: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                palette="viridis"
                    )

    plt.title("Jumlah Pelanggan berdasarkan State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Jumlah Pelanggan")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

with tab2:
    map_plot.plot()

    with st.expander("Penjelasan Lebih Lanjut"):
        st.write('Sesuai dengan grafik yang sudah dibuat, ada lebih banyak pelanggan di bagian tenggara dan selatan. Informasi lainnya, ada lebih banyak pelanggan di kota-kota yang merupakan ibu kota (São Paulo, Rio de Janeiro, Porto Alegre, dan lainnya).')

st.caption('Copyright (C) Desika Nurul Afifah 2024')
