import json
import os
import matplotlib.pyplot as plt
from datetime import datetime
from tvdatafeed import Interval
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
def get_data(tv, nav, client, exchange, name, n_bars, mode, config):
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
            print(f'[stock:{name}] error get data:',e)
            return []
    elif mode == "fund":
        try:
            getd = nav.get_all(name, asDataFrame=True)
            getd = getd.drop(["tags","fund"],axis=1)
            # prepare data to same format with stock
            getd = getd.rename(columns = {'value':'close','updated':'datetime'})
        except Exception as e:
            print(f'[fund:{name}] error get data:',e)
            return []
    elif mode == "crypto":
        try:
            # get date to request history data
            current_date = datetime.now().date()
            current_date = current_date.replace(year=current_date.year -1)
            start_date = current_date.strftime('%d %b %Y')

            request = client(api_key=config['api_key'], api_secret=config['api_secret'])
            klines = request.get_historical_klines(name, "1d", start_date)
            getd = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
            # convert date format
            getd['timestamp'] = getd['timestamp'].apply(lambda x: (datetime.fromtimestamp(x / 1000)).strftime("%Y-%m-%d"))
            # convert any type to date
            getd['timestamp'] = pd.to_datetime(getd['timestamp'])
            getd = getd.rename(columns = {'timestamp':'datetime'})
            getd = getd.iloc[:,:6]
        except Exception as e:
            print(f'[crypto:{name}] error get data:',e)
            return []

    # save data to parquet when data more than one
    if len(getd)>0:
        getd.to_parquet(os.path.join(os.getcwd(), 'data', mode, exchange, f"{name}.parquet"))

    return getd


# load data
def load_data(name, mode, exchange, time):
    try:
        loadd = pd.read_parquet(os.path.join(os.getcwd(),'data', mode, exchange ,f"{name}.parquet"))
        if int(loadd.shape[0]) == time or int(loadd.shape[0]) < time:
            return loadd
        elif int(loadd.shape[0]) > time:
            return loadd.iloc[time:,:]
        else:
            return []
    except Exception as e:
        print('error load data from parquet file:',e)
        return []

def convertday2int(text):
    date = datetime.strptime(text, '%Y-%m-%d').date()
    weekday = (date.weekday()) % 5
    return weekday

def preprocess_befor_fe(df, name, mode):
    if mode == "stock":
        df = df.rename(columns = {"datetime":"date","symbol":"tic"})
        df['date'] = df['date'].dt.date.astype(str)
        df['tic'] = f"{name}"
        df['day'] = df['date'].apply(convertday2int)

    return df

    

        
