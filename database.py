#Enviar los datos que llegan desde el websocket a su colección correspondiente

from turtle import update
import pandas as pd
from pymongo import MongoClient, mongo_client

def update_balances():
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor = db['USER_INFO']
    cursor_balances = db['BALANCES']
    
    #Llamar todos los documentos y convertirlos en un df
    df = pd.DataFrame(list(cursor.find()))
    
    if len(df) > 0:
        df.sort_values('E',ascending=True, inplace=True)
        updates = df['B'].iloc[-1] #última actualización de los balances
        
        for update in updates:
            update['asset'] = update.pop('a')
            update['free'] = update.pop('f')
            update['locked'] = update.pop('l')
            
            query = {'asset':update['asset']}
            cursor_balances.update_one(query,{'$set':update})

        idx = df['_id']
        
        for id in idx:
            query = {'_id':id}
            cursor.delete_one(query)
            

def update_orders():
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor_active_orders =['ACTIVE_ORDERS']
    cursor_historical_orders = db['HISTORICAL_ORDERS']
    
    #llamando ordenes activas 
    df = pd.DataFrame(list(cursor_active_orders.find()))
    
    if len(df) > 0:
        new, filled, canceled = None, None, None
        
        if 'New' in df.value:
            new = df[df['X'] == 'NEW']
            idx = new['i']
            
            amended = []
            for id in idx:
                orders = new[new['i'] == id]
                
                if(len(orders) > 0 ) and (id not in amended):
                    orders = orders.sort_values(by = 'T', ascending=False)
                    orders.drop(orders.index[0], inplace = True)
                    for i in range(len(orders)):
                        query = {'id': orders['_id'].iloc[i]}
                        cursor_active_orders.delete_one(query)
                    amended.append(id)
            del amended,idx,new
        
        if 'FILLED' in df.values:
            filled = df[df['X'] == 'FILLED']
            cursor_historical_orders.insert_many(filled.to_dict('records'))
            idx = filled['i']
            for id in idx:
                query = {'i':id}
                cursor_active_orders.delete_many(query)
            del idx,filled
        
        if 'CANCELED' in df.values:
            canceled = df[df['X'] == 'CANCELED']
            idx = canceled[i]
            for id in idx:
                query={'i':id}
                cursor_active_orders.delete_many(query)
            del idx, canceled
            
def update_database():
    db_client = MongoClient('localhost')
    db = db_client['BINANCE']
    cursor = db['LOGGER']
    
    types = ['order', 'position']
    collections = ['ACTIVE_ORDERS', 'USER_INFO']

    while True:
        for type, collection in zip(types,collections):
            sub_cursor = db[collection]
            query = {'type':type}

            df = pd.DataFrame(list(cursor.find()))
            if len(df) > 0:
                idx = df['_id']
                df.drop(columns=['_id'],inplace=True)
                temp_dict = df.to_dict('records')
                sub_cursor.insert_many(temp_dict)
                
                for id in idx:
                    query = {'_id':id}
                    cursor.delete_one(query)
                update_orders()
                update_balances()
    