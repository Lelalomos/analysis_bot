import numpy as np
from talib.abstract import EMA

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

def pvt_with_divergence(df,short_length = 30, long_length = 35):

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