import streamline as st
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.scatter(np.random.uniform(0,1,100), np.random.uniform(0,1,100))
st.pyplot(fig)
