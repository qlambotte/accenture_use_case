import pandas as pd
from geopy.geocoders import Nominatim

allergy_customer = pd.read_csv(
    "./data/ODL_ALLERGY_CUSTOMER.csv",
    usecols=["allergy_id","customer_id"])
allergy = pd.read_csv(
    "./data/ODL_ALLERGY.csv",
    usecols=["data_id","severity", "name"])
restaurant = pd.read_csv(
    "./data/ODL_RESTAURANT.csv",
    usecols=[
        "data_id", "name", "opening_hours",
        "city", "street", "phone_number",
        "creation_date", "email"]
)
order = pd.read_csv(
    "./data/ODL_ORDER.csv",
    usecols=["restaurant_id", "creation_date", "customer_id", "data_id"])
orderables = pd.read_csv(
    "./data/ODL_ORDERABLES.csv",
    usecols=["price", "restaurant_id", "data_id", "name"])
order_item = pd.read_csv(
    "./data/ODL_ORDER_ITEM.csv",
    usecols=["order_id", "amount", "data_id", "orderable_id"])

## Preprocessing of ALLERGY
# Removes duplicates in allergy table
allergy = allergy.drop_duplicates(subset="data_id")

allergy.to_csv("./data/allergy.csv")

## Preprocessing og ALLERGY_CUSTOMER
# corrects the data (missing values in customer_id are in allergy_id)
def correct_data(row):
    if pd.isnull(row["customer_id"]):
        data = row["allergy_id"].split(";")
        row["allergy_id"] = int(data[0])
        row["customer_id"] = int(data[1])
    else:
        row["customer_id"] = int(row["customer_id"])
        row["allergy_id"] = int(row["allergy_id"])
    return row

# set of allergic customer
allergic_customer = set(allergy_customer["customer_id"].to_list())

# Removes customer that do not have an order in the order table
allergy_customer = allergy_customer.apply(correct_data, axis = 1)
customer_to_remove = allergic_customer - set(order["customer_id"].tolist())
allergy_customer = allergy_customer[
    ~allergy_customer["customer_id"].isin(customer_to_remove)
]

allergy_customer.to_csv("./data/allergy_customer.csv")

## Preprocessing of ORDER_ITEM

# Joins table ORDERABLES along orderable_id
order_item = order_item.join(orderables.set_index("data_id"), on="orderable_id")

# Joins ORDER alons order_id
order_item = order_item.join(order.loc[:, order.columns !="restaurant_id"].set_index('data_id'), on="order_id")

# Adds total amount per order item
order_item["total"] = order_item["amount"] * order_item["price"]

# Adds restaurant info to order_item
rest = restaurant[['data_id' , 'city']]
order_item = order_item.join(rest.set_index('data_id'), on="restaurant_id")

order_item.to_csv("./data/order_item.csv")

## Preprocessing of ORDER
# Compute total amount spend per order
order_tot = order_item[["order_id","total"]].groupby("order_id").sum()

# Add order_tot to ORDER
order = order.join(order_tot, on="data_id")

# Add location info to order table
order = order.join(restaurant[["data_id","city"]].set_index("data_id"), on="restaurant_id")

# Add a col to tell if order is associated to a customer with an allergy
order["is_allergic"] = order["customer_id"].map(lambda x: (x in allergic_customer))

# Cleans the date
order[['creation_date_only', 'creation_time']] = order['creation_date'].str.split(' ', 1, expand=True)
pd.to_datetime(order['creation_date_only'],format="%x")
order['month_year'] = pd.to_datetime(order['creation_date_only']).dt.strftime('%y/%m')
order['month'] = pd.to_datetime(order['creation_date_only']).dt.strftime('%m')

order.to_csv("./data/order.csv")

## RESTAURANT TABLE
# Get missing cities
geolocator = Nominatim(user_agent="geoapiExercises")

def get_city(row):
    if pd.isna(row["city"]):
        place = geolocator.geocode(f"{row['street']}, San Fransisco")
        if place:
            row["city"] = "San Fransisco"
        else:
            row["city"] = "New York"
    return row

restaurant = restaurant.apply(get_city, axis=1)

# Get coordinates of restaurants
geolocator = Nominatim(user_agent="Acc_app_geo")

def get_address_latlon(row):
    address = row["address"]
    location = geolocator.geocode(address, timeout=10)
    if location:
        row["lat"]=location.latitude
        row["lon"]=location.longitude
    else :
        row["lat"] = None
        row["lon"] = None
    return row

restaurant["address"] = (restaurant['street'].map(str) + ', ' + restaurant['city'].map(str))

restaurant = restaurant.apply(get_address_latlon, axis=1)

 # Add revenue of restaurant
resto_value = order.groupby(['restaurant_id'])['total'].sum().sort_values(ascending=False)
resto_value = resto_value.to_frame()
restaurant = restaurant.join(resto_value['total'], on='data_id',)
restaurant = restaurant.rename(columns={"total":"revenue"})

restaurant.loc[:,'cost_of_goods'] = resto_value['total'] * 0.15
restaurant.loc[:,'cost_of_labor_month'] = (resto_value['total'].mean() * 0.41) / 12
restaurant.loc[:,'fixed_costs_month'] = (resto_value['total'].mean() * 0.36) / 12
restaurant.loc[:,'cost_of_labor_total'] = (resto_value['total'].mean() * 0.41)
restaurant.loc[:,'fixed_costs_total'] = (resto_value['total'].mean() * 0.36)
restaurant.loc['total_PNL'] = restaurant['revenue'] - (restaurant['cost_of_goods'] + restaurant['fixed_costs_total'] + restaurant['cost_of_labor_total'])



restaurant.to_csv("./data/restaurants.csv")

## Preprocessing of ORDERABLES

orderables['cost'] = orderables['price'].mean()
orderables['profit'] = orderables['price'] - orderables['cost']

orderables.to_csv("./data/orderables.csv")


## Creating dataframes for trends in dishes

order_item['creation_date'] = pd.to_datetime(order_item['creation_date'])
s = order_item[order_item['city']=='New York'][['creation_date', 'amount', 'total', 'name']].groupby('name').resample('M', on='creation_date').sum()
t = order_item[order_item['city']=='San Francisco'][['creation_date', 'amount', 'total', 'name']].groupby('name').resample('M', on='creation_date').sum()
dish_per_month = s.join(t, lsuffix='_NY', rsuffix='_SF')
dish_per_month.to_csv('./data/dish_per_month.csv')

dish_per_rest = order_item[['creation_date', 'amount', 'total', 'name', 'restaurant_id']].groupby(['restaurant_id', 'name']).resample('M', on='creation_date').sum()
dish_per_rest.to_csv('./data/dish_per_rest.csv')

