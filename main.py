# version 3
from trade_algorithm import indicators
from tvDatafeed import TvDatafeed
import pandas as pd
import os
import json
import datetime
import numpy as np
from sklearn import preprocessing
import pythainav as nav
from utils import get_data, load_data

pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 1000)

tv = TvDatafeed(username=None,password=None)

# list stock config
with open(os.path.join(os.getcwd(),'config','list_stock','stock_config.json')) as f:
    json_stock = json.load(f)

assert json_stock is not None, "error read stock config"

# indicator config for long term
with open(os.path.join(os.getcwd(),'config','indicator','long_indicator.json')) as f:
    indicator_config_long = json.load(f)

assert indicator_config_long is not None, "error read indicator config (long term)"

# indicator config for short term
with open(os.path.join(os.getcwd(),'config','indicator','short_indicator.json')) as f:
    indicator_config_short = json.load(f)

assert indicator_config_short is not None, "error read indicator config (short term)"

# config
with open(os.path.join(os.getcwd(),'config','config.json')) as f:
    config = json.load(f)

assert config is not None, "error read config"

# find current date
current_date = datetime.datetime.today().date()

indicator_engine = indicators()

# prepare config
mode = config['mode']
max_days = config[mode]['len_data']
max_days = max(max_days)

for key_exc in json_stock[f'list_{mode}']:
    print(f'exchange: {key_exc}')

    dict_min_value_1 = {}
    dict_min_value_2 = {}
    dict_remaining_date = {}
    dict_pair_daywithscore = {
        "stock_score":[],
        "min_date":[]
    }

    dict_stock_name_score = {}
    for namest2dict in json_stock[f'list_{mode}'][key_exc]:
        dict_stock_name_score.update({namest2dict:0})
        dict_remaining_date.update({namest2dict:{}})
        for t in config[mode]['len_data']:
            dict_remaining_date[namest2dict].update({f"{t}":0})

    for namest in json_stock[f'list_{mode}'][key_exc]:
        if config['fetch_newdata'] == "on":
            try:
                data = get_data(tv, nav, key_exc, namest, max_days, mode)
                if len(data) == 0:
                    continue
            except Exception as e:
                print(f'stock name: {namest}')
                print(f'error: {e}')
                continue
        else:
            data = load_data(namest, mode, key_exc, max_days)

        score = 0
        # first indicators
        for indicator in config[mode]['long_indicators']:
            # print('indicator:',indicator)
            score += indicator_engine.process(f"{indicator}", data, indicator_config_long[f'{indicator}'])
        
        # print('score:',score)
        dict_stock_name_score[namest] = score

        for t in config[mode]['len_data']:
            data_follow_time = load_data(namest, mode, key_exc, t)

            # find min value in dataframe
            data_cal_number_days = data_follow_time[data_follow_time['close'] == min(list(data_follow_time['close']))]

            # convert timestamp to datetime.date
            if len(data_cal_number_days) > 1:
                data_cal_number_days = data_cal_number_days.iloc[-1,:]
                date_min_value = data_cal_number_days['datetime'].to_pydatetime().date()
            else:
                # convert numpy.datetime64 to datetime
                date_min_value = pd.to_datetime(data_cal_number_days['datetime'].values[0]).to_pydatetime().date()
            # date_min_value = data_cal_number_days['datetime'].to_pydatetime().date()
            remaining_date = current_date - date_min_value
            
            df_min_value = data_follow_time[data_follow_time['close'] == min(list(data_follow_time['close']))]
            df_current_value = data_follow_time.iloc[-2:-1,:]
            if t == 62:
                dict_remaining_date[namest][f'{t}'] = remaining_date.days
                dict_min_value_1[namest] = df_current_value['close'].values[0] - min(list(data_follow_time['close']))
            else:
                dict_remaining_date[namest][f'{t}'] = remaining_date.days
                dict_min_value_2[namest] = df_current_value['close'].values[0] - min(list(data_follow_time['close']))
            
    # sort data by current close value minus the smallest a value in the past
    dict_min_value_1_sort = dict(sorted(dict_min_value_1.items(), key=lambda item: item[1], reverse=True))
    dict_min_value_2_sort = dict(sorted(dict_min_value_2.items(), key=lambda item: item[1], reverse=True))

    # increse score following by date
    dict_prepare_sort = {}
    score_follow_time = 0.5
    for data_v in config[mode]['len_data']:
        for key,_ in dict_remaining_date.items():
            dict_prepare_sort[key] = dict_remaining_date[key][f"{data_v}"]
        
        dict_remaining_date_sort = dict(sorted(dict_prepare_sort.items(), key=lambda item: item[1],reverse=True))
        list_score = [i+score_follow_time for i in range(10)]

        reverse_date_tomin_first = dict(sorted(dict_remaining_date_sort.items(), key=lambda item: item[1]))
        
        print(f'List stock name of the lowest close value in the {data_v} days')
        for k,v in reverse_date_tomin_first.items():
            if int(v) <= 10:
                dict_pair_daywithscore['min_date'].append(k)
                print(k,v)
        print('stock min day:',dict_pair_daywithscore['min_date'])
        print('-'*100)

        for add_score, key_score in zip(list_score,list(dict_remaining_date_sort.keys())[:10]):
            dict_stock_name_score[key_score] = dict_stock_name_score[key_score] + add_score

        score_follow_time+=0.5        
        
        # loop increase score
    for dict_sort_value in [dict_min_value_1_sort, dict_min_value_2_sort]:
        # print('dict_sort_value:',dict_sort_value)
        # normalize score
        list_score = [i*1000 for i in range(1,len(dict_sort_value)+1)]
        np_score = np.array(list_score)
        normalized_arr = preprocessing.normalize([np_score])
        # print('normalize:',normalized_arr.tolist()[0])

        dict_score = {} 
        for score,(k,v) in zip(normalized_arr.tolist()[0],dict_sort_value.items()):
            dict_score.update({k:score})

        # print('dict_score:',dict_score)
        for k,v in dict_score.items():
            dict_stock_name_score[k] = dict_stock_name_score[k] + dict_score[k]


    # print('score:',dict_stock_name_score)
    dict_stock_name_score_sort = dict(sorted(dict_stock_name_score.items(), key=lambda item: item[1], reverse=True))

    # print('dict_stock_name_score_sort final:',dict_stock_name_score_sort)
    
    print(f'days: {max_days}')
    print('-'*100)
    int_check = 0
    for k,v in dict_stock_name_score_sort.items():
        dict_pair_daywithscore['stock_score'].append(k)
        print(k,v)
        int_check+=1
        if int_check >=10:
            break
    print('-'*100)

    # pair
    print(f'The name of the stock that has reached the lowest price in {config[mode]["len_data"]} days')
    dict_pair_daywithscore['stock_score'] = dict_pair_daywithscore['stock_score'][:10]
    for stock_sc in dict_pair_daywithscore['stock_score']:
        if stock_sc in dict_pair_daywithscore['min_date']:
            # list_date_less_than_10.append(stock_sc)
            print(stock_sc)

    # testing
    # trend up 
    dict_stock_trend_up = {}
    for tup in dict_pair_daywithscore['min_date']:
        dict_stock_trend_up.update({tup:0})

    for tup in dict_pair_daywithscore['min_date']:
        try:
            # data = get_data(tv, key_exc, tup, days)
            # data = data.reset_index()
            data = load_data(namest, mode, key_exc, t)
        except Exception as e:
            print(f'stock name: {tup}')
            print(f'error: {e}')
            continue

        score = 0
        # first indicators
        for indicator in config[mode]['short_indicators']:
            # print('indicator:',indicator)
            score += indicator_engine.process(f"{indicator}", data, indicator_config_short[f'{indicator}'])

        dict_stock_trend_up[tup] = score

    dict_stock_trend_up_sort = dict(sorted(dict_stock_trend_up.items(), key=lambda item: item[1], reverse=True))
    print('the name of stock is trend up')
    for k,v in dict_stock_trend_up_sort.items():
        print(k,v)

    print()

