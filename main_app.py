import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fetcher import *

df = fetch_data()

st.write('Hier entsteht das DataMining-Projekt MensaCast.')

fig, ax = plt.subplots()
        
past_weeks = st.slider('Aktuelle Woche und vergangene ... Wochen', min_value = 3, max_value = 51, value = 12, step = 1)
st.write('Durchschnittspreise:')

beginning_of_week = (pd.Timestamp.today() - pd.DateOffset(days=pd.Timestamp.today().weekday())).date()

iterated_week = pd.Timestamp(beginning_of_week)
avg_prices = []
bar_labels = []
for i in range(past_weeks+1):
  df_week = df[(iterated_week<=df['date'])&(df['date']<=(iterated_week+pd.DateOffset(days=5)))]
  bar_labels.append('Test')
  if(df_week['date'].size>0):
    avg_prices.append(np.mean(df_week['price']))
  else:
    avg_prices.append(0)
  iterated_week = iterated_week - pd.DateOffset(days=7)

avg_prices.reverse()

ax = sns.barplot(x=np.arange(past_weeks+1), y=avg_prices)
st.pyplot(fig)
