import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class dish_grapher:

    def __init__():
        ### load df_sales [amount, revenue, name, city, restaurant_id]
        ### load df_sales by restaurant [restaurant_id, name, amount, revenue]
        pass

    def popular_by_amount(city: str):
        # need amount, name, city
        """
        Function that inputs a city name and outputs a dataframe of most popular dishes by revenue
        """
        df = df_sales[df_sales['city']==city]
        return df['amount','name'].groupby('name').sum('amount').sort_values('amount',ascending=False)
        

    def popular_by_revenue(city: str):
        """
        Function that inputs a city name and outputs a dataframe of most popular dishes by revenue
        """
        df = df_sales[df_sales['city']==city]
        return df['paid','name'].groupby('name').sum('paid').sort_values('paid',ascending=False)
        

    def popular_by_amount_by_restaurant(restaurant_id: int):
        # needs amount, name, restaurant_id
        """
        Function that given an restaurant id return a tabel of dishes sorted by amount sold
        """
        am_table = pop_per_restaurant.loc[restaurant_id]
        am_table = am_table.reset_index()
        am_table['abbrev_name'] = am_table['name'].map(lambda x: x[:70]+'...' if len(x)>70 else x)
        am_table[['abbrev_name', 'paid']].set_index('abbrev_name').sort_values('paid', ascending=False)


        fig, ax = plt.subplots()
        sns.barplot(y='abbrev_name', x='paid', data=am_table, color='salmon')
        plt.ylabel('name of orderable')
        plt.xlabel('amount sold')

        return fig
    


    def popular_by_revenue_by_restaurant(restaurant_id: int):
        # needs revenue, name, restaurant_id
        # needs amount, name, restaurant_id
        """
        Function that given an restaurant id return a tabel of dishes sorted by amount sold
        """
        rev_table = pop_per_restaurant.loc[restaurant_id]
        rev_table = rev_table.reset_index()
        rev_table['abbrev_name'] = rev_table['name'].map(lambda x: x[:70]+'...' if len(x)>70 else x)
        rev_table[['abbrev_name', 'paid']].set_index('abbrev_name').sort_values('paid', ascending=False)


        fig, ax = plt.subplots()
        sns.barplot(y='abbrev_name', x='paid', data=am_table, color='salmon')
        plt.ylabel('name of orderable')
        plt.xlabel('amount sold')

        return fig

    def price_distributer(dish: str):
        # needs name, price
        '''
        Function that outputs a graph of the distribution of a dish
        
        param dish: str that represents name of dish
        '''
        dish_price_distribution = df_sales[df_sales['name']==dish].groupby('price').sum()
        tot_price  = (dish_price_distribution.reset_index()['price']*dish_price_distribution.reset_index()['amount']).sum()
        avg_price = np.round(tot_price/dish_price_distribution['amount'].sum(),2)


        # Calculate the binwidth of the histogram

        prices = list(dish_price_distribution.index)
        width = prices[-1]-prices[0]
        for i in range(len(prices)-1):
            width = min(width, prices[i+1]-prices[i])

        # create the figure

        fig, ax = plt.subplots()
        sns.histplot(x='price', data=df_sales[df_sales['name']==dish], hue='city', binwidth=width)
        plt.title(f'Distribution on of the price of {dish} \n Average price: ${avg_price}')
        plt.ylabel('Amount sold')
        plt.xlabel('Price of dish')
        
        return fig



class dish_trend_grapher:

    def init__():
        ### load dataframe resampled by month
        pass

    def dish_trend_by_revenue(restaurant_id: int):
        pass

    def dish_trend_by_amount(restaurant_id: int):
        pass

    


    
