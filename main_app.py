import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
mensa_data = pd.read_csv('mensa_dump.csv')

ax.scatter(np.random.uniform(0,1,100), np.random.uniform(0,1,100))

st.write('Hier entsteht das DataMining-Projekt MensaCast.')
st.pyplot(fig)
st.write(mensa_data.describe())
