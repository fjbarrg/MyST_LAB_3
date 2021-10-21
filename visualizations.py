import plotly.express as px
import plotly.graph_objects as go

def pie_chart(df_2_ranking):

    labels = df_2_ranking["symbol"].to_list()
    values = df_2_ranking["rank (%)"].to_list()

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0])])
    fig.update_layout(
        title_text="Ranking de las Operaciones de Trading")

    return fig.show()