
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