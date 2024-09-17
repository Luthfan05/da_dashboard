
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pydeck as pdk
from babel.numbers import format_currency
# Load df
df = pd.read_csv(r'C:\Users\Asus\Documents\dashboard dicoding.csv', delimiter=';')

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

# Heatmap
st.header('Geolocation Heatmap')

# Check if there is enough df to plot a heatmap
if 'geolocation_lat' in df.columns and 'geolocation_lng' in df.columns:
    # Remove rows with missing coordinates and invalid values
    geo_df = filtered_df[['geolocation_lat', 'geolocation_lng']].dropna()

    # Make sure there are no invalid lat/lng values
    geo_df = geo_df[(geo_df['geolocation_lat'].between(-90, 90)) & 
                        (geo_df['geolocation_lng'].between(-180, 180))]

    # Ensure there is df to plot
    if not geo_df.empty:
        # Create heatmap using pydeck
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=pdk.ViewState(
                latitude=geo_df['geolocation_lat'].mean(),
                longitude=geo_df['geolocation_lng'].mean(),
                zoom=6,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'HeatmapLayer',
                    df=geo_df,
                    get_position='[geolocation_lng, geolocation_lat]',
                    radius=200,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        ))
    else:
        st.write("No valid geolocation df to display.")
else:
    st.write("Geolocation df not available in the dfset.")
st.header('Best and Worst Performing Product by Number of Sales')

# Group by product_category_name and sum qty
product_sales = filtered_df.groupby('product_category_name')['qty'].sum().reset_index()

# Sort to get best and worst performing products
best_performing = product_sales.sort_values(by='qty', ascending=False).head(1)
worst_performing = product_sales.sort_values(by='qty', ascending=True).head(1)

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
