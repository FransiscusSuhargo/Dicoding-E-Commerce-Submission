import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def sales_over_time(df):
        customer_has_delivered_orders = df[df['order_status'] == 'delivered']
        #Mengubah data menjadi datetime
        customer_has_delivered_orders['order_delivered_carrier_date'] = pd.to_datetime(customer_has_delivered_orders['order_delivered_carrier_date'])
        customer_has_delivered_orders['order_delivered_customer_date'] = pd.to_datetime(customer_has_delivered_orders['order_delivered_customer_date'])
        #Menghitung waktu pengantaran dan menambahkannya pada dataset
        monthly_orders = customer_has_delivered_orders.resample(rule='M', on='order_delivered_customer_date').agg({
        "order_id": "count"
        })
        return(monthly_orders)

def delivery_time(df):
        customer_has_delivered_orders = df[df['order_status'] == 'delivered']
        #Mengubah data menjadi datetime
        customer_has_delivered_orders['order_delivered_carrier_date'] = pd.to_datetime(customer_has_delivered_orders['order_delivered_carrier_date'])
        customer_has_delivered_orders['order_delivered_customer_date'] = pd.to_datetime(customer_has_delivered_orders['order_delivered_customer_date'])
        #Menghitung waktu pengantaran dan menambahkannya pada dataset
        delivery_time = customer_has_delivered_orders['order_delivered_customer_date'] - customer_has_delivered_orders['order_delivered_carrier_date']
        customer_has_delivered_orders['delivery_time'] = delivery_time
        #Menghapus order dengan delivery time yang negatif
        customer_has_delivered_orders = customer_has_delivered_orders[customer_has_delivered_orders['delivery_time'] > pd.Timedelta(0)]
        average_delivery_time = customer_has_delivered_orders.groupby('customer_city').agg({
        'delivery_time' : 'mean'
        }).sort_values(by='delivery_time', ascending=True).reset_index()
        return(average_delivery_time)
    
def payment_counts(df):
    payment_counts = df.groupby(by='payment_type').count()['order_id'].sort_values(ascending=False)
    payment_counts = payment_counts[payment_counts.index != "not_defined"]
    return payment_counts

def customer_counts(df):
    customer_count = df.groupby(by="customer_city").count()['customer_unique_id'].sort_values(ascending=False).head(20)
    return customer_count

def top_3_categories_city(df):
    category_highest = df.groupby(['customer_city', 'product_category_name_english']).agg({
        'product_id': 'count'  
    }).rename(columns={'product_id': 'count'}).reset_index()
    top_cities = category_highest.groupby('customer_city')['count'].sum().nlargest(10).index
    top_categories_per_city = category_highest[category_highest['customer_city'].isin(top_cities)]
    top_3_categories_per_city = top_categories_per_city.groupby('customer_city').apply(lambda x: x.nlargest(3, 'count')).reset_index(drop=True)
    return(top_3_categories_per_city)
def categories_product_sales(df):
    # Mencari tahu kategori produk apa yang paling banyak dijual
    category_highest = df.groupby('product_category_name_english').agg({
    'product_id': 'count'  
    }).rename(columns={'product_id': 'count'}).sort_values(by='count', ascending=False)

    # Mencari tahu kategori produk apa yang paling sedikit dijual
    category_lowest = df.groupby('product_category_name_english').agg({
    'product_id': 'count'  
    }).rename(columns={'product_id': 'count'}).sort_values(by='count', ascending=True)
    return category_highest, category_lowest

# Load cleaned data
all_df = pd.read_csv("dashboard/all_data.csv")

datetime_columns = ["order_delivered_carrier_date", "order_delivered_customer_date"]
all_df.sort_values(by="order_delivered_customer_date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_delivered_customer_date"].min()
max_date = all_df["order_delivered_customer_date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://upload.wikimedia.org/wikipedia/id/7/72/Universitas-surabaya.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_delivered_customer_date"] >= str(start_date)) & 
                (all_df["order_delivered_customer_date"] <= str(end_date))]


# # Menyiapkan berbagai dataframe
sales_over_time_data = sales_over_time(main_df)
average_delivery_time = delivery_time(main_df)
payment_counts_data = payment_counts(main_df)
customer_counts_data = customer_counts(main_df)
explore_categories_city_data = top_3_categories_city(main_df)
category_highest, category_lowest = categories_product_sales(main_df) 

st.title("Sales Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    sales_over_time_data.index,
    sales_over_time_data["order_id"],
    marker='o', 
    linewidth=2,
    color="#72BCD4"
)
ax.set_title("Total delivered over time", fontsize=20)
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=10)

# Display the plot in Streamlit
st.pyplot(fig)

st.title("Category per Cities")
category_highest_reset = category_highest.reset_index().sort_values(by="count",ascending=False)
category_lowest_reset = category_lowest.reset_index().sort_values(by="count",ascending=True)

colors_highest = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

#Bar plot untuk 5 kategori dengan penjualan terbanyak
sns.barplot(x=category_highest_reset.head(5)['count'], 
            y=category_highest_reset.head(5)['product_category_name_english'], 
            palette=colors_highest, ax=ax[0])
ax[0].set_title("Top 5 Most Sold Product Categories", fontsize=15)
ax[0].set_xlabel("Count")
ax[0].set_ylabel("Product Category")

colors_lowest = ["#FF6F61", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
# Bar plot untuk 5 kategori dengan penjualan tersedikit
sns.barplot(x=category_lowest_reset.head(5)['count'], 
            y=category_lowest_reset.head(5)['product_category_name_english'], 
            palette=colors_lowest, ax=ax[1])
ax[1].set_title("Top 5 Least Sold Product Categories", fontsize=15)
ax[1].set_xlabel("Count")
ax[1].set_ylabel(None)
ax[1].yaxis.tick_right()

plt.tight_layout()
st.pyplot(fig)

st.title("Top 3 Categories for Each City")
top_cities = explore_categories_city_data.groupby('customer_city')['count'].sum().nlargest(10).index

top_categories_per_city = explore_categories_city_data[explore_categories_city_data['customer_city'].isin(top_cities)]
top_3_categories_per_city = top_categories_per_city.groupby('customer_city').apply(lambda x: x.nlargest(3, 'count')).reset_index(drop=True)

plt.figure(figsize=(12, 6))

sns.barplot(x='customer_city', y='count', hue='product_category_name_english', data=top_3_categories_per_city)

plt.title('Top 3 Product Categories per City')
plt.xlabel('Customer City')
plt.ylabel('Count of Products')
plt.xticks(rotation=45)  

plt.tight_layout()
st.pyplot(plt)

st.title("Distribution Of Payment Types")
plt.figure(figsize=(8, 8))
plt.bar(x=payment_counts_data.index, height=payment_counts_data, color="#72BCD4")
plt.xticks(rotation=45)
plt.title('Distribution of Payment Types', fontsize=16)
st.pyplot(plt)

st.title("Average Delivery Time per Cities")
average_delivery_time['delivery_time'] = average_delivery_time['delivery_time'].dt.total_seconds() / 3600  

colors_fastest = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors_slowest = ["#FF6F61", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

sns.barplot(x=average_delivery_time['delivery_time'].head(5), 
            y=average_delivery_time['customer_city'].head(5), 
            palette=colors_fastest, ax=ax[0])
ax[0].set_title("Top 5 Fastest Cities by Delivery Time", fontsize=15)
ax[0].set_xlabel("Average Delivery Time (Hours)")
ax[0].set_ylabel("State")

average_delivery_time = average_delivery_time.sort_values(by="delivery_time", ascending=False )
sns.barplot(x=average_delivery_time['delivery_time'].head(5), 
            y=average_delivery_time['customer_city'].head(5), 
            palette=colors_slowest, ax=ax[1])
ax[1].set_title("Top 5 Slowest Cities by Delivery Time", fontsize=15)
ax[1].set_xlabel("Average Delivery Time (Hours)")
ax[1].set_ylabel(None)
ax[1].yaxis.tick_right()

plt.tight_layout()
st.pyplot(fig)


