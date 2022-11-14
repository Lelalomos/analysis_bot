from tvDatafeed import TvDatafeed, Interval
# import matplotlib.pyplot as plt
import pandas as pd
import time
import multiprocessing as mp

c = list()
tv = TvDatafeed(username=None,password=None)
excel_stock = pd.read_csv('list_stock_thai.csv') 

def loop_yield(list_v,step=5):
    for i in range(0,len(list_v),step):
        yield list_v[i:i+step]

def search_stock_th(name_stock,q):
    stock_list = tv.search_symbol(name_stock)
    for stock_d in stock_list:
        get_stock = stock_d.get('country')
        if get_stock == "TH":
            q.put('found')

    return q.put(name_stock)


if __name__ == "__main__":
    q = mp.Queue()
    for stocks in loop_yield(excel_stock['name'].to_list()):
        # multiprocessing
        process = list()
        for st in stocks:
            print('start st:',st)
            process.append(mp.Process(target=search_stock_th, args=(st,q)))
        
        for p in process:
            p.start()
            c.append(q.get())

        for p in process:
            p.join()

        time.sleep(10)
        print('end st:',stocks)

        # break

    print('c:',c)
    
        
        