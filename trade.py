from talib.abstract import EMA, STOCH
import matplotlib.pyplot as plt
import os

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

    low_span = config['cross_ema']['low_span']
    long_span = config['cross_ema']['long_span']
    low_df = EMA(df['close'], low_span)
    long_df = EMA(df['close'], long_span)

    if config['plot_config']['plot']:
        fig = plt.figure(figsize=(10, 7))
        plt.title(f'cross_ema-{namest}')
        plt.plot(low_df[config['plot_config']['n_bar']*-1:], 'g', label= f'ema{low_span}')
        plt.plot(long_df[config['plot_config']['n_bar']*-1:], 'r', label= f'ema{long_span}')
        leg = plt.legend(loc='upper left')
        plt.savefig(os.path.join(os.getcwd(),'images',f'cross_ema-{namest}.jpg'))


    # logic buy and sell
    #     buy 100>200
    if low_df[-1] > long_df[-1]:
        return 0 #False
    #     sell 100<200
    elif low_df[-1] < long_df[-1]:
        return 1 #True
    return 3


def ema_stoch(df):
    ...

def ichimoku(df):
    ...

def macd_stoch(df):
    ...

def macd(df):
    ...