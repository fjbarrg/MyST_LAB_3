#importamos librerias 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import functions as f

def ranking_graph(param_data):
    fig = go.Figure(data=[go.Pie(labels=param_data['symbol'], values=param_data['rank (%)'],
                                 pull=[0.1]+[0]*(len(param_data)-1))])
    fig.update_layout(title_text="rank (%)")
    return fig.show()


def drawdown_drawup_graf(param_data, param: bool = True):
    if param:
        metrica = f.f_evolucion_capital(param_data)
        e_desc, drawdown, drawup = f.f_estadisticas_mad(0.05,metrica)
        to_index = list(metrica["close_time_"].apply(str))
        date_ind_dd = str(pd.Timestamp(drawdown.iloc[0, -2][0]))
        ind_dd = to_index.index(date_ind_dd)
        drawdown_cap = [float(metrica.iloc[ind_dd - i, -1]) for i in [2, 1, 0]]
        drawdown_dates = [metrica.iloc[ind_dd - i, 0] for i in [2, 1, 0]]
        date_ind_du = str(pd.Timestamp(drawup.iloc[0, -2][0]))
        ind_du = to_index.index(date_ind_du)
        drawup_cap = [float(metrica.iloc[ind_du - i, -1]) for i in [2, 1, 0]]
        drawup_dates = [metrica.iloc[ind_du - i, 0] for i in [2, 1, 0]]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=metrica['timestamp'], y=metrica['profit_acm_d'], mode='lines',
                                 name='Profit diario', line=dict(color='black')))
        # Drawdown
        fig.add_trace(go.Scatter(x=drawdown_dates, y=drawdown_cap,
                                 mode='lines', name='Drawdown', line=dict(color="crimson", width=4, dash="dashdot",)))
        # Drawup
        fig.add_trace(go.Scatter(x=drawup_dates, y=drawup_cap,
                                 mode='lines', name='Drawdup', line=dict(color="LightSeaGreen", width=4, dash="dashdot",)))
        fig.update_layout(title="Drawdown y Drawup", xaxis_title="Fechas", yaxis_title="Profit acumulado")
        return fig.show()

