from xml.dom import UserDataHandler
import numpy as np
import streamlit as st
import pydeck as pdk
import pandas as pd
# relativedelta to add days or years
from dateutil.relativedelta import relativedelta
import datetime as dt
import dishgraph


@st.cache
def load_dfs_in_cache():
    """This function loads all used dataframes and variables
    in cache for optimizing performance."""
    df_allergy = pd.read_csv('./data/allergy.csv')
    df_allergy_customer = pd.read_csv('./data/allergy_customer.csv')
    df_order = pd.read_csv('./data/order.csv')
    df_order_item = pd.read_csv('./data/order_item.csv')
    df_orderables = pd.read_csv('./data/orderables.csv')
    df_restaurant = pd.read_csv('./data/restaurants.csv')

    df_order['creation_date'] = df_order['creation_date'].apply(pd.to_datetime)
    df_restaurant = df_restaurant.replace('None', np.nan).dropna()
    df_restaurant['lat'] = df_restaurant['lat'].astype(float)
    df_restaurant['lon'] = df_restaurant['lon'].astype(float)
    customers_list = set(df_order["customer_id"].to_list())

    return df_allergy, df_allergy_customer, df_order, df_order_item, df_orderables, df_restaurant, customers_list

df_allergy, df_allergy_customer, df_order, df_order_item, df_orderables, df_restaurant, customers_list = load_dfs_in_cache()

modus = st.sidebar.selectbox('Select mode:', ('Map', 'Restaurant View', 'Customer page'))

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
    max_rev = df_restaurant['revenue'].max()

    selected_layers = [pdk.Layer("ColumnLayer",
                       data=df_restaurant,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=['revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=df_restaurant,
                       get_position=['lon', 'lat'],
                       radius=80,
                       elevation_scale=0.1,
                       auto_highlight=True,
                       pickable=True,
                       get_elevation=[f'{max_rev} - revenue'],
                       get_fill_color=[f"255*(1 - revenue / {max_rev}), 255*(revenue / {max_rev}), 0", 140],
                       elevation_range=[0, 1000]),
                       pdk.Layer("ColumnLayer",
                       data=df_restaurant,
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
                       data=df_restaurant,
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
    resto_filter = st.sidebar.text_input("Restarant filter (optional):")
    restolist = []
    if resto_filter != "":
        restolist = df_restaurant.loc[df_restaurant['name'].str.contains(resto_filter, case=False), 'name'].tolist()
    else:
        restolist = df_restaurant['name'].tolist()
    restolist.sort()
    resto_sel = st.sidebar.selectbox('Select a restaurant:', restolist)
    resto_id_lst = df_restaurant.loc[df_restaurant['name'] == resto_sel, 'data_id'].tolist()
    if len(resto_id_lst) > 1:
        resto_addr = df_restaurant.loc[df_restaurant['name'] == resto_sel, 'street'].tolist()
        resto_addr_sel = st.sidebar.radio('Multiple found with this name, select address:', resto_addr)
        resto_id = df_restaurant.loc[(df_restaurant['name'] == resto_sel) & (df_restaurant['street'] == resto_addr_sel), 'data_id'].tolist()[0]
    elif len(resto_id_lst) == 1:
        resto_id = resto_id_lst[0]
    st.markdown(f"## {resto_sel}:")
    st.markdown(f"**Adress**: {df_restaurant.loc[df_restaurant['data_id'] == resto_id, 'street'].tolist()[0]}, "
    f"{df_restaurant.loc[df_restaurant['data_id'] == resto_id, 'city'].tolist()[0]}  \n"
    f"**data_id**: {resto_id}")
    st.markdown("***")

    def revenue_one_month(x, y):
        revenue_by_month = df_order.loc[df_order['restaurant_id'] == x].groupby(['month_year'])['total'].sum().to_frame().sort_values('month_year')
        revenue_one_month = revenue_by_month.loc[y, 'total']
        return revenue_one_month

    months_set = set(df_order.loc[df_order['restaurant_id'] == resto_id, 'month_year'].tolist())
    sorted_months_set = sorted(months_set)
    st.markdown("### Select a month:")
    month_year = st.select_slider(" ", sorted_months_set)
    revenue_month = revenue_one_month(resto_id, month_year)
    st.markdown(f"### Revenue on {month_year} was {str(round(revenue_month,2))}$")
    st.markdown("***")
    def restaurant_COG(x):  # cost of goods
        cost_of_goods = df_restaurant.loc[df_restaurant['data_id'] == x, 'cost_of_goods']
        return cost_of_goods.iloc[0]

    def restaurant_COL(x):  # cost of labor
        cost_of_labor = df_restaurant.loc[df_restaurant['data_id'] == x, 'cost_of_labor_month']
        return cost_of_labor.iloc[0]

    def restaurant_FC(x):  # fixed costs
        fixed_cost = df_restaurant.loc[df_restaurant['data_id'] == x, 'fixed_costs_month']
        return fixed_cost.iloc[0]
    
    col1, col2, col3 = st.columns(3)

    with col1:
        cog = restaurant_COG(resto_id)
        st.markdown("Monthly cost of goods:")
        st.markdown(f"### {round(cog, 2)}$")
    
    with col2:
        col = restaurant_COL(resto_id)
        st.markdown("Monthly cost of labor:")
        st.markdown(f"### {round(col, 2)}$")

    with col3:
        fc = restaurant_FC(resto_id)
        st.markdown("Monthly Fixed cost:")
        st.markdown(f"### {round(fc, 2)}$")

    st.markdown("***")
    revenue_by_month = df_order.loc[df_order['restaurant_id'] == resto_id].groupby(['month_year'])['total'].sum().to_frame().sort_values('month_year')
    st.markdown("### Revenue per month in US$")
    st.line_chart(revenue_by_month)

    st.markdown("***")
    popular_months = df_order.loc[df_order['restaurant_id'] == resto_id].groupby(['month'])['total'].sum().to_frame().sort_values('month')
    st.markdown("### Most popular months:")
    st.bar_chart(popular_months)



def customer_page():
    # Allergies
    customer = st.sidebar.selectbox("Select a customer.", customers_list)
    st.header(
        f"Details on customer {customer}"
    )

    def buisiness_insights(customer_id, data):
        clv = data["total"].sum()
        crp = data["total"].count()
        cab = round(clv / crp, 2)
        return {
            "clv": clv,
            "crp": crp,
            "cab": cab
            }
    orders = df_order[df_order["customer_id"] == customer]
    st.subheader("Buisiness informations.")
    bi = buisiness_insights(customer, orders)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Customer Lifetime Value", value=f"{bi['clv']}$")
    col2.metric(label="Customer repeat purchase", value=f"{bi['crp']} orders")
    col3.metric(label="Customer average order", value=f"{bi['cab']}$/o")

    st.subheader("Allergy information")
    allergies = df_allergy_customer[df_allergy_customer["customer_id"] == customer]["allergy_id"].to_list()
    if len(allergies) == 0:
        st.write("This customer has no known allergy.")
    elif len(allergies) == 1:
        al = df_allergy[df_allergy["data_id"] == allergies[0]]
        name, severity = al["name"][allergies[0]], al["severity"][allergies[0]]
        st.write(f"This customer is allergic to {name}, which has {severity} severity.")
    else:
        st.write("This customer has the following allergies:")
        aller = df_allergy[df_allergy["data_id"].isin(allergies)][["name", "severity"]].reset_index(drop=True)
        aller.index += 1
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
    restaurants_names = df_restaurant[df_restaurant["data_id"].isin(restaurants)]["name"].to_list()
    restaurants_names.append("All")
    rest = st.selectbox("Select a restaurant", restaurants_names)
    if rest == "All":
        tot = round(orders["total"].sum(), 2)
        st.write(f"Overall, customer {customer} spent {tot}$.")
    else:
        rest_id = restaurants.intersection(set(df_restaurant[df_restaurant["name"] == rest]["data_id"].to_list()))
        orders = orders[orders["restaurant_id"] == rest_id.pop()]
        tot = round(orders["total"].sum(), 2)
        no_orders = orders.shape[0]
        if no_orders == 1:
            orders_string = "one order"
        else:
            orders_string = f"{no_orders} orders"
        st.write(f"Customer {customer} spent {tot}$ in restaurant {rest}, with {orders_string}.")
    orders_id = orders["data_id"].to_list()
    order_to_detail = st.selectbox("Select an order", orders_id)
    order_details = df_order_item[df_order_item["order_id"] == order_to_detail]
    restaurant_id = order_details["restaurant_id"].iloc[0]
    print(restaurant_id)
    restaurant_details = df_restaurant[df_restaurant["data_id"] == restaurant_id]
    restaurant_name = restaurant_details["name"].iloc[0]
    city = restaurant_details["city"].iloc[0]
    date = order_details["creation_date"].iloc[0]
    n = order_details.shape[0]
    if n == 1:
        no_items = "one item"
    else:
        no_items = f"{n} items"
    tot = round(order_details["total"].sum(), 2)
    st.write(f"This order was made in {restaurant_name}, {city}, on {date}, for a total of {tot}$. It contains {no_items}.")
    df = order_details[["name", "price", "amount", "total"]]
    df = df.reset_index(drop=True)
    df.index += 1
    st.write(df)

if modus == 'Map':
    display_maps()
elif modus == 'Restaurant View':
    restaurant_view()
elif modus == 'Customer page':
    customer_page()
