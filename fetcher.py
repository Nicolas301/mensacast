import pandas as pd
import streamlit as st

@st.cache
def fetch_data(eff_day):
  df = pd.read_csv('mensa_dump.csv', encoding = 'utf-8')
  df.drop_duplicates(subset = ['date', 'meal'], inplace = True) # Mehrfachabfragen raus
  return df
