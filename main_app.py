import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from fetcher import *
import time
import os

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
        missing_values = 52
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

curr_time = time.time()
eff_day = effective_day()
df, fetch_date = fetch_data(eff_day)
st.write(f'Datenstand: {fetch_date.strftime("%d.%m.%Y, %X")}.')

st.write(f'TIMELOG: Datenaktualisierung erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()

st.write('Hier entsteht das DataMining-Projekt MensaCast.')

fig, ax = plt.subplots()
        
past_weeks = st.slider('Aktuelle Woche und vergangene ... Wochen', min_value = 3, max_value = 51, value = 11, step = 1)
if past_weeks == 0:
        past_weeks = 11

st.write('Durchschnittspreise:')

st.write(f'TIMELOG: Technische Vorbereitung erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()

avg_prices, bar_labels = calculate_average_week_prices(monday())

st.write(f'TIMELOG: Durchschnittliche Wochenpreise erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()

regression = LinearRegression().fit(np.arange(past_weeks+1).reshape(-1,1), avg_prices[(np.size(bar_labels)-past_weeks-1):])

st.write(f'TIMELOG: Lineare Regression erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()

plot_data = pd.DataFrame({'arange_values': np.arange(past_weeks+1),
                          'avg_prices': avg_prices[(np.size(bar_labels)-past_weeks-1):],
                          'bar_labels': bar_labels[(np.size(bar_labels)-past_weeks-1):],
                          'lin_reg_values': regression.predict(np.arange(past_weeks+1).reshape(-1,1))})
st.write(f'TIMELOG: DataFrame-Erstellung erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()
sns.barplot(data=plot_data, x='bar_labels', y='avg_prices', ax=ax)
sns.lineplot(data=plot_data, x='bar_labels', y='avg_prices', ax=ax)
sns.lineplot(data=plot_data, x='arange_values', y='lin_reg_values', ax=ax, color='#FF0000')
sns.set_theme(style='whitegrid')
ax.tick_params(labelsize=7)
for label in ax.get_xticklabels():
  label.set_rotation(90)
ax.set_xlabel('')
ax.set_ylabel('')
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter(f'%.2f €'))
st.pyplot(fig)
st.write(f'TIMELOG: Plotten erledigt in {time.time()-curr_time}ms.')
curr_time = time.time()
