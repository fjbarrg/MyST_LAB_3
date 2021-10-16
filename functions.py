#primero corrimos:   pip install MetaTrader5 
from os import pardir
import MetaTrader5 as mt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from getpass import getpass
import statistics

from pandas.io.sql import DatabaseError

def f_account_info(connection):
    return mt.account_info()._asdict()


def f_leer_archivo():
    #del archivo donde estan los datos de inicio de sesión
    param_archivo = pd.read_csv(r'C:\Users\ariad\OneDrive\Documentos\GitHub\MyST_LAB_3\files\cuentas.csv')
    Names = list(param_archivo['Name'])
    Users = list(param_archivo['Account'])
    Passwords = list(param_archivo['Password'])
    
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


def f_pip_size(param_ins):
    param_archivo = pd.read_csv(r'C:\Users\ariad\OneDrive\Documentos\GitHub\MyST_LAB_3\files\cuentas.csv')
    Names = list(param_archivo['Name'])
    Users = list(param_archivo['Account'])
    Passwords = list(param_archivo['Password'])
    print('Los nombres son:',Names)
    Name = input('Ingrese nombre del integrante a analizar: ')
    #iniciar conexión con MT5
    if Name in Names:
        if Name == 'Ariadna':
            a = mt.initialize(login=Users[0], server='FxPro-MT5',password=Passwords[0])
            pip_size = int(0.1/mt.symbol_info(param_ins)._asdict().get('trade_tick_size'))
        #Javier
        else:
            a = mt.initialize(login=Users[1], server='FxPro-MT5',password=Passwords[1])
            pip_size = int(0.1/mt.symbol_info(param_ins)._asdict().get('trade_tick_size'))
    else:
        print(mt.last_error())
    return pip_size

def f_columnas_tiempos(param_data):
    param_data['open_time'] = [datetime.fromtimestamp(i) for i in param_data['Time']]
    param_data['close_time'] = [datetime.fromtimestamp(i) for i in param_data['Time.1']]
    param_data['time'] = (param_data['close_time']-param_data['open_time']).apply(timedelta.total_seconds,1)
    return param_data

#def f_columnas_pips(param_data):
 #   param_data = [param_data['Price.1'].iloc[i]-param_data['Price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
  #              if param_data['Type'].iloc[i]== 'buy'
   #             else (param_data['Price'].iloc[i]-param_data['Price.1'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
    #            for i in range]