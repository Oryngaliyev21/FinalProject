import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import *
import json
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup

#Block for current time and date
time = datetime.now()
day = date.today()
current_time = time.strftime("%H:%M:%S")
current_day = day.strftime("%B %d, %Y")

#Application title and basic info
st.title('COVID-19 pandemic tracker')
st.write('Data sources:')
st.write('Scrapping webpage:', 'https://www.worldometers.info/coronavirus/')
st.write('For geolocation:', 'https://clck.ru/U5wL4')
st.write('Date when information updated:', current_time, '-', current_day, '(GMT+6)')

#Parser block
url = 'https://www.worldometers.info/coronavirus/'
req = requests.get(url)
page = BeautifulSoup(req.content, 'html.parser')
table = page.find_all('table', id="main_table_countries_today")[0]
Covid_test = pd.read_html(str(table), displayed_only=False)[0]

#Make a pure worksheet without any bugs
Covid = Covid_test.drop(Covid_test.index[[6, 229, 230, 231, 232, 233, 234, 235, 236]])
Covid['Continent'] = Covid['Continent'].replace([None], 'Cruise ship')
Covid = Covid.drop('#', 1)
Covid = Covid.rename(columns={'Country,Other': 'Country'})
Covid['Country'] = Covid['Country'].replace(['Réunion'], ['Reunion'])
Covid['Country'] = Covid['Country'].replace(['Curaçao'], ['Curacao'])

#Separate DataFrame for Continents
Covid_Continents_test = Covid.drop(Covid.index[7:])
Covid_Continents = Covid_Continents_test.sort_values(by=['TotalCases'], ascending=False)
Covid_Continents = Covid_Continents.reset_index(drop=True)
Covid_Continents = Covid_Continents.fillna('-')
Covid_Continents = Covid_Continents.rename(columns={'Country': 'Continents'})

#Separate DataFrame for Countries
Covid_Countries_test = Covid.drop(Covid.index[0:7])
Covid_Countries = Covid_Countries_test.reset_index(drop=True)
Covid_Countries = Covid_Countries.fillna(0)

#For displaying table of World and all continents(except Antarctica) data
st.write("""## Table of World and all continents(except Antarctica) data""")
data_continents = pd.DataFrame(Covid_Continents, columns=['Continents', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases'])
st.table(data_continents)

#For taking geolocation(latitude, longitude) for each country
Coordinates = pd.read_csv('Coordinates.csv') #Used data from kaggle(link above)
df = pd.DataFrame(Coordinates)

Lat = list(df['latitude'])
Lon = list(df['longitude'])
Cou = list(df['country'])

latitude = []
longitude = []

for i in (Covid_Countries['Country']):
    for k, index in enumerate(Cou):
        if i == index:
            latitude.append(Lat[k])
            longitude.append(Lon[k])
        else:
            continue

Covid_Countries['latitude'] = latitude
Covid_Countries['longitude'] = longitude

#Checkboxe for user input features
default_Attributes = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases']
list_of_columns = list(Covid_Countries.columns)
st.write("""## For filtering data""")

if st.checkbox('by Continents'):
    For_Continent = []
    for i in list_of_columns:
        if i != 'Continent' and i != 'Country':
            For_Continent.append(i)

    Selected_Continent = st.multiselect('Continent and Other', list(sorted(set(Covid_Countries['Continent']))))
    Selected_Attributes_for_Continent = st.multiselect('Attribute', For_Continent, default_Attributes)

    Attributes_for_Continent = ['Continent', 'Country']
    for i in Selected_Attributes_for_Continent:
        Attributes_for_Continent.append(i)

    Covid_Countries_filter_test0 = Covid_Countries[Attributes_for_Continent]
    Covid_Countries_filter0 = Covid_Countries_filter_test0[Covid_Countries_filter_test0.Continent.isin(Selected_Continent)]

    st.dataframe(Covid_Countries_filter0)

if st.checkbox('by Countries'):
    Selected_Countries = st.multiselect('Country', list(sorted(Covid_Countries['Country'])))
    Selected_Attributes_for_Countries = st.multiselect('Attribute', list_of_columns[1:], default_Attributes)

    Attributes_for_Countries = ['Country']

    for i in Selected_Attributes_for_Countries:
        Attributes_for_Countries.append(i)

    Covid_Countries_filter_test1 = Covid_Countries[Attributes_for_Countries]
    Covid_Countries_filter1 = Covid_Countries_filter_test1[Covid_Countries_filter_test1.Country.isin(Selected_Countries)]
    st.dataframe(Covid_Countries_filter1)

#Update json file for Advanced WorldMap with our Covid data(TotalCases, TotalDeaths and etc.)
with open('World Map Geo JSON data.json') as f:
    Covid_Json_test = json.load(f)

TC = list(Covid_Countries['TotalCases'])
TD = list(Covid_Countries['TotalDeaths'])
AC = list(Covid_Countries['ActiveCases'])
PP = list(Covid_Countries['Population'])

for i in Covid_Json_test['features']:
    info = i['properties']
    for k, index in enumerate(list(Covid_Countries['Country'])):
        if info.get('name') == index:
            info['TotalCases'] = TC[k]
            info['TotalDeaths'] = TD[k]
            info['ActiveCases'] = AC[k]
            info['Population'] = PP[k]
Covid_Json = json.dumps(Covid_Json_test)

#SELECTBOX widgets for maps
metrics = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests']
cols = st.selectbox('Covid metric to view', metrics)

# let's ask the user which column should be used as Index
if cols in metrics:
    metric_to_show_in_covid_Layer = cols

# Create the plot layer
subheading = st.subheader("Covid-19 distribution Marker Map")

#Load Data for MAPS
Country = Covid_Countries['Country']
lat = Covid_Countries['latitude']
lon = Covid_Countries['longitude']
elevation = Covid_Countries[metric_to_show_in_covid_Layer]

def color_change(elev):
    if(elev < 1000):
        return('green')
    elif(1000 <= elev <10000):
        return('orange')
    else:
        return('red')

map_marker = folium.Map(location=[0,0], zoom_start = 2)

marker_cluster = MarkerCluster().add_to(map_marker)

for lat, lon, elevation, Country in zip(lat, lon, elevation, Country):
    folium.Marker(location=[lat, lon], popup=[Country,elevation], icon=folium.Icon(color = color_change(elevation))).add_to(map_marker)
folium_static(map_marker)

# Create the plot layer
subheading = st.subheader("Covid-19 distribution Heatmap")

#Create base map for Heatmap
map_heat = folium.Map(location=[0,0], zoom_start = 2)
max_totalcases = max(list(Covid_Countries["TotalCases"]))
min_totalcases = min(list(Covid_Countries["TotalCases"]))

#Method to create Choropleth map
popup = GeoJsonPopup(
    fields=['name', 'TotalCases', 'TotalDeaths', 'ActiveCases', 'Population'],
    aliases=['Country:', 'Total Cases:', 'TotalDeaths', 'ActiveCases', 'Population'],
    localize=True,
    labels=True,
    style="background-color: yellow;")
tooltip = GeoJsonTooltip(
    fields=['name', 'TotalCases', 'TotalDeaths', 'ActiveCases', 'Population'],
    aliases=['Country:', 'Total Cases:', 'TotalDeaths', 'ActiveCases', 'Population'],
    localize=True,
    sticky=False,
    labels=True,
    max_width=800)
heatmap = folium.Choropleth(
    geo_data=Covid_Json, data=Covid_Countries,
    name='Covid-19',
    columns=['Country', 'TotalCases'],
    key_on='properties.name',
    bins=[min_totalcases, 10000, 50000, 100000, 300000, 500000, 1000000, 5000000, 15000000, max_totalcases+1],
    fill_color='YlOrRd',
    fill_opacity=0.9, line_opacity=0.6,
    legend_name='Total Cases',
    highlight=True).add_to(map_heat)
folium.GeoJson(
    Covid_Json,
    style_function=lambda feature: {
        'fillColor': '#ffff00',
        'color': 'black',
        'weight': 0.2,
        'dashArray': '5, 5'
    },
    tooltip=tooltip,
    popup=popup).add_to(heatmap)

folium_static(map_heat)
