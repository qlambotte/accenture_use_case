import pandas as pd
from geopy.geocoders import Nominatim

allergy_customer = pd.read_csv(
    "../data/ODL_ALLERGY_CUSTOMER.csv",
    usecols=["allergy_id","customer_id"])
allergy = pd.read_csv(
    "../data/ODL_ALLERGY.csv",
    usecols=["data_id","severity", "name"])
restaurant = pd.read_csv(
    "../data/ODL_RESTAURANT.csv",
    usecols=[
        "data_id", "name", "opening_hours",
        "city", "street", "phone_number",
        "creation_date", "email"]
)
order = pd.read_csv(
    "../data/ODL_ORDER.csv",
    usecols=["restaurant_id", "creation_date", "customer_id", "data_id"])
orderables = pd.read_csv(
    "../data/ODL_ORDERABLES.csv",
    usecols=["price", "restaurant_id", "data_id", "name"])
order_item = pd.read_csv(
    "../data/ODL_ORDER_ITEM.csv",
    usecols=["order_id", "amount", "data_id", "orderable_id"])

## Preprocessing of ALLERGY
# Removes duplicates in allergy table
allergy = allergy.drop_duplicates(subset="data_id")

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
allergic_customer = set(allergy_customer["customer_id"].tolist())

# Removes customer that do not have an order in the order table
allergy_customer = allergy_customer.apply(correct_data, axis = 1)
customer_to_remove = allergic_customer - set(order["customer_id"].tolist())
allergy_customer = allergy_customer[
    ~allergy_customer["customer_id"].isin(customer_to_remove)
]

## Preprocessing of ORDER_ITEM

# Joins table ORDERABLES along orderable_id
order_item = order_item.join(orderables.set_index("data_id"), on="orderable_id")

# Joins ORDER alons order_id
order.item = order_item.join(order.set_index('data_id'), on="order_id")

# Adds total amount per order item
order_item["total"] = order_item["amount"] * order_item["price"]

# Adds restaurant info to order_item
rest = restaurant[['data_id' , 'city']]
order_item = order_item.join(rest.set_index('data_id'), on="restaurant_id")

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
pd.to_datetime(order_df['creation_date_only'],format="%x")
order['month_year'] = pd.to_datetime(order['creation_date_only']).dt.strftime('%y/%m')
order['month'] = pd.to_datetime(order['creation_date_only']).dt.strftime('%m')

## RESTAURANT TABLE
# Get missing cities
geolocator = Nominatim(user_agent="geoapiExercises")

def get_city(row):
    if row["city"].isna():
        place = geolocator.geocode(f"{row["street"]}, San Fransisco")
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

restaurant["address"] = (df_restaurant['street'].map(str) + ', ' + df_restaurant['city'].map(str))

restaurant = restaurant.apply(get_address_latlon, axis=1)

# Add revenue of restaurant
resto_value = order.groupby(['restaurant_id'])['order_value'].sum().sort_values(ascending=False)
resto_value = resto_value.to_frame()
restaurant = restaurant.join(resto_value['order_value'], on='data_id',)
restaurant = restaurant.rename(columns={"order_value":"revenue"})


## Preprocessing of ORDERABLES

orderables['cost'] = orderables['price'].mean()
orderables['profit'] = orderables['price'] - orderables['cost']
