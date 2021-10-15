#primero corrimos:   pip install MetaTrader5 
import MetaTrader5 as mt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from getpass import getpass
import statistics

from pandas.io.sql import DatabaseError


def f_login(path, login, password, server):
    connection=mt.initialize(path=meta_path, login=login_account,password=password,server=server_name,portable=False)
    if connection:
        print('funciona')
    else:
        print(mt.last_error())
    return mt

def f_account_info(connection):
    return mt.account_info()._asdict()

#def f_leer_archivo(connection, start_date, end_date):
#    df_deals=connection.history_deals_get(start_date,end_date)
 #   df_deals=pd.DataFrame(list(df_deals),columns=df_deals[0]._asdict().keys())
  #  df_deals['time'] = pd.to_datetime(df_deals['time'], unit='s')
   # return df_deals

    #bajar orders también


def f_leer_archivo():
    #del archivo donde estan los datos de inicio de sesión
    Accounts = pd.read_csv(r'C:\Users\ariad\OneDrive\Documentos\GitHub\MyST_LAB_3\files\cuentas.csv')
    Names = list(Accounts['Name'])
    Users = list(Accounts['Account'])
    Passwords = list(Accounts['Password'])
    
    print('Los nombres son:',Names)
    Name = input('Ingrese nombre del integrante a analizar: ')
    #iniciar conexión con MT5
    if Name in Names:
        if Name == 'Ariadna':
            a = mt.initialize(login=Users[0], server='FxPro-MT5',password=Passwords[0])
        #Javier
        else:
            a = mt.initialize(login=Users[1], server='FxPro-MT5',password=Passwords[1])
    else:
        print('El nombre no fue válido, intente de nuevo')
    #creación de DataFrame
    if a:
        print('Se inició sesión con éxito')
        df_deals = mt.history_deals_get(datetime(2021,1,12),datetime.now())
        df_deals=pd.DataFrame(list(df_deals),columns=df_deals[0]._asdict().keys())

        Dates = pd.DataFrame({'Position': df_deals['position_id'].unique()})
        opentime = []
        closetime = []
        price_o = []
        price_c = []
        for i in df_deals['position_id'].unique():
            dates = np.array(df_deals['time'][df_deals['position_id']==i])
            prices = np.array(df_deals['price'][df_deals['position_id']==i])
            if len(dates)==2:
                opentime.append(dates[0])
                closetime.append(dates[1])
                price_o.append(prices[0])
                price_c.append(prices[1])
            else:
                opentime.append(dates[0])
                closetime.append(0)
                price_o.append(prices[0])
                price_c.append(prices[-1])
        Dates['Time'] = opentime
        Dates['Symbol'] = [np.array(df_deals['symbol'][df_deals['position_id']==i])[0] 
        for i in df_deals['position_id'].unique()]
        type_op = [np.array(df_deals['type'][df_deals['position_id']==i])[0] 
        for i in df_deals['position_id'].unique()]
        Dates['Type'] = ['buy' if i == 0 else 'sell' for i in type_op]
        Dates['Volume'] = [np.array(df_deals['volume'][df_deals['position_id']==i])[0] 
        for i in df_deals['position_id'].unique()]
        Dates['Price'] = price_o
        Dates['Time.1'] = closetime
        Dates['Price.1'] = price_c
        Dates['Commission'] = [np.array(df_deals['commission'][df_deals['position_id']==i])[-1] 
        for i in df_deals['position_id'].unique()]
        Dates['Swap'] = [np.array(df_deals['swap'][df_deals['position_id']==i])[-1]
        for i in df_deals['position_id'].unique()]
        Dates['Profit'] = [np.array(df_deals['profit'][df_deals['position_id']==i])[-1] 
        for i in df_deals['position_id'].unique()]
        Dates = Dates[Dates['Time.1']!=0]

        return Dates.sort_values(by='Time.1',ascending=True).reset_index(drop=True)

    else:
        print(mt.last_error())

