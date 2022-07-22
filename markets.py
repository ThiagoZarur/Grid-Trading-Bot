import ccxt
import pandas as pd
from pymongo import MongoClient, mongo_client
from pprint import pprint
from utils import fix_floats
from decouple import config

def update_markets(exchange):
    client = MongoClient('localhost')
    db = client['BINANCE']
    cursor = db['SYMBOL_INFO']
    cursor_balances = db['BALANCES']
    balances = exchange.fetch_balance()['info']['balances']
    
    for balance in balances:
        balance = fix_floats(balance)
        query = {'asset':balance['asset']}
        update = {'$set':balance}
        cursor_balances.update_many(query, update, True) #aquí True nos permite actualizar en caso de no encontrar la petición
        
    
    markets = exchange.fetch_markets()
    
    in_db = pd.DataFrame(list(cursor.find()))
    temp = []
    
    if len(in_db) != 0:
        temp = list(in_db['symbol'])
        
    for market in markets:
        symbol = market['symbol']
        id = market['id']
        precision = market['precision']
        minNotional = market['info']['filters'][3]['minNotional']
        
        symbol_info = {
            'symbol': symbol,
            'id': id,
            'precision': precision,
            'minNotional': minNotional,
            'ask': 0,
            'bid': 0,
            'midprice': 0
        }
        
        if len(in_db) == 0:
            cursor.insert_one(symbol_info)
        else:
            if symbol in temp:
                query = {'symbol':symbol}
                update = {'$set': symbol_info}
                cursor.update_one(query, update, True)
                temp.remove(symbol)
                
        if len(temp) != 0:
            for symbol in temp:
                query = {'symbol': symbol}
                cursor.d_one(query)
        client.close()
        
exchange = ccxt.binance({
    'api_key': config('API_KEY',default=''),
    'secret':config('PRIVATE_KEY',default=''),
    'enableRateLimit': True,
    'timeout': 3000,
    'options':{
    'defaultType': 'spot'
    }
})

update_markets(exchange)