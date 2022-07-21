#Se encargara de enviar las ordenes al exchange con su formato adecuado 

from gettext import find
from venv import create
import ccxt
from numpy import FLOATING_POINT_SUPPORT
from pkg_resources import resource_listdir 
from pymongo import MongoClient, mongo_client
from concurrent.futures import ThreadPoolExecutor
import time 

#formato del precio y orden
def format_price_and_amount(symbol, price, amount):
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor = db['SYMBOL_INFO']
    query = {'symbol': symbol}
    symbol_info = cursor.find_one(query)
    amount = round(amount,int(symbol_info['precision']['amount']))
    price = round(price,int(symbol_info['precision']['price']))
    return price, amount

#enviar las ordenes al exchange o cancelarlas con multihilo

def update_orders(exchange, new_orders=[], cancel_orders=[]):
    executor = ThreadPoolExecutor(max_workers=10)
    
    for order in new_orders:
        result = executor.submit(create_order,exchange,order)
        print(result)
        
    for order in cancel_orders:
        result = executor.submit(cancel_order, exchange, order)
        
    time.sleep(1) #darle tiempo para que lleguen los mensajes

#checar los balances
def check_balances(order ={}):
    flag = False
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor = db['BALANCES']
    assets = order['symbol'].split('/')
    
    if order['side'] == 'buy':
        amount = order['amount'] * amount['price']
        query = {'asset':assets[1]}
        balance = cursor.find_one(query)
        
        if balance['free'] > amount:
            flag=True
    
    elif order['side'] == 'sell':
        query = {'asset': assets[0]}
        balance = cursor.find_one(query)
        
        if balance['free'] > order['amount']:
            flag=True
    return flag

def create_order(exchange,params_order={}):
    
    if check_balances(order = params_order):
        price,amount = format_price_and_amount(symbol=params_order['symbol'], price= params_order['price'],amount = params_order['order']/params_order['price'])
        params_order['price'] = price
        params_order['amount'] = amount
        
        order = exchange.create_order(
            symbol = params_order['symbol'],
            type = params_order['type'],
            side=params_order['side'],
            price = price,
            amount = amount,
            params = params_order['params'],
        )
def cancel_order(exhange, params_order={}):
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor = db['SYMBOL_INFO']
    query = {'id':params_order['s']}
    symbol_info = cursor.find_one(query)
    
    exhange.cancel_order(symbol = symbol_info['symbol'], id = int(params_order['i']))