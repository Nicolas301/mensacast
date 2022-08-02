import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

file = open('mensa_dump.csv', mode='r', encoding='utf-8')

l_id = []
l_canteen = []
l_date = []
l_meal = []
l_price = []
l_vegetarian = []
l_mensaint = []
l_mensaint_country = []
l_dinner = []

isHeader = True
for line in file:
    if isHeader:
        isHeader = False
    else:
        try:
            ID = line[1:line.index(',"')]
            line = line[line.index(',""')+3:]
            canteen_ID = line[0:line.index('""')]
            line = line[line.index('"",""')+5:]
            date = line[0:line.index('""')]
            line = line[line.index('"",""')+5:]
            meal = line[0:line.index('"",')]
            line = line[line.index('"",""')+5:]
            line = line[line.index('"",""')+5:]
            price = line[0:line.index('""')]
            line = line[line.index('"",""')+5:]
            vegetarian = line[0:line.index('""')]
            line = line[line.index('"",""')+5:]
            mensaint = line[0:line.index('""')]
            line = line[line.index('"",')+3:]
            mensaint_country = line[0:line.index(',""')].replace('"','')
            line = line[line.index(',""')+3:]
            dinner = line[0:1]

            l_id.append(ID)
            l_canteen.append(canteen_ID)
            l_date.append(pd.Timestamp(date))
            l_meal.append(meal)
            l_price.append(float(price))
            l_vegetarian.append(int(vegetarian))
            l_mensaint.append(int(mensaint))
            l_mensaint_country.append(mensaint_country)
            l_dinner.append(int(dinner))
        except:
            pass

df = pd.DataFrame({'meal_id': l_id,
                   'canteen_id': l_canteen,
                   'date': l_date,
                   'meal': l_meal,
                   'price': l_price,
                   'is_vegetarian': l_vegetarian,
                   'is_mensa_international': l_mensaint,
                   'mensa_int_country': l_mensaint_country})
df.drop_duplicates(subset = ['date', 'meal', 'canteen_id'], inplace = True) # Mehrfachabfragen raus
df = df.loc[df['canteen_id']=='1'] # Nur Hauptmensa
file.close()

fig, ax = plt.subplots()

ax.plot(np.len(df[:,'price']), df[:,'price'])

st.write('Hier entsteht das DataMining-Projekt MensaCast.')
st.pyplot(fig)
st.write(df.describe())
st.write('Test')
