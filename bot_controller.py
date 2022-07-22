#Se encargara de manejar los procesos y mantener persistencia con el exchange 

import multiprocessing
import sys
sys.path.append('../')
import pandas as pd
import ccxt 
from pymongo import MongoClient, mongo_client 
from multiprocessing import Process
import time
from decouple import config

from database import update_database
from webdata import run_websockets
from orders import cancel_order, update_orders
from grid_bot import GridBot

class BotController:
    def __init__(self, symbols, strategy):
        self.symbols = symbols
        self.strategy = strategy
        
        self.exchange = ccxt.binance({
        'api_key': config('API_KEY',default=''),
        'secret':config('PRIVATE_KEY',default=''),
        'enableRateLimit': True,
        'timeout': 3000,
        'options':{
            'defaultType': 'spot'
            }
        })

        def bot_runner(self):
            websymbols = [(symbol.repace('/','').lower()) for symbol in self.symbols]
            p1 = Process(target= run_websockets, args=(websymbols, ['depth5']))
            p1.start()
            
            p2 = Process(target=update_database)
            p2.start()
            
            time.sleep(3)
            
            while True:
                try:
                    for symbol in self.symbols:
                        new_orders, cancel_order = self.strategy.get_orders(symbol = symbol)
                        update_orders(exchange= self.exchange, new_orders=new_orders, cancel_orders=cancel_order)
                        
                except Exception as e:
                    print(e)

symbols = ['ETH/BTC']


params = {
    'n_grids': 5,
    'p_grids':0.5,
    's_grids': 1.5
    
}

stragey = GridBot(params=params)
model = BotController(symbols=symbols, strategy=stragey)
model.bot_runner()
