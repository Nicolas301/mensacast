import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fetcher import *

@st.cache
def calculate_average_week_prices():
        beginning_of_week = (pd.Timestamp.today() - pd.DateOffset(days=pd.Timestamp.today().weekday())).date()

        iterated_week = pd.Timestamp(beginning_of_week)
        avg_prices = []
        bar_labels = []
        for i in range(52):
          df_week = df[(iterated_week<=df['date'])&(df['date']<=(iterated_week+pd.DateOffset(days=5)))]
          bar_labels.append(f'{iterated_week.strftime("%d.%m.%Y")} - {(iterated_week+pd.DateOffset(days=4)).strftime("%d.%m.%Y")}')
          if(df_week['date'].size>0):
            avg_prices.append(np.mean(df_week['price']))
          else:
            avg_prices.append(0)
          iterated_week = iterated_week - pd.DateOffset(days=7)

        return avg_prices, bar_labels

df = fetch_data()

st.write('Hier entsteht das DataMining-Projekt MensaCast.')

fig, ax = plt.subplots()
        
past_weeks = st.slider('Aktuelle Woche und vergangene ... Wochen', min_value = 3, max_value = 51, value = 12, step = 1)
st.write('Durchschnittspreise:')

avg_prices, bar_labels = calculate_average_week_prices()

avg_prices.reverse()
bar_labels.reverse()

ax = sns.barplot(x=bar_labels[:(past_weeks+1)], y=avg_prices[:(past_weeks+1)])
ax.tick_params(labelsize=7)
for label in ax.get_xticklabels():
  label.set_rotation(90)
st.pyplot(fig)
st.write(f'Debugwert: {df.size}')
