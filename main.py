from tvDatafeed import TvDatafeed, Interval
import multiprocessing as mp
import json
import pandas as pd
import os
from trade import cross_ema

def get_data(tv, exchange, name_stock, n_bars):
    return tv.get_hist(name_stock, exchange, interval=Interval.in_daily, n_bars=n_bars)


list_stock = list()
indicator_config = {
    "cross_ema":{
        "low_span": 90,
        "long_span": 95
    },
    "plot_config":{
        "plot": True,
        "n_bar": 60
    }
}

config = {
    "find-min": True,
    "find-max": True
}

if __name__ == "__main__":
    # variable
    tv = TvDatafeed(username=None,password=None)

    # load config
    with open(os.path.join(os.getcwd(),'config','list_stock','stock_config.json')) as f:
        json_stock = json.load(f)

    
    for exc in json_stock:
        for namest, nbar in json_stock[exc].items():
            data = get_data(tv, exc, namest, nbar['limit_data'])
            result_ema = cross_ema(data, namest, **indicator_config)
            
            print()
            print('name stock:',namest)
            min_data = data[data['close'] == data['close'].min()]
            min_data = min_data.reset_index()
            print(f"min data --> date: {min_data['datetime'].values[0]}, close: {min_data['close'].values[0]}")
            if result_ema == 1:
                print('sell')
            elif result_ema == 0:
                print('buy')
            else:
                print('noting')
            print()
    

    

    
