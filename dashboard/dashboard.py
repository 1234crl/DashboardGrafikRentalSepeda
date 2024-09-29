import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 

days_df = pd.read_csv("data/day.csv")
hours_df = pd.read_csv("data/hour.csv")

#Menerapkan filter tahun
days_df['dteday'] = pd.to_datetime(days_df['dteday'])
days_df['year'] = days_df['dteday'].dt.year

min_year = days_df["year"].min()
max_year = days_df["year"].max()


def create_daily_orders_df(df):
    daily_orders_df = df.groupby([df['dteday'].dt.date, 'weathersit', 'workingday', 'hum']).agg({
        "instant": "sum"
    }).reset_index()

    daily_orders_df.rename(columns={
        "instant": "order_count",
        "weathersit": "Weather"
    }, inplace=True)
    
    return daily_orders_df


with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://png.pngtree.com/png-vector/20220908/ourmid/pngtree-bicycle-logo-vector-road-illustration-speed-vector-png-image_39138348.png")
    
    # Mengambil start_date & end_date dari date_input
    selected_year = st.selectbox('Pilih Tahun', range(min_year, max_year + 1))

main_df = days_df[(days_df["year"] >= (selected_year)) & 
                (days_df["year"] <= (selected_year))]

daily_orders_df = create_daily_orders_df(main_df)
print(daily_orders_df)


st.header('Bike Rental Information Dashboard :sparkles:')

st.subheader('Yearly Order According to The Weather')

col1, col2 = st.columns(2)
 
with col1:
    total_workdays = daily_orders_df[daily_orders_df['workingday'] == 1].shape[0]
    st.metric("Total Working Days", value=total_workdays)
 
with col2:
    total_holidays = daily_orders_df[daily_orders_df['workingday'] == 0].shape[0]    
    st.metric("Total Holidays", value=total_holidays)
    

colors = ["#72BCD4", "#D3D3D3", "#72BCD4"]
byweather_df = daily_orders_df.groupby(by="Weather").order_count.nunique().reset_index()
byweather_df.rename(columns={
    "order_count": "customer_count"
}, inplace=True)

weather_label = {1 : "Clear", 2: "Mist + Cloudy", 3: "Light Rain/Snow"}
byweather_df['weather_label'] = byweather_df['Weather'].map(weather_label)

plt.figure(figsize=(10, 5))
sns.barplot(
    y="customer_count", 
    x="weather_label",
    data=byweather_df.sort_values(by="customer_count", ascending=False),
    palette = colors,
    hue="Weather",
    legend=False
)
plt.title("Number of Customer by Weather", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)
st.pyplot(plt)



#########################################################################
st.subheader('Comparison of Number of Casual and Registered Customers')

year_label = {0 : "2011", 1: "2012"}
hours_df['year_label'] = hours_df['yr'].map(year_label)

agg_casual_registered = hours_df.groupby('year_label').agg({
    "instant": "nunique",
    "casual": ["max","min","mean","std"],
    "registered": ["max","min","mean","std"]
}).reset_index()


agg_casual_registered.columns = ['year_label', 'instant_nunique', 'casual_max', 'casual_min', 'casual_mean', 'casual_std',
                      'registered_max', 'registered_min', 'registered_mean', 'registered_std']

agg_casual_registered_melted = agg_casual_registered.melt(id_vars='year_label', 
                                      value_vars=['casual_mean', 'registered_mean'],
                                      var_name='User Type', 
                                      value_name='Average Users')
plt.figure(figsize=(10, 5))
sns.barplot(x='year_label', 
            y='Average Users', 
            data=agg_casual_registered_melted,
            hue="User Type")

plt.title("Perbandingan Rata-rata Jumlah Pelanggan Casual dan Registered Per Tahun")
plt.xlabel("Tahun")
plt.ylabel("Rata-rata jumlah pelanggan kasual dan terdaftar")
st.pyplot(plt)




#######################################################
st.subheader('Humidity Clustering and The Impact to The Customer')
daily_orders_df['hum'] = daily_orders_df['hum']*100
daily_orders_df['hum'] = daily_orders_df['hum'].round(1)

bins = [0, 20, 60, 100]
hum_labels = ['Uncomfortably Dry', 'Comfort Range', 'Uncomfortably Wet']

daily_orders_df['humidity_bin'] = pd.cut(daily_orders_df['hum'], bins=bins, labels=hum_labels, include_lowest=True)
cluster_df = daily_orders_df.groupby(by='humidity_bin', observed=False).agg({
    "order_count": "nunique"    
})
print(cluster_df)

plt.figure(figsize=(10, 5))
sns.barplot(x='humidity_bin', 
            y='order_count', 
            data=cluster_df,
           hue = 'order_count')

plt.title("Number of Customer According to The Humidity")
plt.xlabel(None)
plt.ylabel(None)
plt.show()
st.pyplot(plt)
