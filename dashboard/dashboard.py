import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')
import matplotlib.image as mpimg
import urllib

# func
class DataAnalyzer:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_values(ascending=False)
        most_common_score = review_scores.idxmax()

        return review_scores, most_common_score

    def create_bystate_df(self):
        bystate_df = self.df.groupby(by="customer_state").customer_id.nunique().reset_index()
        bystate_df.rename(columns={
            "customer_id": "customer_count"
        }, inplace=True)
        most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
        bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

        return bystate_df, most_common_state
    
    def create_rfm_df(self):
        rfm_df = self.df.groupby(by="customer_id", as_index=False).agg({
            "order_approved_at": "max", #mengambil tanggal order terakhir
            "order_id": "nunique",
            "payment_value": "sum"
        })
        rfm_df.columns = ["customer_id", "order_purchase_timestamp", "frequency", "monetary"]
        
        rfm_df["order_purchase_timestamp"] = rfm_df["order_purchase_timestamp"].dt.date
        recent_date = self.df["order_approved_at"].dt.date.max()
        rfm_df["recency"] = rfm_df["order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
        rfm_df.drop("order_purchase_timestamp", axis=1, inplace=True)
    
        return rfm_df
    
class MapPlotter:
    def __init__(self, data, plt, mpimg, urllib, st):
        self.data = data
        self.plt = plt
        self.mpimg = mpimg
        self.urllib = urllib
        self.st = st

    def plot(self):
        brazil = self.mpimg.imread(self.urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
        ax = self.data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", figsize=(10,10), alpha=0.3,s=0.3,c='maroon')
        self.plt.axis('off')
        self.plt.imshow(brazil, extent=[-73.98283055, -33.8,-33.75116944,5.4])
        self.st.pyplot()
        
        
####################################################################################################################################################################################################


# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_data = pd.read_csv("https://raw.githubusercontent.com/dhayyue/submission-analisis-data-dengan-python/main/dashboard/all_data.csv")
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

geolocation = pd.read_csv("https://raw.githubusercontent.com/dhayyue/submission-analisis-data-dengan-python/main/data/geolocation_dataset.csv")
data = geolocation

for col in datetime_cols:
    all_data[col] = pd.to_datetime(all_data[col])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

# Sidebar
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://raw.githubusercontent.com/dhayyue/submission-analisis-data-dengan-python/main/logo.jpeg"
                 , width=120)
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

#main
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
st.markdown('<h1 style="font-size: 48px;">Public Data Insights</h1>', unsafe_allow_html=True)
st.markdown('<h1 style="color:blue;">Data Exploration Dashboard</h1>', unsafe_allow_html=True)

st.markdown('<h2 style="color:#9D00FF;">Total Pemesanan</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df["order_count"].sum()
    formatted_total_order = "{:.2f}".format(total_order)
    st.markdown(f"Total Pemesanan: **{formatted_total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    formatted_total_revenue = "{:.2f}".format(total_revenue)
    st.markdown(f"Total Penghasilan: **{formatted_total_revenue}**")
    
# area plot
fig, ax = plt.subplots(figsize=(12, 6))

# Membuat area plot untuk menampilkan total pesanan per hari
ax.fill_between(
    daily_orders_df["order_approved_at"].dt.strftime('%Y-%m-%d'),
    daily_orders_df["order_count"],
    color="#90CAF9",
    alpha=0.5
)

# Atur parameter visualisasi
ax.tick_params(axis="x", rotation=90)  # putar label di sumbu x agar mudah dibaca
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel("Tanggal Pemesanan", fontsize=15)
ax.set_ylabel("Total Pemesanan", fontsize=15)
ax.set_title("Total Pesanan per Tanggal (Area Plot)", fontsize=16)
st.pyplot(fig)

# Pengeluaran Pelanggan
st.markdown('<h2 style="color:#9D00FF;">Pengeluaran pelanggan</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    total_spent = sum_spend_df["total_spend"].sum()
    formatted_total_spent = "{:,.2f}".format(total_spent)  # Format dengan koma dan dua desimal
    st.markdown(f"**Total Pengeluaran:** {formatted_total_spent}")
with col2:
    avg_spent = sum_spend_df["total_spend"].mean()
    formatted_avg_spent = "{:,.2f}".format(avg_spent)  # Format dengan koma dan dua desimal
    st.markdown(f"**Rata-rata Pengeluaran:** {formatted_avg_spent}")
fig, ax = plt.subplots(figsize=(10, 5))

sns.lineplot(
    data=sum_spend_df,
    x="order_approved_at",
    y="total_spend",
    marker="o",  
    linewidth=2,
    color="#f6d6c2"
)

ax.tick_params(axis="x", rotation=30)
ax.tick_params(axis="y", labelsize=12)
ax.set_xlabel("Tanggal Pemesanan", fontsize=12)
ax.set_ylabel("Total Pengeluaran", fontsize=12)
ax.set_title("Pengeluaran Pelanggan per Tanggal", fontsize=14)
st.pyplot(fig)

# Order Information
st.markdown('<h2 style="color:#9D00FF;">Detail Produk Terjual</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    total_sold_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"**Total Produk Terjual: {total_sold_items}**", unsafe_allow_html=True)

with col2:
    avg_sold_items = round(sum_order_items_df["product_count"].mean(), 2)
    st.markdown(f"**Rata-rata Produk Terjual: {avg_sold_items}**", unsafe_allow_html=True)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18, 8))

# Produk paling laris
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette="coolwarm", ax=axes[0])
axes[0].set_ylabel("")
axes[0].set_xlabel("Total Penjualan", fontsize=12)
axes[0].set_title("Produk Paling Banyak Terjual", loc="center", fontsize=14)
axes[0].tick_params(axis='y', labelsize=10)
axes[0].tick_params(axis='x', labelsize=10)

# Produk yang paling sedikit terjual
sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette="coolwarm", ax=axes[1])
axes[1].set_ylabel("")
axes[1].set_xlabel("Total Penjualan", fontsize=12)
axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].set_title("Produk Paling Sedikit Terjual", loc="center", fontsize=14)
axes[1].tick_params(axis='y', labelsize=10)
axes[1].tick_params(axis='x', labelsize=10)
st.pyplot(fig)


for i, v in enumerate(review_score.values):
    ax.text(i, v + 3, f'{v}', ha='center', va='bottom', fontsize=10, color='blue')
st.pyplot(fig)
st.markdown('<h2 style="color:#9D00FF;">Pelanggan Terbaik Berdasarkan RFM (Recency, Frequency, Monetary)</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 2)
    st.metric("Rata-rata Recency", value=avg_recency)

    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale='en_US')
    st.metric("Rata-rata Monetary", value=avg_monetary)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 1)
    st.metric("Rata-rata Frequency", value=avg_frequency)

# Membuat visualisasi bar chart dengan 2 baris untuk setiap metrik
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(30, 20))

# Recency
sns.barplot(x="customer_id", y="recency", data=rfm_df.sort_values(by="recency").head(5), palette="coolwarm", ax=axes[0, 0])
axes[0, 0].set_title("Top 5 Customers by Recency", fontsize=30)
axes[0, 0].set_xlabel("Customer ID", fontsize=20)
axes[0, 0].set_ylabel("Recency (days)", fontsize=20)
axes[0, 0].tick_params(labelsize=15)

# Frequency
sns.barplot(x="customer_id", y="frequency", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette="YlGn", ax=axes[0, 1])
axes[0, 1].set_title("Top 5 Customers by Frequency", fontsize=30)
axes[0, 1].set_xlabel("Customer ID", fontsize=20)
axes[0, 1].set_ylabel("Frequency", fontsize=20)
axes[0, 1].tick_params(labelsize=15)

# Monetary
sns.barplot(x="customer_id", y="monetary", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette="BuGn_r", ax=axes[1, 0])
axes[1, 0].set_title("Top 5 Customers by Monetary", fontsize=30)
axes[1, 0].set_xlabel("Customer ID", fontsize=20)
axes[1, 0].set_ylabel("Monetary (USD)", fontsize=20)
axes[1, 0].tick_params(labelsize=15)

# Kombinasi Recency, Frequency, dan Monetary dengan scatter plot
sns.scatterplot(x="recency", y="frequency", size="monetary", data=rfm_df, sizes=(20, 200), legend=False, ax=axes[1, 1], color="orange")
axes[1, 1].set_title("RFM Scatter Plot", fontsize=30)
axes[1, 1].set_xlabel("Recency (days)", fontsize=20)
axes[1, 1].set_ylabel("Frequency", fontsize=20)
axes[1, 1].tick_params(labelsize=15)

st.pyplot(fig)

# demografi pelanggan 
st.markdown('<h2 style="color:#9D00FF;">Distribusi Pelanggan Berdasarkan Demografi</h2>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["State", "Geolocation", "Age Group"])

with tab1:
    st.markdown(f"<h3 style='color:#A020F0;'>Top State with Most Customers: {most_common_state}</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(15, 7))
    sns.barplot(x=state.customer_state.value_counts().index, y=state.customer_count.values, palette="mako", ax=ax)
    ax.set_title("Jumlah Pelanggan Berdasarkan State", fontsize=20)
    ax.set_xlabel("State", fontsize=15)
    ax.set_ylabel("Jumlah Pelanggan", fontsize=15)
    st.pyplot(fig)

with tab2:
    map_plot.plot()
    st.expander("Detail Geolocation Analysis")
    st.markdown("Hasil dari visualisasi menunjukkan bahwa pelanggan yang tersebar lebih banyak berada di wilayah tenggaradan kota-kota metropolitan. Wilayah ini memiliki pengaruh besar dalam pesanan e-commerce.")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    st.pyplot(fig)
with tab3:
    # Hypothetical Age Group Distribution
    age_groups = ["18-25", "26-35", "36-45", "46-55", "55+"]
    customers_per_age_group = [500, 1200, 900, 600, 300]

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(x=age_groups, y=customers_per_age_group, palette="rocket", ax=ax)
    ax.set_title("Distribusi Pelanggan Berdasarkan Kelompok Umur", fontsize=20)
    ax.set_xlabel("Kelompok Umur", fontsize=15)
    ax.set_ylabel("Jumlah Pelanggan", fontsize=15)
    st.pyplot(fig)

