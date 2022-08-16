import streamlit as st
import scipy.stats as sta
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.linear_model import LinearRegression
from fetcher import *

# Gibt den Montag der aktuellen Woche zurück
def monday():
        return (effective_day() - pd.DateOffset(days=pd.Timestamp.today().weekday())).date()

# Dummytag, um tägliches Neuauslesen zu erzwingen
def effective_day():
        return (pd.Timestamp.today(tz='Europe/Berlin') - pd.DateOffset(hours=6, minutes=30)).date()

def highlight_vegetarian(df, vegetarian_column):
        return ['background-color: #004400' if vegetarian_column.iloc[x] else 'background-color: #440000' for x in np.arange(df.shape[0])]

# Gibt in einem Essensdatenframe die Gerichte zurück, die zeitlich im Intervall [from_including, to_excluding) liegen
def slice_time(data, from_including, to_excluding=None):
        if to_excluding is not None:
                return data.loc[[(pd.to_datetime(date) >= pd.to_datetime(from_including)) & (pd.to_datetime(date) < pd.to_datetime(to_excluding)) for date in data['date']]]
        else:
                return data.loc[[pd.to_datetime(date) >= pd.to_datetime(from_including) for date in data['date']]]

@st.cache
def past_day_numbers(day):
        number_past_days = slice_time(df, day-pd.DateOffset(months=12), effective_day()-pd.DateOffset(months=3))['date'].shape[0]
        number_present_days = slice_time(df, day-pd.DateOffset(months=3))['date'].shape[0]
        return number_past_days, number_present_days

@st.cache(allow_output_mutation=True)
def calculate_average_week_prices(beginning_of_week):
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

number_past_days, number_present_days = past_day_numbers(effective_day())

st.header('MensaCast')
st.write(f'Datenstand: {fetch_date.strftime("%d.%m.%Y")}.')
st.caption('Build 2, Stand: 16. August 2022') # Vorher: Build 1, Stand: 8. August 2022

tab1, tab2, tab3, tab4 = st.tabs(['Speiseplan', 'Durchschnittspreise', 'Komponentensuche', 'Statistiken'])

with tab1:
        today_index = pd.Timestamp.today(tz='Europe/Berlin').weekday()
        weekday_labels = []
        weekday_labels.append(f'Montag, {(pd.to_datetime(monday())).strftime("%d.%m.%Y")}')
        weekday_labels.append(f'Dienstag, {(pd.to_datetime(monday()) + np.timedelta64(1,"D")).strftime("%d.%m.%Y")}')
        weekday_labels.append(f'Mittwoch, {(pd.to_datetime(monday()) + np.timedelta64(2,"D")).strftime("%d.%m.%Y")}')
        weekday_labels.append(f'Donnerstag, {(pd.to_datetime(monday()) + np.timedelta64(3,"D")).strftime("%d.%m.%Y")}')
        weekday_labels.append(f'Freitag, {(pd.to_datetime(monday()) + np.timedelta64(4,"D")).strftime("%d.%m.%Y")}')
        selected_weekday = st.selectbox('Wochentag', weekday_labels,index=min(today_index,4))
        highlight_veg = st.checkbox('Vegetarische Gerichte hervorheben', value = False, help = 'In einigen Fällen werden Gerichte vom Studierendenwerk fälschlich als vegetarisch oder nicht-vegetarisch eingeordnet. Dies ist kein Fehler dieser Webseite.')
        start_of_day = pd.to_datetime(monday())
        if selected_weekday == weekday_labels[1]:
                start_of_day = pd.to_datetime(monday()) + np.timedelta64(1,'D')
        elif selected_weekday == weekday_labels[2]:
                start_of_day = pd.to_datetime(monday()) + np.timedelta64(2,'D')
        elif selected_weekday == weekday_labels[3]:
                start_of_day = pd.to_datetime(monday()) + np.timedelta64(3,'D')
        elif selected_weekday == weekday_labels[4]:
                start_of_day = pd.to_datetime(monday()) + np.timedelta64(4,'D')
        end_of_day = start_of_day + np.timedelta64(1,'D')
        df_current_day = df[(pd.to_datetime(df['date']) >= start_of_day) & (pd.to_datetime(df['date']) < end_of_day)].drop(columns=['id','date']).rename(columns={'meal': 'Essen', 'price': 'Preis', 'is_vegetarian': 'Vegetarisch'})
        df_current_day.set_index(np.arange(1,df_current_day.shape[0]+1),inplace=True)
        df_current_day.sort_values(by='Preis', inplace = True)
        vegetarian_column = df_current_day['Vegetarisch']
        df_style = df_current_day.style.format({'Preis': '{:.2f}€'}, decimal = ',')
        if highlight_veg:
                df_style = df_style.apply(highlight_vegetarian, vegetarian_column = vegetarian_column, axis = 0)
        df_current_day.drop(columns=['Vegetarisch'], inplace=True)
        st.table(df_style)


with tab2:
        past_weeks = st.slider('Aktuelle Woche und vergangene ... Wochen', min_value = 3, max_value = 103, value = 11, step = 1)
        
        use_lines = st.checkbox('Durchschnittspreise als Linien- statt Balkendiagramm darstellen', value = False)

        avg_prices, bar_labels = calculate_average_week_prices(monday())

        regression = LinearRegression().fit(np.arange(past_weeks+1).reshape(-1,1), avg_prices[(np.size(bar_labels)-past_weeks-1):])

        plot_data = pd.DataFrame({'arange_values': np.arange(past_weeks+1),
                                  'flip_arange_values': np.flip(np.arange(past_weeks+1)),
                                  'avg_prices': avg_prices[(np.size(bar_labels)-past_weeks-1):],
                                  'bar_labels': bar_labels[(np.size(bar_labels)-past_weeks-1):],
                                  'lin_reg_values': regression.predict(np.arange(past_weeks+1).reshape(-1,1))})
        
        trend = regression.predict(np.array(past_weeks).reshape(-1,1))[0]/regression.predict(np.array(0).reshape(-1,1))[0]
        trend = np.power(trend,1/(past_weeks+1))-1
        st.metric('Wöchentlicher Preistrend',value='',delta=f'{round(100*trend,1)} %'.replace('.',','), delta_color='inverse',help='... basierend auf den Daten im Diagrammzeitraum')

        custom_scale = [[0, '#007700'],[.5, '#FFFFAA'],[1, '#AA0000']]
        if not(use_lines):
                avg_plot = go.Bar(x = plot_data['bar_labels'], y = plot_data['avg_prices'], name='Durchschnitt', marker=dict(color=plot_data['arange_values'], colorscale = 'RdBu'), showlegend = False)
        else:
                avg_plot = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['avg_prices'], name='Durchschnitt', line=dict(color='#0000FF'), showlegend = False)
        lin_reg_plot = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['lin_reg_values'],line=dict(color="#FF00FF"), name = 'Linearer Trend', showlegend = False)
        layout = go.Layout(title="Durchschnittspreise in Euro:",title_font_color='#00AAFF',hovermode='x')
        fig = go.Figure(data=[avg_plot,lin_reg_plot], layout=layout)
        st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
        
with tab3:
        # Schlüssel wird angezeigt, Wert wird intern verwendet
        # 0: verwende Schlüssel als Wert
        # einzelner Wert: ersetze Schlüssel durch Wert
        # Liste von Werten: Werte sind gleichbedeutend
        component_dict = {'Pommes': ['Pommes', 'Twister'], 'Reis': 0, 'Soja': 0, 'Tofu': 0, 'Ananas': 0, 'Schnitzel': 0, 'Nudeln': ['Nudel','Spirelli','Spaghetti'],
                          'Suppe': 0, 'Kartoffeln': 'Kartoffel', 'Käse': ['Mozzarella','Käse'], 'Auflauf': 0, 'Brötchen': 0, 'Schwein': 0, 'Steak': 0,
                          'Erbsen': 'Erbse', 'Couscous': 0, 'Chili': 0, 'Tzatziki': 0, 'Lachs': 0, 'Pute': 0, 'Salat': 0,
                          'Blumenkohl': 0, 'Linsen': 'Linse', 'Soße': ['Soße', 'Sosse'], 'Wokgerichte': 'Wok', 'Pilze': ['Pilz','Champignon'],
                          'Huhn': ['Hähnchen', 'Huhn', 'Hühner'], 'Rind': 0, 'Curry': 0, 'Gulasch': 0, 'Sauerkraut': 0,
                          'Gyros': 0, 'Rostbrätel': 0, 'Bratwurst': 0, 'Tomaten': 'Tomate', 'Minestrone': 0,
                          'Rotkohl': 0, 'Frikadelle': 0, 'Puffer': 'Puffer', 'Mozzarellasticks': 0,
                          'Shake': 0, 'Falafel': 0, 'Nuggets': 0, 'Eintopf': 0, 'Rührei': 0, 'Kartoffeltaschen': 0, 'Spinat': 0, 'Klöße': ['Klöße', 'Kloß']}
        
        selected_components = st.multiselect('Komponentenkombination', sorted(list(component_dict.keys())))
        
        # Preprocessing
        sliced_df = slice_time(df,effective_day()-pd.DateOffset(months=12))
        sel_df = sliced_df.copy()
        sel_df['meal'] = sel_df['meal'].str.lower().str.replace('strindberg','')
        for sel_comp in selected_components:
                val = component_dict[sel_comp]
                if type(val) is int:
                        val = sel_comp
                elif type(val) is list:
                        sublist = val[1:]
                        val = val[0]
                        for replace_string in sublist:
                                sel_df['meal'] = sel_df['meal'].str.replace(replace_string.lower(), val.lower())
                sel_df = sel_df[[val.lower() in x for x in sel_df['meal']]]
        sel_df = df[[index in sel_df.index for index in df.index]]
        sel_df_past = slice_time(sel_df, effective_day()-pd.DateOffset(months=12), effective_day()-pd.DateOffset(months=3))
        sel_df_present = slice_time(sel_df, effective_day()-pd.DateOffset(months=3))
        st.write(f'Zahl der Gerichte in den letzten drei Monaten: {number_present_days}')
        
        if sel_df_past.shape[0] == 0:
                delta = '0,0 %'
        else:
                delta = f'{round(((sel_df_present.shape[0]/number_present_days)/(sel_df_past.shape[0]/number_past_days)-1)*100,1)} %'.replace('.',',')
        
        st.metric('Häufigkeit in den letzten drei Monaten', sel_df_present.shape[0], delta=delta,help='... und relative Häufigkeit der Komponentenkombination in den letzten drei Monaten verglichen mit den neun Monaten davor')
        
        if sel_df.shape[0] > 0:
                st.write('Letzte fünf Gerichte mit dieser Komponentenkombination in den letzten zwölf Monaten:')
                if sel_df.shape[0] > 5:
                        sel_df = sel_df.iloc[sel_df.shape[0]-5:]
                sel_df = sel_df.drop(columns=['id','is_vegetarian']).rename(columns={'date': 'Datum', 'meal': 'Essen', 'price': 'Preis'})
                sel_df.set_index(np.arange(1,sel_df.shape[0]+1),inplace=True)
                sel_df['Datum'] = pd.to_datetime(sel_df['Datum'])
                sel_df_style = sel_df.style.format({'Preis': '{:.2f}€', 'Datum': '{:%d.%m.%Y}'}, decimal = ',')
                st.table(sel_df_style)


with tab4:
        st.write('Dieser Teil der Seite befindet sich noch in Entwicklung!')
        st.write('Alle Statistiken beziehen sich auf die letzten drei Monate. Alle Entwicklungsindikatoren beziehen sich auf diesen Zeitraum verglichen mit den neun Monaten davor.')
        sel_df_past = slice_time(df, effective_day()-pd.DateOffset(months=12), effective_day()-pd.DateOffset(months=3))
        sel_df_present = slice_time(df, effective_day()-pd.DateOffset(months=3))
        avg_present = sel_df_present.shape[0]/pd.unique(sel_df_present['date']).shape[0]
        avg_past = sel_df_past.shape[0]/pd.unique(sel_df_past['date']).shape[0]
        st.metric('Durchschnittliche Zahl der Gerichte', str(round(avg_present,1)).replace('.',','), delta = f'{round(100*(avg_present/avg_past-1),1)} %'.replace('.',','))
