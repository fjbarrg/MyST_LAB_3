import functions as f
import importlib

importlib.reload(f) #correr cada que se modifique algo en functions.py

# descargar histórico 
historico_ariadna = f.f_leer_archivo()

# pip_size
EURUSD_pip = f.f_pip_size('EURUSD')

# agregamos columna de tiempo
tiempo = f.f_columnas_tiempos(historico_ariadna) #modificar f.pip_size segun el usuario 

# agregamos columna con los pips
pips_ariadna = f.f_columnas_pips(tiempo)

# diccionarios
estadisticas = f.f_estadisticas_ba(pips_ariadna)

#metricas de atribución al desempeño
metricas = f.f_evolucion_capital(historico_ariadna)

# estadisticas RS
e_desc = f.f_estadisticas_mad(0.05,metricas)

# behavioral finance
ocurrencias, df_anclas = f.f_columnas_pips2(pips_ariadna)


