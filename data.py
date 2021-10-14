import functions as f
from datetime import datetime
import importlib

#conexión
meta_path='C:\Program Files\MetaTrader 5 Terminal\\terminal64.exe'
login_account=5400337
password= 'yKptOu7U'
server_name='FxPro-MT5'
t_out=1000
importlib.reload(f)
#conectamos 
conn=f.f_login(meta_path,login_account,password,server_name)

#descargamos históricos
start_fecha=datetime(2021,9,12)
end_fecha=datetime(2021, 10, 7)
df_historicos=f.f_historicos(conn,start_fecha,end_fecha)

print(df_historicos)
