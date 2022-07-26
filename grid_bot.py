from pymongo import MongoClient

class GridBot:
    def __init__(self, params = {}):
        self.n_grids = params['n_grids'] #Numero de grids
        self.p_grids = params['p_grids'] #Porcentaje de distancia entre grids
        self.s_grids = params['s_grids'] #Tamanio de la orden por grid
        
        client = MongoClient('localhost')
        self.db = client['BINANCE']
    
    #activo donde queremos poner la orden esta disponible
    def is_available(self, symbol, price):
        cursor = self.db['ACTIVE_ORDERS']
        query = {'s':symbol.replace('/',''),
                 'p':{'$gt':float(price*(1 - self.p_grids)),
                '$lt':float(price*(1 + self.p_grids))},
                 }
        active_order = list(cursor.find(query))
        if len(active_order) > 0:
            return False
        return True
    
    def cancel_orders(self, symbol, range_orders):
        cursor = self.db['ACTIVE_ORDERS']
        query = {
            's': symbol.replace('/', ''),
            '$or':[{'p':{'$gt':float(range_orders[1])}},{{'p':{'$lt':float(range_orders[0])}}}]
        }
        cancel_orders = list(cursor.find(query))
        return cancel_orders
    
    #generar las ordenes y regresar los diccionarios
    def get_orders(self,symbol):
        symbol_info = self.db['SYMBOL_INFO'].find_one({'symbol':symbol})
        midprice = symbol_info['midprice']
        range_orders = (midprice*(1-self.p_grids*self.n_grids), midprice*(1+self.p_grids*self.n_grids))
        new_orders = []
        
        for i in range(1,self.n_grids+1):
            price = midprice * (1 - (i * self.p_grids)) #generar ordenes de compra
            
            if self.is_available(symbol, price):
                buy_order = {
                    'symbol': symbol,
                    'type':'limit',
                    'side':'buy',
                    'amount': self.s_grids * float(symbol_info['minNotional']),
                    'price': price,
                    'params':{
                        
                    }
                }
                new_orders.append(buy_order)
                
            price = midprice * (1 + (i * self.p_grids))
            
            if self.is_available(symbol, price):
                sell_order = {
                    'symbol': symbol,
                    'type':'limit',
                    'side':'sell',
                    'amount': self.s_grids * float(symbol_info['minNotional']),
                    'price': price,
                    'params':{
                        
                    }
                }
                new_orders.append(sell_order)
        
        return new_orders, self.cancel_orders(symbol = symbol, range_orders = range_orders)
        
