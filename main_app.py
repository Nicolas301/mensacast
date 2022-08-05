import streamlit as st
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

st.header('MensaCast')
st.write('Data Mining mit dem Speiseplan der Ilmenauer Hauptmensa.')
st.caption(f'Datenstand: {fetch_date.strftime("%d.%m.%Y, %X")}.')

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
        highlight_veg = st.checkbox('Vegetarische Gerichte hervorheben', value = False)
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
        
        trend = regression.predict(np.array(past_weeks).reshape(-1,1))[0,0]
        st.write(trend)
        
        st.metric('Preistrend',value='',delta=f'{round(100*regression.coef_[0],1)} %'.replace('.',','), delta_color='inverse',help='... im Diagrammzeitraum')

        custom_scale = [[0, '#007700'],[.5, '#FFFFAA'],[1, '#AA0000']]
        if not(use_lines):
                avg_plot = go.Bar(x = plot_data['bar_labels'], y = plot_data['avg_prices'], name='Durchschnitt', marker=dict(color=plot_data['arange_values'], colorscale = 'RdBu'), showlegend = False)
        else:
                avg_plot = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['avg_prices'], name='Durchschnitt', line=dict(color='#0000FF'), showlegend = False)
        lin_reg_plot = go.Scatter(mode = 'lines', x = plot_data['bar_labels'], y = plot_data['lin_reg_values'],line=dict(color="#FF00FF"), name = 'Linearer Trend', showlegend = False)
        layout = go.Layout(title="Durchschnittspreise in Euro:",title_font_color='#001199',hovermode='x')
        fig = go.Figure(data=[avg_plot,lin_reg_plot], layout=layout)
        st.plotly_chart(fig, use_container_width=True, config=dict(displayModeBar=False))
        
with tab3:
        st.write('Dieser Teil der Seite befindet sich noch in Entwicklung!')

with tab4:
        st.write('Dieser Teil der Seite befindet sich noch in Entwicklung!')
        # st.metric


