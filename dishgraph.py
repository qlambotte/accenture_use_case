import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class DishGrapher:

    def __init__(self):
        self.sales = pd.read_csv('./data/order_item.csv', usecols=['restaurant_id', 'name', 'amount', 'price', 'total', 'city']) 
        ### load df_sales [amount, revenue, name, city, restaurant_id]
        ### load df_sales by restaurant [restaurant_id, name, amount, revenue]

    def popular(self, city: str , col: str):
        # need amount, name, city
        """
        Function that inputs a city name and outputs a dataframe of most popular dishes by revenue

        :params city: str either 'New York' or 'San Francisco'
        :param col: str either 'amount' or 'total
        """
        df = self.sales[self.sales['city']==city]
        return df[[col,'name']].groupby('name').sum().sort_values(col,ascending=False)
        

    def popular_by_restaurant(self, restaurant_id: int, col: str):
        # needs amount, name, restaurant_id
        """
        Function that given an restaurant id  and column and returns a tabel of dishes sorted by column sold

        :param restaurant_id: int that represent restaurant_id
        :param col: str represent either amount ('amount') or revenue ('total')
        """
        
        am_table = self.sales.groupby(['restaurant_id', 'name']).sum().loc[restaurant_id][[col]]
        am_table = am_table.reset_index()
        am_table['abbrev_name'] = am_table['name'].map(lambda x: x[:70]+'...' if len(x)>70 else x)
        am_table[['abbrev_name', col]].set_index('abbrev_name').sort_values(col, ascending=False)


        fig, ax = plt.subplots()
        sns.barplot(y='abbrev_name', x=col, data=am_table, color='salmon')
        plt.ylabel('name of orderable')
        plt.xlabel(f'{col}')

        return fig

    def price_distributer(self, dish: str):
        # needs name, price
        '''
        Function that outputs a graph of the distribution of a dish
        
        param dish: str that represents name of dish
        '''
        dish_price_distribution = self.sales[self.sales['name']==dish].groupby('price').sum()
        avg_price = np.round(dish_price_distribution['total'].sum()/dish_price_distribution['amount'].sum(),2)


        # Calculate the binwidth of the histogram

        prices = list(dish_price_distribution.index)
        if len(prices) < 2:
            width = 0.1
        else:
            width = prices[-1]-prices[0]
            for i in range(len(prices)-1):
                width = min(width, prices[i+1]-prices[i])

        # create the figure

        fig, ax = plt.subplots()
        sns.histplot(x='price', data=self.sales[self.sales['name']==dish], hue='city', binwidth=width)
        plt.title(f'Distribution on of the price of {dish} \n Average price: ${avg_price}')
        plt.ylabel('Amount sold')
        plt.xlabel('Price of dish')
        
        return fig



class DishTrendGrapher:

    def init__(self, dish):
        self.dish = dish
        ### load dataframe resampled by month
        pass


    def dish_trend(self, restaurant_id: int, col: str):
        pass


    

    


    
