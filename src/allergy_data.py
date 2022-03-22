import pandas as pd

order = pd.read_csv("./data/order.csv")

order.dropna(subset=["total"], inplace=True)

order_groups = order.groupby(["restaurant_id", "is_allergic"])

revenue_per_restaurant = order_groups["total"].sum()

customer_per_rest = order_groups["customer_id"].nunique()
customer_per_rest.name="Number_of_customer"

allergy_analysis=pd.concat([revenue_per_restaurant, customer_per_rest], axis=1)
allergy_analysis["Revenue per customer"] = allergy_analysis["total"]/allergy_analysis["Number_of_customer"]

allergy_analysis.to_csv("./data/allergy_data.csv")
