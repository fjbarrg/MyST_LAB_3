#primero corrimos:   pip install MetaTrader5 
import MetaTrader5 as mt
import pandas as pd
import numpy as np


def f_login(path, login, password, server):
    connection=mt.initialize(path=meta_path, login=login_account,password=password,server=server_name,portable=False)
    if connection:
        print('funciona')
    else:
        print(mt.last_error())
    return mt

def f_account_info(connection):
    return mt.account_info()._asdict()

def f_leer_archivo(connection, start_date, end_date):
    df_deals=connection.history_deals_get(start_date,end_date)
    df_deals=pd.DataFrame(list(df_deals),columns=df_deals[0]._asdict().keys())
    df_deals['time'] = pd.to_datetime(df_deals['time'], unit='s')
    return df_deals

    #bajar orgers también 
     

   

