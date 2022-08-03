import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import fetcher

df = fetch_data()

fig, ax = plt.subplots()

avg_prices = []
date_check = []

for date in df['date'].drop_duplicates(inplace = False):
    res_df = df.loc[(date-pd.DateOffset(days=30)<=df['date'])&(df['date']<=date)]
    if len(res_df.index) > 0:
        avg_prices.append(np.sum(res_df['price'].astype(float))/len(res_df.index))
        date_check.append(date)


ax.plot(np.arange(len(avg_prices)), avg_prices)

st.write('Hier entsteht das DataMining-Projekt MensaCast.')
st.pyplot(fig)
st.write(df.describe())
st.write('Test')
