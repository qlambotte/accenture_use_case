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
    allergy = pd.read_csv('./data/allergy.csv')
    allergy_customer = pd.read_csv('./data/allergy_customer.csv')
    order = pd.read_csv('./data/order.csv')
    order_item = pd.read_csv('./data/order_item.csv')
    orderables = pd.read_csv('./data/orderables.csv')
    restaurant = pd.read_csv('./data/restaurants.csv')
    dish_per_month = pd.read_csv('./data/dish_per_month.csv')
    dish_per_rest = pd.read_csv('./data/dish_per_rest.csv')
    order['creation_date'] = order['creation_date'].apply(pd.to_datetime)
    restaurant = restaurant.replace('None', np.nan).dropna()
    restaurant['lat'] = restaurant['lat'].astype(float)
    restaurant['lon'] = restaurant['lon'].astype(float)
    customers_list = set(order["customer_id"].to_list())
    return allergy, allergy_customer, order, order_item, orderables, restaurant, dish_per_month, dish_per_rest, customers_list

allergy, allergy_customer, order, order_item, orderables, restaurant, dish_per_month, dish_per_rest, customers_list = load_dfs_in_cache()

modus = st.sidebar.selectbox('Select mode:', ('Global View', 'Restaurant View', 'Customer page'))

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
        start_date = order['creation_date'].min().date()
        end_date = order['creation_date'].max().date() - relativedelta(days=date_range)

        slider = st.sidebar.slider('Select start date:', min_value=start_date, value=start_date, max_value=end_date, format=format)
        # check in table
        st.sidebar.table(pd.DataFrame([[slider, slider + relativedelta(days=date_range)]],
                                      columns=['selected start',
                                               'end'],
                                      index=['date']))

    st.write(f'Showing: {feature} for {city}')
    max_rev = restaurant['revenue'].max()

    selected_layers = [pdk.Layer("ColumnLayer",
                       data=restaurant,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=['revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=restaurant,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=[f'{max_rev} - revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=restaurant,
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
                       data=restaurant,
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


customers = set(order["customer_id"].to_list())

def customer_page():
    # Allergies
    customer = st.sidebar.selectbox("Select a customer.", customers)
    st.header(
        f"Details on customer {customer}"
    )
    def buisiness_insights(customer_id, data):
        clv = round(data["total"].sum(),2)
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

def dishes_map():

    st.header('Information on Dishes')

    city = st.sidebar.selectbox("Select a city.", ['New York', 'San Francisco'])
    col_type = st.sidebar.selectbox("Select by type", ['amount sold', 'revenue'])
    if col_type == 'amount sold':
        col = 'amount'
    else:
        col = 'total'
    graph = DishGrapher()

    st.subheader(f'The most popular dishes by {col_type} in {city}')
    table_dish = graph.popular(city, col)
    list_of_dishes = list(table_dish.index)
    st.write(graph.popular(city, col))

    dish = st.sidebar.selectbox("Select by dish", list_of_dishes)
    abbrev_dish  = dish[:50]+'...' if len(dish)>50 else dish
    st.subheader(f'Facts about {abbrev_dish}')

    col1, col2 = st.columns(2)

    with col1:
        st.write(graph.price_distributer(dish))
    with col2:
        trender = DishTrendGrapher()
        st.write(trender.dish_trend(dish, col))

if modus == 'Global View':
    col1, col2, col3 = st.columns(3)
    rev = round(order["total"].sum())
    col1.metric(label="Gross revenue", value=f"{rev}$")
    col2.metric(label="Number of customer", value=len(customers_list))
    col3.metric(label="CLV", value=3)

    choice = st.selectbox("Select an option", ["View maps", "View insights on dishes"])
    if "maps" in choice:
        display_maps()
    else:
        dishes_map()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
