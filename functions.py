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
    try:
        mt.initialize(login=Users[0], server='FxPro-MT5',password=Passwords[0])
        pip_size = int(0.1/mt.symbol_info(param_ins)._asdict().get('trade_tick_size'))
        return pip_size
    except:
            print(mt.last_error())

def f_columnas_tiempos(param_data):
    param_data['open_time'] = [datetime.fromtimestamp(i) for i in param_data['Time']]
    param_data['close_time'] = [datetime.fromtimestamp(i) for i in param_data['Time.1']]
    param_data['time'] = (param_data['close_time']-param_data['open_time']).apply(timedelta.total_seconds,1)
    return param_data

def f_columnas_pips(param_data):
    param_data['pips'] = [(param_data['Price.1'].iloc[i]-param_data['Price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                if param_data['Type'].iloc[i]== 'buy'
                else (param_data['Price'].iloc[i]-param_data['Price.1'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                for i in range(len(param_data))]
    param_data['pips_acm'] = param_data['pips'].cumsum()
    param_data['profit_acm'] = param_data['Profit'].cumsum()
    return param_data

def f_estadisticas_ba(param_data):
    Ops_totales = len(param_data)
    Ganadoras = len(param_data[param_data['Profit']>=0])
    Ganadoras_c = len(param_data[(param_data['Profit']>=0) & (param_data['Type']=='buy')])
    Ganadoras_v = len(param_data[(param_data['Profit']>=0) & (param_data['Type']!='buy')])
    Perdedoras = len(param_data[param_data['Profit']<0])
    Perdedoras_c = len(param_data[(param_data['Profit']<0) & (param_data['Type']=='buy')])
    Perdedoras_v = len(param_data[(param_data['Profit']<0) & (param_data['Type']!='buy')])
    Mediana_profit = statistics.median(param_data.sort_values(by='Profit')['Profit'])
    Mediana_pips = statistics.median(param_data.sort_values(by='pips')['pips'])
    r_efectividad = Ganadoras/Ops_totales
    r_proporcion = Ganadoras/Perdedoras
    r_efectividad_c = Ganadoras_c/Ops_totales
    r_efectividad_v = Ganadoras_v/Ops_totales
    
    valor = [Ops_totales,Ganadoras,Ganadoras_c,Ganadoras_v,Perdedoras,Perdedoras_c,Perdedoras_v,Mediana_profit,
             Mediana_pips,r_efectividad,r_proporcion,r_efectividad_c,r_efectividad_v]
    df_1_tabla = pd.DataFrame({'medida':['Ops totales','Ganadoras','Ganadoras_c','Ganadoras_v','Perdedoras',
                                         'Perdedoras_c','Perdedoras_v','Mediana(Profit)','Mediana(Pips)',
                                         'r_efectividad','r_proporcion','r_efectividad_c','r_efectividad_v'],
                               'valor':np.round(valor,2),
                               'descripcion':['Operaciones totales','Operaciones ganadoras',
                                              'Operaciones ganadoras de compra','Operaciones ganadoras de venta',
                                              'Operaciones perdedoras','Operaciones perdedoras de compra',
                                              'Operaciones perdedoras de venta','Mediana de profit de operaciones',
                                              'Mediana de pips de operaciones','Ganadoras Totales/Operaciones Totales',
                                              'Ganadoras Totales/Perdedoras Totales',
                                              'Ganadoras Compras/Operaciones Totales',
                                              'Ganadoras Ventas/Operaciones Totales']})
    symbols = param_data['Symbol'].unique()
    df_2_ranking = pd.DataFrame({'symbol':param_data['Symbol'].unique(),
                                 'rank (%)':100*np.round([len(param_data[(param_data['Profit']>0) & 
                                                        (param_data['Symbol']==symbols[i])])/
                                         len(param_data[param_data['Symbol']==symbols[i]]) 
                                         for i in range(len(symbols))],2)
                                })
   
    df_2_ranking = df_2_ranking.sort_values(by='rank (%)',ascending=False).reset_index(drop=True)
    
    return {'df_1_tabla':df_1_tabla,'df_2_ranking':df_2_ranking}