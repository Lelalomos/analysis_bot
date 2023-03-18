from talib.abstract import EMA, MACD
import talib.abstract as ta
import talib
import numpy as np
from indicators import mtf_ssl, pvt_with_divergence

class indicators:
    def __init__(self):
        pass
        
    def cross_ema(self, df, config):
        low_span = config['low_span']
        long_span = config['long_span']

        df['low_df'] = EMA(df['close'], low_span)
        df['long_df'] = EMA(df['close'], long_span)

        low_line = list(df['low_df'])
        long_line = list(df['long_df'])

        # logic buy and sell
        #     buy 100>200
        if low_line[-1] > long_line[-1]:
            return 2
        #     sell 100<200
        elif low_line[-1] < long_line[-1]:
            return -1
        
        return 0
    
    def cross_rsi(self, df, config):
        rsi_short_line = talib.RSI(df['close'],config['rsi_short'])
        rsi_long_line = talib.RSI(df['close'],config['rsi_long'])

        if rsi_short_line.iloc[-1] > rsi_long_line.iloc[-1]:
            return 2
        elif rsi_short_line.iloc[-1] < rsi_long_line.iloc[-1]:
            return -1

        return 0
    
    def macd(self, df, config):
        macd_line, signal_line, _ = MACD(df['close'], config['fastperiod'], config['slowperiod'], config['signalperiod'])
        if macd_line[-1] > signal_line[-1]:
            return 2
        elif macd_line[-1] < signal_line[-1]:
            return -1
        return 0
    

    def ichimoku_cloud(self, df, config):

        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        period9_high = df['high'].rolling(window=config['tenkansen_value']).max()
        period9_low = df['low'].rolling(window=config['tenkansen_value']).min()
        tenkan_sen = (period9_high + period9_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = df['high'].rolling(window=config['kinjunsen_value']).max()
        period26_low = df['low'].rolling(window=config['kinjunsen_value']).min()
        kijun_sen = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(config['shift_value'])

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = df['high'].rolling(window=config['senkou_b_value']).max()
        period52_low = df['low'].rolling(window=config['senkou_b_value']).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(config['shift_value'])

        df['cloud_green_line_a'] = senkou_span_a
        df['cloud_red_line_b'] = senkou_span_b

        # plot img
        # plot_save_img(df['cloud_green_line_a'], df['cloud_red_line_b'], namest)

        # logic buy and sell
        close = df['close'].to_list()[-1]
        cloud_green_line_a =    df['cloud_green_line_a'].to_list()[-1]
        cloud_red_line_b =  df['cloud_red_line_b'].to_list()[-1]

        close = float(close)
        cloud_green_line_a = float(cloud_green_line_a)
        cloud_red_line_b = float(cloud_red_line_b)

        # buy
        if close > cloud_green_line_a and close > cloud_red_line_b and cloud_green_line_a > cloud_red_line_b:
            return 2
        # sell
        elif close < cloud_green_line_a and close < cloud_red_line_b and cloud_green_line_a < cloud_red_line_b:
            return -1
        
        return 0
    
    def collect_mtfssl_pvtdiver(self, df, config):
        pvtup, pvtdown, pvt_osc = pvt_with_divergence(df, config['low_span'], config['long_span'])
        pvt_osc = pvt_osc[~np.isnan(pvt_osc)]
        pvtup = pvtup.dropna()
        pvtdown = pvtdown.dropna()
        sslup, ssldown = mtf_ssl(df, config['length_mtf_ssl'])
        sslup = sslup.dropna()
        ssldown = ssldown.dropna()

        # current close value must better than close value in past
        result_distance = 0
        if config['day'] == 1:
            result_distance = df['close'].iloc[-1] - df['close'].iloc[-2]
            # buy
            if sslup.to_list()[-1] > ssldown.to_list()[-1] and pvt_osc[-1] > pvtup.to_list()[-1] and result_distance >= 3:
                return 2 #False
            #     sell
            elif sslup.to_list()[-1] < ssldown.to_list()[-1] and pvt_osc[-1] < pvtdown.to_list()[-1]:
                return -1 #True
        else:
            config['day'] *= -1
            result_distance = df['close'].iloc[-1] - df['close'].iloc[config['day']]

            if sslup.to_list()[-1] > ssldown.to_list()[-1] and pvt_osc[-1] > pvtup.to_list()[-1] and result_distance >= 3:
                return 2 #False
            
        return 0
    
    def process(self, name, df, config):
        sum_score = 0 
        for cf in config:
            result = eval(f"self.{name}")(df, cf)
            sum_score+=result
        return sum_score
    