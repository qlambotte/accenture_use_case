import this
from xml.dom import UserDataHandler
import numpy as np
import streamlit as st
import pydeck as pdk
import pandas as pd
# relativedelta to add days or years
from dateutil.relativedelta import relativedelta
import datetime as dt


@st.cache
def load_dfs_in_cache():
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

    # modified code from Yass
    df_order[['creation_date_only', 'creation_time']] = df_order['creation_date'].str.split(' ', 1, expand=True)
    pd.to_datetime(df_order['creation_date_only'], format="%x")
    df_order.groupby(['customer_id'])['restaurant_id'].count().sort_values(ascending=True).to_frame()['restaurant_id'].mean()
    order_item_df_value = df_order_item.join(df_orderables[['price', 'name']], on='orderable_id')
    order_item_df_value["order_value"] = order_item_df_value['price'].mul(order_item_df_value['amount'])
    orders_value = order_item_df_value.groupby(['order_id'])['order_value'].sum().sort_values(ascending=False).to_frame()
    order_value_df = df_order.join(orders_value['order_value'], on='data_id')
    order_value_df['month_year'] = pd.to_datetime(order_value_df['creation_date_only']).dt.strftime('%y/%m')
    order_value_df['month'] = pd.to_datetime(order_value_df['creation_date_only']).dt.strftime('%m')
    resto_value_df = order_value_df.groupby(['restaurant_id'])['order_value'].sum().sort_values(ascending=False)
    resto_value_df = resto_value_df.to_frame()
    restaurant_revenue = df_restaurant.join(resto_value_df['order_value'], on='data_id',)
    restaurant_revenue = restaurant_revenue.rename(columns={"order_value": "revenue"})

    df_order['creation_date'] = df_order['creation_date'].apply(pd.to_datetime)
    restaurant_revenue = restaurant_revenue.replace('None', np.nan).dropna()
    restaurant_revenue['lat'] = restaurant_revenue['lat'].astype(float)
    restaurant_revenue['lon'] = restaurant_revenue['lon'].astype(float)

    return df_allergy, df_allergy_customer, df_order, df_order_item, df_orderables, df_restaurant, restaurant_revenue

df_allergy, df_allergy_customer, df_order, df_order_item, df_orderables, df_restaurant, restaurant_revenue = load_dfs_in_cache()

modus = st.sidebar.selectbox('Select mode:', ('Map', 'Restaurant View', 'Customer page'))

def test():
    print("blas")

def display_maps():
    city = st.sidebar.radio("Please select a City:",
                            ("USA", 'New York', 'San Francisco', 'Both'))

    feature = st.sidebar.radio('What feature do you want to display?',
                               ('Restaurant revenue (max)', 'Restaurant revenue (min)'))

    date_range_sel = st.sidebar.selectbox('Select a date range:',
                                          ('All', 'Year', 'Month', 'Week'))
    if date_range_sel == 'Year':
        date_range = 365
    elif date_range_sel == 'Month':
        date_range = 30
    elif date_range_sel == 'Week':
        date_range = 7

    if date_range_sel != 'All':
        # Range selector
        format = 'MMM DD, YYYY'  # format output
        start_date = df_order['creation_date'].min().date()
        end_date = df_order['creation_date'].max().date() - relativedelta(days=date_range)

        slider = st.sidebar.slider('Select start date:', min_value=start_date, value=start_date, max_value=end_date, format=format)
        # check in table
        st.sidebar.table(pd.DataFrame([[slider, slider + relativedelta(days=date_range)]],
                                      columns=['selected start',
                                               'end'],
                                      index=['date']))

    st.write(f'Showing: {feature} for {city}')
    max_rev = restaurant_revenue['revenue'].max()

    selected_layers = [pdk.Layer("ColumnLayer",
                       data=restaurant_revenue,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=['revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=restaurant_revenue,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=[f'{max_rev} - revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=restaurant_revenue,
                       get_position=['lon', 'lat'],
                       radius=10000,
                       elevation_scale=20,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=['revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000],
                       extruded=True,),
                       pdk.Layer("ColumnLayer",
                       data=restaurant_revenue,
                       get_position=['lon', 'lat'],
                       radius=10000,
                       elevation_scale=20,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=[f'{max_rev} - revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000],
                       extruded=True,)]

    tooltip = {
        "html": "<b>{name}</b><br>Has a revenue of: <b>{revenue}</b> $",
        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
    }

    if city == 'New York':
        if feature == 'Restaurant revenue (max)':
            thislayer = selected_layers[0]
        else:
            thislayer = selected_layers[1]
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                 initial_view_state={"latitude": 40.709381,
                                                     "longitude": -74.008828,
                                                     "zoom": 10,
                                                     "pitch": 60},
                                 tooltip=tooltip,
                                 layers=thislayer
                                 ))
    elif city == 'San Francisco':
        if feature == 'Restaurant revenue (max)':
            thislayer = selected_layers[0]
        else:
            thislayer = selected_layers[1]
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                 initial_view_state={"latitude": 37.754772,
                                                     "longitude": -122.441767,
                                                     "zoom": 11,
                                                     "pitch": 60},
                                 tooltip=tooltip,
                                 layers=thislayer
                                 ))
    elif city == 'USA':
        if feature == 'Restaurant revenue (max)':
            thislayer = selected_layers[2]
        else:
            thislayer = selected_layers[3]
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                initial_view_state={"latitude": 39.462830,
                                                    "longitude": -99.509115,
                                                    "zoom": 3,
                                                    "pitch": 60},
                                tooltip=tooltip,
                                layers=thislayer))
    else:
        col1, col2 = st.columns(2)
        with col1:
            if feature == 'Restaurant revenue (max)':
                thislayer = selected_layers[0]
            else:
                thislayer = selected_layers[1]
            st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                     initial_view_state={"latitude": 40.709381,
                                                         "longitude": -74.008828,
                                                         "zoom": 10,
                                                         "pitch": 60},
                                     tooltip=tooltip,
                                     layers=thislayer
                                     ))
        with col2:
            if feature == 'Restaurant revenue (max)':
                thislayer = selected_layers[0]
            else:
                thislayer = selected_layers[1]
            st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
                                     initial_view_state={"latitude": 37.754772,
                                                         "longitude": -122.441767,
                                                         "zoom": 10,
                                                         "pitch": 60},
                                     tooltip=tooltip,
                                     layers=thislayer
                                     ))


def restaurant_view():
    # dishes per restaurant
    st.write("Add Restaurant View content here...")

def customer_page():
    # Allergies
    st.write("Add Customer page content here...")

if modus == 'Map':
    display_maps()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
