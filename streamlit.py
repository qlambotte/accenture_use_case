import numpy as np
import streamlit as st
import pydeck as pdk
import pandas as pd
import os

# read vals from csv
df_allergy = pd.read_csv('ODL_ALLERGY.csv')
df_allergy_customer = pd.read_csv('ODL_ALLERGY_CUSTOMER.csv')
df_order = pd.read_csv('ODL_ORDER.csv')
df_order_item = pd.read_csv('ODL_ORDER_ITEM.csv')
df_orderables = pd.read_csv('ODL_ORDERABLES.csv')
df_restaurant = pd.read_csv('ODL_RESTAURANT_latlon.csv')

# remove unwanted cols
df_allergy = df_allergy.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts'])
df_allergy_customer = df_allergy_customer.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts'])
df_order = df_order.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts'])
df_order_item = df_order_item.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts', 'Column_useless'])
df_orderables = df_orderables.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts'])
# df_restaurant = df_restaurant.drop(columns=['id', '_rid', '_self', '_etag', '_attachments', '_ts'])
# df_restaurant = df_restaurant.drop(df_restaurant.columns[0], axis=1)
df_restaurant = df_restaurant.replace('None', np.nan).dropna()
df_restaurant['lat'] = df_restaurant['lat'].astype(float)
df_restaurant['lon'] = df_restaurant['lon'].astype(float)


selected_layers = [pdk.Layer("ColumnLayer",
                   data=df_restaurant,
                   get_position=['lon', 'lat'],
                   radius=50,
                   elevation_scale=10,
                   auto_highlight=True,
                   pickable=True,
                   get_elevation='data_id',
                   get_fill_color=["data_id / 10", "data_id", "data_id * 10", 140],
                   elevation_range=[0, 1000]),
                   pdk.Layer("ColumnLayer",
                   data=df_restaurant,
                   get_position=['lon', 'lat'],
                   radius=10000,
                   elevation_scale=2000,
                   auto_highlight=True,
                   pickable=True,
                   get_elevation='data_id',
                   get_fill_color=["data_id / 10", "data_id", "data_id * 10", 140],
                   elevation_range=[0, 1000],
                   extruded=True,)]

tooltip = {
    "html": "<b>{data_id}</b> is the value of the Restaurant: <b>{name}</b>",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

city = st.radio("Please select a City:",
                ('New York', 'San Francisco', 'Both', "USA"))

if city == 'New York':
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                             initial_view_state={"latitude": 40.709381,
                                                 "longitude": -74.008828,
                                                 "zoom": 11,
                                                 "pitch": 60},
                             tooltip=tooltip,
                             layers=selected_layers[0]
                             ))
elif city == 'San Francisco':
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                             initial_view_state={"latitude": 37.76,
                                                 "longitude": -122.4,
                                                 "zoom": 11,
                                                 "pitch": 60},
                             tooltip=tooltip,
                             layers=selected_layers[0]
                             ))
elif city == 'USA':
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                             initial_view_state={"latitude": 39.462830,
                                                 "longitude": -99.509115,
                                                 "zoom": 3,
                                                 "pitch": 60},
                             tooltip=tooltip,
                             layers=selected_layers[1]
                             ))
else:
    col1, col2 = st.columns(2)
    with col1:
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                 initial_view_state={"latitude": 40.709381,
                                                     "longitude": -74.008828,
                                                     "zoom": 10,
                                                     "pitch": 60},
                                 tooltip=tooltip,
                                 layers=selected_layers[0]
                                 ))
    with col2:
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                 initial_view_state={"latitude": 37.76,
                                                     "longitude": -122.4,
                                                     "zoom": 10,
                                                     "pitch": 60},
                                 tooltip=tooltip,
                                 layers=selected_layers[0]
                                 ))
