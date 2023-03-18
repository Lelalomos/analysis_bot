# version 3 (beta)
from trade_algorithm import indicators
from tvDatafeed import TvDatafeed,Interval
import pandas as pd
import os
import json
import datetime

pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 1000)

tv = TvDatafeed(username=None,password=None)

# timeout: _ssl.c:1112: The handshake operation timed out
def get_data(tv, exchange, name_stock, n_bars):
    return tv.get_hist(name_stock, exchange, interval=Interval.in_daily, n_bars=n_bars)

# list stock config
with open(os.path.join(os.getcwd(),'config','list_stock','stock_test.json')) as f:
    json_stock = json.load(f)

assert json_stock is not None, "error read stock config"


# indicator config
with open(os.path.join(os.getcwd(),'config','indicator','indicator.json')) as f:
    indicator_config = json.load(f)

assert indicator_config is not None, "error read indicator config"

# config
with open(os.path.join(os.getcwd(),'config','config.json')) as f:
    config = json.load(f)

assert config is not None, "error read config"

# print('dict_stock_name_score:',dict_stock_name_score)
# find current date
current_date = datetime.datetime.today().date()

list_time = [62, 93, 124, 155]
indicator_engine = indicators()

for days in config['len_data']:
    for key_exc in json_stock['list_stock']:
        print(f'exchange: {key_exc}')

        dict_min_value_1 = {}
        dict_min_value_2 = {}
        dict_remaining_date = {}
        dict_pair_daywithscore = {
            "stock_score":[],
            "min_date":[]
        }

        dict_stock_name_score = {}
        for namest2dict in json_stock['list_stock'][key_exc]:
            dict_stock_name_score.update({namest2dict:0})
            dict_remaining_date.update({namest2dict:{}})
            for t in list_time:
                dict_remaining_date[namest2dict].update({f"{t}":0})

        for namest in json_stock['list_stock'][key_exc]:
            try:
                data = get_data(tv, key_exc, namest, days)
                data = data.reset_index()
                len_data = len(data)
                print(f'stock name: {namest}:{len(data)}')
            except Exception as e:
                print(f'stock name: {namest}')
                print(f'error: {e}')
                continue

            score = 0
            for indicator in config['inducators']:
                print('indicator:',indicator)
                score += indicator_engine.process(f"{indicator}", data, indicator_config[f'{indicator}'])
                
            print('score:',score)
            
