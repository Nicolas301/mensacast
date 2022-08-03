import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from fetcher import *

df = fetch_data()

fig, ax = plt.subplots()

avg_prices = []
date_check = []

for date in df['date'].drop_duplicates(inplace = False):
    if(data<pd.to_datetime('1/1/2021')):
        continue
    res_df = df.loc[(date-pd.DateOffset(days=30)<=df['date'])&(df['date']<=date)]
    if len(res_df.index) > 0:
        avg_prices.append(np.sum(res_df['price'].astype(float))/len(res_df.index))
        date_check.append(date)


ax.plot(np.arange(len(avg_prices)), avg_prices)

st.write('Hier entsteht das DataMining-Projekt MensaCast.')
st.write('Monatliche Durchschnittspreise seit 2021'):
st.pyplot(fig)
st.write(df.describe())
st.write('Test')
