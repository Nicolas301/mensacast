import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pandas as pd
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from fetcher import *
import time

def monday():
        return (pd.Timestamp.today() - pd.DateOffset(days=pd.Timestamp.today().weekday())).date()

# Dummytag, um tägliches Neuauslesen zu erzwingen
def effective_day():
        return (pd.Timestamp.today() - pd.DateOffset(hours=6, minutes=30)).date()

@st.cache(allow_output_mutation=True)
def calculate_average_week_prices(beginning_of_week):
        print('Ping')
        iterated_week = pd.Timestamp(beginning_of_week)
        avg_prices = []
        bar_labels = []
        missing_values = 104
        while missing_values > 0:
                iter_distance = missing_values
                missing_values = 0
                for i in range(iter_distance):
                  df_week = df[(iterated_week<=pd.to_datetime(df['date']))&(pd.to_datetime(df['date'])<=(iterated_week+pd.DateOffset(days=5)))]
                  if(df_week['date'].size>0):
                    avg_prices.append(np.mean(df_week['price']))
                    bar_labels.append(f'{iterated_week.strftime("%d.%m.%Y")} - {(iterated_week+pd.DateOffset(days=4)).strftime("%d.%m.%Y")}')
                  else:
                    missing_values += 1
                  iterated_week = iterated_week - pd.DateOffset(days=7)
        
        avg_prices.reverse()
        bar_labels.reverse()
        return np.asarray(avg_prices), np.asarray(bar_labels)

eff_day = effective_day()
df, fetch_date = fetch_data(eff_day)
st.write(f'Datenstand: {fetch_date.strftime("%d.%m.%Y, %X")}.')

mobile_version = st.checkbox('Mobile Ansicht', value=False, help='Macht Grafiken kleiner, die sich nicht automatisch skalieren.')
plot_width = 750*(1-mobile_version)+340*mobile_version
plot_height = 500*(1-mobile_version)+400*mobile_version

st.write('Hier entsteht das DataMining-Projekt MensaCast.')

fig, ax = plt.subplots()

past_weeks = st.slider('Aktuelle Woche und vergangene ... Wochen', min_value = 3, max_value = 103-80*mobile_version, value = 11, step = 1)
if past_weeks == 0:
        past_weeks = 11
if past_weeks > 23 and mobile_version:
        past_weeks = 23

avg_prices, bar_labels = calculate_average_week_prices(monday())

regression = LinearRegression().fit(np.arange(past_weeks+1).reshape(-1,1), avg_prices[(np.size(bar_labels)-past_weeks-1):])

plot_data = pd.DataFrame({'arange_values': np.arange(past_weeks+1),
                          'flip_arange_values': np.flip(np.arange(past_weeks+1)),
                          'avg_prices': avg_prices[(np.size(bar_labels)-past_weeks-1):],
                          'bar_labels': bar_labels[(np.size(bar_labels)-past_weeks-1):],
                          'lin_reg_values': regression.predict(np.arange(past_weeks+1).reshape(-1,1))})

custom_scale = [[0, '#007700'],[.5, '#FFFFAA'],[1, '#AA0000']]
bar_1 = go.Bar(x = plot_data['bar_labels'], y = plot_data['avg_prices'], marker=dict(color=plot_data['arange_values'], colorscale = custom_scale, showlegend = False))
line_1 = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['avg_prices'],line=dict(color="#FFFF00"))
line_2 = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['lin_reg_values'],line=dict(color="#FF0000"))
layout = go.Layout(title="Durchschnittspreise in Euro",title_font_color='#001199')
fig = go.Figure(data=[bar_1,line_1,line_2], layout=layout)
st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
