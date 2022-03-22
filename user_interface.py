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
    allergy = pd.read_csv('./data/allergy.csv')
    allergy_customer = pd.read_csv('./data/allergy_customer.csv')
    order = pd.read_csv('./data/order.csv')
    order_item = pd.read_csv('./data/order_item.csv')
    orderables = pd.read_csv('./data/orderables.csv')
    restaurant = pd.read_csv('./data/restaurants.csv')
    return allergy, allergy_customer, order, order_item, orderables, restaurant

allergy, allergy_customer, order, order_item, orderables, restaurant = load_dfs_in_cache()

modus = st.sidebar.selectbox('Select mode:', ('Map', 'Restaurant View', 'Customer page'))

def test():
    print("blas")

def display_maps():
    pass
def restaurant_view():
    # dishes per restaurant
    st.write("Add Restaurant View content here...")


customers = set(order["customer_id"].to_list())

def customer_page():
    # Allergies
    customer = st.sidebar.selectbox("Select a customer.", customers)
    st.write(
        f"On this page, you will find informations about customer {customer}"
    )
    orders = order[order["customer_id"]==customer]
    allergies = allergy_customer[allergy_customer["customer_id"]==customer]["allergy_id"].to_list()
    if len(allergies) == 0:
        st.write("This customer is not allergic.")
    elif len(allergies) == 1:
        al = allergy[allergy["data_id"]==allergies[0]]
        name, severity = al["name"][allergies[0]], al["severity"][allergies[0]]
        st.write(f"This customer is allergic to {name}, which has {severity} severity.")
    else:
        st.write(f"This customer has the following allergies:")
        st.table(allergy[allergy["data_id"].isin(allergies)][["name", "severity"]].reset_index(drop=True))
    restaurants = set(orders["restaurant_id"].to_list())
    st.write(f"Customer {customer} made {orders.shape[0]} order(s) in {len(restaurants)} restaurant(s). You may find the details here.")
    restaurants_names = restaurant[restaurant["data_id"].isin(restaurants)]["name"].to_list()
    restaurants_names.append("All")
    rest = st.selectbox("Select a restaurant", restaurants_names)
    if rest == "All":
        tot = orders["total"].sum()
        st.write(f"Overall, customer {customer} spent {tot}$.")
        st.write(orders)
    else:
        rest_id = restaurants.intersection(set(restaurant[restaurant["name"]==rest]["data_id"].to_list()))
        orders = orders[orders["restaurant_id"]==rest_id.pop()]
        tot = orders["total"].sum()
        no_orders = orders.shape[0]
        st.write(f"Customer {customer} spent {tot}$ in restaurant {rest}, with {no_orders} order(s).")
        orders_id = orders["data_id"].to_list()
        order_to_detail = st.selectbox("Select an order", orders_id)
        order_details = order_item[order_item["order_id"]==order_to_detail]
        st.write(order_details)
if modus == 'Map':
    display_maps()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
