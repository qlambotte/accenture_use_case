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
    st.header(
        f"Details on customer {customer}"
    )
    def buisiness_insights(customer_id, data):
        clv = data["total"].sum()
        crp = data["total"].count()
        cab = round(clv/crp,2)
        return {
            "clv": clv,
            "crp": crp,
            "cab": cab
            }
    orders = order[order["customer_id"]==customer]
    bi = buisiness_insights(customer, orders)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Customer Lifetime Value", value=f"{bi['clv']}$")
    col2.metric(label="Customer repeat purchase", value=f"{bi['crp']} orders")
    col3.metric(label="Customer average order", value=f"{bi['cab']}$/o")

    st.subheader("Allergy information")
    allergies = allergy_customer[allergy_customer["customer_id"]==customer]["allergy_id"].to_list()
    if len(allergies) == 0:
        st.write("This customer has no known allergy.")
    elif len(allergies) == 1:
        al = allergy[allergy["data_id"].isin(allergies)]
        name, severity = al["name"].iloc[0], al["severity"].iloc[0]
        st.write(f"This customer is allergic to {name}, which has {severity} severity.")
    else:
        st.write(f"This customer has the following allergies:")
        aller = allergy[allergy["data_id"].isin(allergies)][["name", "severity"]].reset_index(drop=True)
        aller.index +=1
        st.table(aller)
    st.subheader("Spending details")
    restaurants = set(orders["restaurant_id"].to_list())
    num_orders = orders.shape[0]
    if num_orders == 1:
        orders_string = "one order"
        restaurant_string = "one restaurant"
    else:
        orders_string = f"{num_orders} orders"
        num_restaurants = len(restaurants)
        if num_restaurants > 1:
            restaurant_string = f"{num_restaurants} restaurants"
    st.write(f"Customer {customer} made {orders_string} in {restaurant_string}. You may find the details here.")
    restaurants_names = restaurant[restaurant["data_id"].isin(restaurants)]["name"].to_list()
    restaurants_names.append("All")
    rest = st.selectbox("Select a restaurant", restaurants_names)
    if rest == "All":
        tot = round(orders["total"].sum(),2)
        st.write(f"Overall, customer {customer} spent {tot}$.")
    else:
        rest_id = restaurants.intersection(set(restaurant[restaurant["name"]==rest]["data_id"].to_list()))
        orders = orders[orders["restaurant_id"]==rest_id.pop()]
        tot = round(orders["total"].sum(),2)
        no_orders = orders.shape[0]
        if no_orders == 1:
            orders_string = "one order"
        else:
            orders_string = f"{no_orders} orders"
        st.write(f"Customer {customer} spent {tot}$ in restaurant {rest}, with {orders_string}.")
    orders_id = orders["data_id"].to_list()
    order_to_detail = st.selectbox("Select an order", orders_id)
    order_details = order_item[order_item["order_id"]==order_to_detail]
    restaurant_id = order_details["restaurant_id"].iloc[0]
    restaurant_details = restaurant[restaurant["data_id"]==restaurant_id]
    restaurant_name = restaurant_details["name"].iloc[0]
    city = restaurant_details["city"].iloc[0]
    date = order_details["creation_date"].iloc[0]
    n = order_details.shape[0]
    if n == 1:
        no_items = "one item"
    else:
        no_items = f"{n} items"
    tot = round(order_details["total"].sum(),2)
    st.write(f"This order was made in {restaurant_name}, {city}, on {date}, for a total of {tot}$. It contains {no_items}.")
    df = order_details[["name", "price", "amount", "total"]]
    df = df.reset_index(drop=True)
    df.index +=1
    st.write(df)

if modus == 'Map':
    display_maps()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
