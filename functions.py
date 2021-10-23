#primero corrimos:   pip install MetaTrader5 
from os import pardir
import MetaTrader5 as mt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from getpass import getpass
import statistics

from pandas.io.sql import DatabaseError


#importar yahoo 
import yfinance as yf   

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

#%% 1.- Estadística Descriptiva
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

def f_columnas_tiempos(pips_ariadna):
    pips_ariadna['open_time'] = [datetime.fromtimestamp(i) for i in pips_ariadna['Time']]
    pips_ariadna['close_time'] = [datetime.fromtimestamp(i) for i in pips_ariadna['Time.1']]
    pips_ariadna['time'] = (pips_ariadna['close_time']-pips_ariadna['open_time']).apply(timedelta.total_seconds,1)
    return pips_ariadna

def f_columnas_pips(pips_ariadna):
    pips_ariadna['pips'] = [(pips_ariadna['Price.1'].iloc[i]-pips_ariadna['Price'].iloc[i])*f_pip_size(pips_ariadna['Symbol'].iloc[i])
                if pips_ariadna['Type'].iloc[i]== 'buy'
                else (pips_ariadna['Price'].iloc[i]-pips_ariadna['Price.1'].iloc[i])*f_pip_size(pips_ariadna['Symbol'].iloc[i])
                for i in range(len(pips_ariadna))]
    pips_ariadna['pips_acm'] = pips_ariadna['pips'].cumsum()
    pips_ariadna['profit_acm'] = pips_ariadna['Profit'].cumsum()
    return pips_ariadna

def f_estadisticas_ba(pips_ariadna):
    Ops_totales = len(pips_ariadna)
    Ganadoras = len(pips_ariadna[pips_ariadna['Profit']>=0])
    Ganadoras_c = len(pips_ariadna[(pips_ariadna['Profit']>=0) & (pips_ariadna['Type']=='buy')])
    Ganadoras_v = len(pips_ariadna[(pips_ariadna['Profit']>=0) & (pips_ariadna['Type']!='buy')])
    Perdedoras = len(pips_ariadna[pips_ariadna['Profit']<0])
    Perdedoras_c = len(pips_ariadna[(pips_ariadna['Profit']<0) & (pips_ariadna['Type']=='buy')])
    Perdedoras_v = len(pips_ariadna[(pips_ariadna['Profit']<0) & (pips_ariadna['Type']!='buy')])
    Mediana_profit = statistics.median(pips_ariadna.sort_values(by='Profit')['Profit'])
    Mediana_pips = statistics.median(pips_ariadna.sort_values(by='pips')['pips'])
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
    symbols = pips_ariadna['Symbol'].unique()
    df_2_ranking = pd.DataFrame({'symbol':pips_ariadna['Symbol'].unique(),
                                 'rank (%)':100*np.round([len(pips_ariadna[(pips_ariadna['Profit']>0) & 
                                                        (pips_ariadna['Symbol']==symbols[i])])/
                                         len(pips_ariadna[pips_ariadna['Symbol']==symbols[i]]) 
                                         for i in range(len(symbols))],2)
                                })
   
    df_2_ranking = df_2_ranking.sort_values(by='rank (%)',ascending=False).reset_index(drop=True)
    
    return {'df_1_tabla':df_1_tabla,'df_2_ranking':df_2_ranking}

#%% Métricas de Atribución al Desempeño

def f_evolucion_capital(param_data):
    param_data['close_time'] = [i.strftime('%Y-%m-%d') for i in param_data['close_time']]
    param_data['close_time_'] = pd.to_datetime(param_data['close_time'])
    df = pd.DataFrame({'close_time_': pd.date_range(start='9/17/2021', end='10/15/2021')})
    df = pd.merge(df, param_data.loc[:, ('close_time_', 'Profit')], how='left', on='close_time_')
    df = df.fillna(0)
    df = df.set_index('close_time_')
    df = df.resample('D').sum()
    df["profit_acm_d"] = df["Profit"].cumsum()
    df["cap_acum"] = df["profit_acm_d"] + 1000000 #se le agrega el capital inicial

    return df

#importar yahoo 
import yfinance as yf

def f_estadisticas_mad(rf, df):
    # Sharpe Ratio Original
    rp = np.log(df.cap_acum) - np.log(df.cap_acum.shift(1))
    rp = rp.fillna(0)
    sdp = rp.std()
    rp_mean = rp.mean()
    rf = (0.05 / 252)
    sharpe_original = (rp_mean - rf) / sdp

    # Sharpe Ratio Actualizado
    # benchmark = pd.read_csv(r'C:\Users\ariad\OneDrive\Documentos\GitHub\MyST_LAB_3\files\SP500.csv')['AdjClose']
    #descargamos S&P500 de yahoo finance
    benchmark = yf.download('^GSPC', '2021-09-17','2021-10-15')
    benchmark = benchmark['Adj Close']
    rp_benchmark = np.log(benchmark) - np.log(benchmark.shift(1))
    rp_benchmark = rp_benchmark.fillna(0)
    rp_benchmark = pd.DataFrame(rp_benchmark)
    benchmark = pd.DataFrame(benchmark)
    rp_benchmark = rp_benchmark.rename(columns={'Adj Close':'cap_acum'})
    rp_rb = pd.concat([benchmark,rp_benchmark], axis=1)
    rp_rb['Rp-Rb'] = rp_rb['cap_acum'] - rp_rb['Adj Close']
    std_sra = rp_rb['Rp-Rb'].std()
    r_trader = rp_rb['cap_acum'].mean()
    r_benchmark = rp_rb['Adj Close'].mean()
    sharpe_actualizado = (r_trader - r_benchmark) / std_sra

    min_ = df.cap_acum.min()
    max_ = df.cap_acum.max()

    # Drawdown
    drawdown_cap = df.profit_acm_d.min()
    date_drawdown = (df.loc[df.profit_acm_d == drawdown_cap].index.values[0])
    date_drawdown = np.datetime_as_string(date_drawdown, unit='D')
    temp = 0
    peak = 0
    du = 0
    b = df.profit_acm_d
    for i in range(len(b)):
        if b[i] < b[i - 1] and b[i] < peak:
            peak = b[i]
            temp = 0

        elif b[i] > b[i - 1]:
            temp = b[i]

        if temp - peak > du:
            du = temp - peak
    # DrawUp
    temp = 0
    peak = 0
    dd = 0
    for i in range(len(b)):
        if b[i] > b[i - 1] and b[i] > peak:
            peak = b[i]
            temp = 0

        elif b[i] < b[i - 1]:
            temp = b[i]

        if temp - peak < dd:
            dd = temp - peak
    
    
    
    drawup_cap = du
    date_drawup = np.datetime_as_string(df.loc[df.cap_acum == min_].index.values[0], unit='D')

    data = [
        ['sharpe_original', 'Cantidad', sharpe_original, "Sharpe Ratio Fórmula Original"],
        ['sharpe_actualizado', 'Cantidad', sharpe_actualizado, "Sharpe Ratio Fórmula Ajustada"],
        ['drawdown_capi', 'Fecha Inicial', date_drawdown, "Fecha inicial del DrawDown de Capital"],
        ['drawdown_capi', 'Fecha Final', date_drawdown, "Fecha final del DrawDown de Capital"],
        ['drawdown_capi', 'Fecha Final', dd, "Máxima pérdida flotante registrada"],
        ['drawup_capi', 'Fecha Inicial', date_drawup, "Fecha inicial del DrawUp de Capital"],
        ['drawup_capi', 'Fecha Final', date_drawup, "Fecha final del DrawUp de Capital"],
        ['drawup_capi', 'Fecha Final', drawup_cap, "Máxima ganancia flotante registrada"]
            ]

    df = pd.DataFrame(data, columns=['metrica', ' ', 'Valor', 'Descripción'])

    return df , dd, drawup_cap

#%% Behavioral Finance

def f_columnas_pips2(param_data):
    param_data['float_pips'] = [(param_data['float_price'].iloc[i]-param_data['Price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                if param_data['Type'].iloc[i]== 'buy'
                else (param_data['Price'].iloc[i]-param_data['float_price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                for i in range(len(param_data))]
    return param_data


def f_be_de_parte1(param_data):
    # Filtrado de operaciones ganadoras (operaciones ancla)
    pips_ariadna['capital_acm'] = pips_ariadna['profit_acm'] + 100000
    ganadoras = pips_ariadna[pips_ariadna.Profit > 0]
    ganadoras = ganadoras.reset_index(drop=True)
    ganadoras["Ratio"] = (ganadoras["Profit"] / abs(ganadoras["profit_acm"]))

    perdedoras = pips_ariadna[pips_ariadna.Profit < 0]
    perdedoras = perdedoras.reset_index(drop=True)
    perdedoras["Ratio"] = (perdedoras["Profit"] / abs(perdedoras["profit_acm"]))

    df_anclas = ganadoras.loc[:, ['close_time', "open_time", 'Type', "Symbol",'Profit', "profit_acm", "capital_acm", "Ratio", "Time", "Time.1", "Price", "Volume"]]                         
    df_anclas = df_anclas.reset_index(drop=True)
    
    # pedir timeframe 

    # Criterio de selección de operaciones abiertas por cada ancla
    ocurrencias = []
    file_list = []
    for x in df_anclas.index:
        df = pips_ariadna[(pips_ariadna.open_time <= df_anclas["close_time"][x]) &
                        (pips_ariadna.close_time > df_anclas["close_time"][x])].loc[:,
             ['Type', 'Symbol', 'Volume', 'Profit', "Price", "pips"]]
        df['close_time_ancla'] = pd.Timestamp(df_anclas['close_time'][x])
        file_list.append(df)
        ocurrencias.append(len(df))
    all_df = pd.concat(file_list, ignore_index=True)

    # Descarga de precios para cada operación abierta
    float_price = []
    if not mt.initialize():
        print(mt.last_error())
        quit()
