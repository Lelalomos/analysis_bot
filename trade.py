from talib.abstract import EMA, MACD
from utils import plot_save_img
import numpy as np

def cross_ema(df, namest, **config):
    """

    Args:
        df (dataframe): datafrme stock,
        config (dict): EMA indicator config

    Returns:
        0: buy
        1: sell
        3: noting

    """

    low_span = config['low_span']
    long_span = config['long_span']
    # low_df = EMA(df['close'], low_span)
    # long_df = EMA(df['close'], long_span)
    df['low_df'] = EMA(df['close'], low_span)
    df['long_df'] = EMA(df['close'], long_span)

    low_line = list(df['low_df'])
    long_line = list(df['long_df'])

    plot_save_img(long_line, low_line, namest)

    # logic buy and sell
    #     buy 100>200
    if low_line[-1] > long_line[-1]:
        return 2, df #False
    #     sell 100<200
    elif low_line[-1] < long_line[-1]:
        return -1, df #True
    return 0, df


def ichimoku_cloud(df, tenkansen_value = 9, kinjunsen_value = 26, shift_value = 26, senkou_b_value = 52, namest = "empty"):
        """
        Description:
            Get the values of Lines for Ichimoku Cloud

        Args:
            df: Dataframe,
            int: tenkansen value,
            int: kinjunsen value,
            int: shift value,
            int: senkou_b value,

        Returns:
            df: Dataframe

        Reference Code: https://stackoverflow.com/questions/28477222/python-pandas-calculate-ichimoku-chart-components
        
        """

        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        period9_high = df['high'].rolling(window=tenkansen_value).max()
        period9_low = df['low'].rolling(window=tenkansen_value).min()
        tenkan_sen = (period9_high + period9_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        period26_high = df['high'].rolling(window=kinjunsen_value).max()
        period26_low = df['low'].rolling(window=kinjunsen_value).min()
        kijun_sen = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(shift_value)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        period52_high = df['high'].rolling(window=senkou_b_value).max()
        period52_low = df['low'].rolling(window=senkou_b_value).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(shift_value)

        df['cloud_green_line_a'] = senkou_span_a
        df['cloud_red_line_b'] = senkou_span_b

        # plot img
        plot_save_img(df['cloud_green_line_a'], df['cloud_red_line_b'], namest)

        # logic buy and sell
        close = df['close'].to_list()[-1]
        cloud_green_line_a =    df['cloud_green_line_a'].to_list()[-1]
        cloud_red_line_b =  df['cloud_red_line_b'].to_list()[-1]

        close = float(close)
        cloud_green_line_a = float(cloud_green_line_a)
        cloud_red_line_b = float(cloud_red_line_b)

        # buy
        if close > cloud_green_line_a and close > cloud_red_line_b and cloud_green_line_a > cloud_red_line_b:
            return 2, df
        # sell
        elif close < cloud_green_line_a and close < cloud_red_line_b and cloud_green_line_a < cloud_red_line_b:
            return -1, df
        # noting
        else:
            return 0, df       

def macd(df, namest):
    df['macd_line'], df["signal_line"], _ = MACD(df['close'])
    macd_line = list(df['macd_line'])
    signal_line = list(df["signal_line"])

    # config plot
    plot_save_img(macd_line, signal_line, namest)
        
    #     buy
    if macd_line[-1] > signal_line[-1]:
        return 2, df #False
    #     sell
    elif macd_line[-1] < signal_line[-1]:
        return -1, df #True
    return 0, df


def mtf_ssl(dataframe, length=250):
    df = dataframe.copy()

    df["smaHigh"] = df["high"].rolling(length).mean()
    df["smaLow"] = df["low"].rolling(length).mean()

    df["hlv"] = np.where(
        df["close"] > df["smaHigh"], 1, np.where(df["close"] < df["smaLow"], -1, np.NAN)
    )
    df["hlv"] = df["hlv"].ffill()

    df["sslDown"] = np.where(df["hlv"] < 0, df["smaHigh"], df["smaLow"])
    df["sslUp"] = np.where(df["hlv"] < 0, df["smaLow"], df["smaHigh"])

    return df["sslDown"], df["sslUp"]


def pvt_with_divergence(df,short_length = 90, long_length = 95):

    # Compute PVT
    pvt = (df['volume'] * (df['close'] - df['close'].shift(1)) / df['close']).cumsum()

    # Compute OBV Oscillator
    short_pvt = EMA(pvt, timeperiod=short_length)
    long_pvt = EMA(pvt, timeperiod=long_length)
    pvt_osc = short_pvt - long_pvt

    # Compute divergence
    up = (df['close'].pct_change().where(df['close'].pct_change() > 0, other=0)).rolling(window=short_length).mean()
    down = (-df['close'].pct_change().where(df['close'].pct_change() < 0, other=0)).rolling(window=short_length).mean()
    # down = (-(df['close'] - df['close'].shift(1) < 0)).rolling(window=short_length).mean()

    return up, down, pvt_osc


def collect_mtfssl_pvtdiver(df, short_ema, long_ema, day):
    pvtup, pvtdown, pvt_osc = pvt_with_divergence(df, short_ema, long_ema)
    pvt_osc = pvt_osc[~np.isnan(pvt_osc)]
    pvtup = pvtup.dropna()
    pvtdown = pvtdown.dropna()
    sslup, ssldown = mtf_ssl(df)
    sslup = sslup.dropna()
    ssldown = ssldown.dropna()

    # current close value must better than close value in past
    result_distance = 0
    if day == 1:
        result_distance = df['close'].iloc[-1] - df['close'].iloc[-2]
        # buy
        if sslup.to_list()[-1] > ssldown.to_list()[-1] and pvt_osc[-1] > pvtup.to_list()[-1] and result_distance >= 3:
            return 2 #False
        #     sell
        elif sslup.to_list()[-1] < ssldown.to_list()[-1] and pvt_osc[-1] < pvtdown.to_list()[-1]:
            return -1 #True
        else:
             return 0
    else:
        day *= -1
        result_distance = df['close'].iloc[-1] - df['close'].iloc[day]

        if sslup.to_list()[-1] > ssldown.to_list()[-1] and pvt_osc[-1] > pvtup.to_list()[-1] and result_distance >= 3:
            return 2 #False
        else:
             return 0
    


    



