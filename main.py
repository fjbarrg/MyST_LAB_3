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

#metricas de atribución al desempeño
metricas = f.f_evolucion_capital(historico_ariadna)




