import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pydeck as pdk
from babel.numbers import format_currency
from folium.plugins import HeatMap
import folium
from streamlit_folium import st_folium

# Load df
df = pd.read_csv('dashboard dicoding.csv', delimiter=';')

# Convert order_purchase_timestamp to datetime
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Calculate revenue
df['revenue'] = df['qty'] * df['price'] + df['freight_value']

# Streamlit App
st.title('Simple Dashboard')

# Date Filter
st.header('Search by Date')
start_date = st.date_input('Start date', df['order_purchase_timestamp'].min().date())
end_date = st.date_input('End date', df['order_purchase_timestamp'].max().date())

# Filter df based on the selected date range
filtered_df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
                     (df['order_purchase_timestamp'].dt.date <= end_date)]

# Plot revenue over time
st.header('Revenue Over Time')

# Group by order_purchase_timestamp (monthly or daily depending on the df)
revenue_by_date = filtered_df.groupby(filtered_df['order_purchase_timestamp'].dt.to_period('M'))

# Plotting
fig, ax = plt.subplots()
revenue_by_date['revenue'].plot(ax=ax)
ax.set_title('Revenue by Month')
ax.set_xlabel('Month')
ax.set_ylabel('Revenue')

# Display plot
st.pyplot(fig)

# Drop rows with NaN values in geolocation_lat and geolocation_lng
df = df.dropna(subset=['geolocation_lat', 'geolocation_lng'])

def clean_geolocation(value):
    if isinstance(value, str):
        # Replace commas with dots
        value = value.replace(',', '.')
    return float(value)
  
# Pastikan tipe data geolocation_lat dan geolocation_lng menjadi float
df['geolocation_lat'] = df['geolocation_lat'].astype(float)
df['geolocation_lng'] = df['geolocation_lng'].astype(float)

# Ekstrak data latitude dan longitude ke dalam list of lists
heat_data = df[['geolocation_lat', 'geolocation_lng']].values.tolist()

# Membuat peta dasar
map = folium.Map(location=[df['geolocation_lat'].mean(), df['geolocation_lng'].mean()], zoom_start=10)

# Membuat heatmap
HeatMap(heat_data).add_to(map)

# Menampilkan peta di dalam Streamlit dashboard
st.title("Dashboard Heatmap")
st.write("Berikut adalah visualisasi heatmap dari data geolocation:")
st_folium(map, width=700, height=500)


# Group by product_category_name and sum qty
product_sales = filtered_df.groupby('product_category_name')['qty'].sum().reset_index()

# Sort to get best and worst performing products
best_performing = product_sales.sort_values(by='qty', ascending=False).head(5)
worst_performing = product_sales.sort_values(by='qty', ascending=True).head(5)

st.subheader('Best Performing Product')
st.write(best_performing)

st.subheader('Worst Performing Product')
st.write(worst_performing)

# Plot Best and Worst Performing Products
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

# Plot Best Performing Product
ax[0].bar(best_performing['product_category_name'], best_performing['qty'], color='green')
ax[0].set_title('Best Performing Product')
ax[0].set_xlabel('Product Category')
ax[0].set_ylabel('Quantity Sold')

# Plot Worst Performing Product
ax[1].bar(worst_performing['product_category_name'], worst_performing['qty'], color='red')
ax[1].set_title('Worst Performing Product')
ax[1].set_xlabel('Product Category')
ax[1].set_ylabel('Quantity Sold')

st.pyplot(fig)
