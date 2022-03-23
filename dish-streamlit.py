import this
from xml.dom import UserDataHandler
import numpy as np
import streamlit as st
import pydeck as pdk
import pandas as pd
# relativedelta to add days or years
from dateutil.relativedelta import relativedelta
import datetime as dt

from dishgraph import DishGrapher, DishTrendGrapher




@st.cache
def load_dfs_in_cache():
    # read vals from csv
    order_item = pd.read_csv('./data/order_item.csv')
    dish_per_month = pd.read_csv('./data/dish_per_month.csv')
    dish_per_rest = pd.read_csv('./data/dish_per_rest.csv')
    return  order_item, dish_per_month, dish_per_rest

order_item, dish_per_month, dish_per_rest  = load_dfs_in_cache()

modus = st.sidebar.selectbox('Select mode:', ('Map', 'Restaurant View', 'Customer page', 'Dish page'))

def display_maps():
    pass

def restaurant_view():
    pass

def customer_page():
    pass

def dishes_map():

    st.header('Information on Dishes')
    
    city = st.sidebar.selectbox("Select a city.", ['New York', 'San Francisco'])
    col_type = st.sidebar.selectbox("Select by type", ['amount sold', 'revenue'])
    st.subheader(f'The most popular dishes by {col_type} in {city}')
    if col_type == 'amount sold':
        col = 'amount'
    else:
        col = 'total'
    graph = DishGrapher()
    table_dish = graph.popular(city, col)
    list_of_dishes = list(table_dish.index)
    st.write(graph.popular(city, col))

    
    dish = st.sidebar.selectbox("Select by dish", list_of_dishes)
    abbrev_dish  = dish[:50]+'...' if len(dish)>50 else dish

    st.subheader(f'Facts about {abbrev_dish}')
    st.write(graph.price_distributer(dish))

    trender = DishTrendGrapher()
    st.write(trender.dish_trend(dish, col))




if modus == 'Map':
    display_maps()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
elif modus == 'Dish page':
    dishes_map()