import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
from tvDatafeed import Interval
import pandas as pd

def read_config(path_json):
    """

    Args:
        path_json (string): path json file

    Returns:
        dictionary: data of json file

    """
    with open(path_json) as js:
        return json.load(js)

# read config for plot image from plot_image folder
config_plot = read_config(os.path.join(os.getcwd(),'config','plot_image','plot_config.json'))

def loop_yield(list_v,step=5):
    for i in range(0,len(list_v),step):
        yield list_v[i:i+step]

def search_stock_th(name_stock, tv, q):
    stock_list = tv.search_symbol(name_stock)
    for stock_d in stock_list:
        get_stock = stock_d.get('country')
        if get_stock == "TH":
            q.put('found')

    return q.put(name_stock)

def plot_save_img(green_line, red_line, namest):
    if config_plot['plot_config']['plot']:
        os.makedirs(os.path.join(os.getcwd(),'images',f'macd-{namest}'),exist_ok=True)
        plt.figure(figsize=(10, 7))
        plt.title(f'macd-{namest}')
        plt.plot(green_line[config_plot['plot_config']['n_bar']*-1:], 'g', label= f'green line')
        plt.plot(red_line[config_plot['plot_config']['n_bar']*-1:], 'r', label= f'red line')
        plt.legend(loc='upper left')
        plt.savefig(os.path.join(os.getcwd(),'images',f'macd-{namest}-{datetime.now().strftime("%Y%m%d")}.jpg'))


# timeout: _ssl.c:1112: The handshake operation timed out
def get_data(tv, nav, exchange, name, n_bars, mode):
    # prepare folder to store data
    os.makedirs(os.path.join(os.getcwd(),'data'),exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(),'data',mode),exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(),'data',mode,exchange),exist_ok=True)
    # os.makedirs(os.path.join(os.getcwd(),'data','crypto'),exist_ok=True)

    # get data
    getd = None
    if mode == "stock":
        try:
            getd = tv.get_hist(name, exchange, interval=Interval.in_daily, n_bars=n_bars)
            getd = getd.reset_index()
        except Exception as e:
            print('[stock] error get data:',e)
            return []
    elif mode == "fund":
        try:
            getd = nav.get_all(name, asDataFrame=True)
            getd = getd.drop(["tags","fund"],axis=1)
            # prepare data to same format with stock
            getd = getd.rename(columns = {'value':'close','updated':'datetime'})
        except Exception as e:
            print('[fund] error get data:',e)
            return []
    elif mode == "crypto":
        pass

    # save data to parquet when data more than one
    if len(getd)>0:
        getd.to_parquet(os.path.join(os.getcwd(), 'data', mode, exchange, f"{name}.parquet"))

    return getd


# load data
def load_data(name, mode, exchange, time):
    try:
        loadd = pd.read_parquet(os.path.join(os.getcwd(),'data', mode, exchange ,f"{name}.parquet"))
        if len(loadd) > 0:
            return loadd.iloc[:time,:]
        else:
            return []
    except Exception as e:
        print('error load data from parquet file:',e)
        return []

        
