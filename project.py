import requests
import json
import folium
import base64
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import *
from streamlit_folium import folium_static
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
st.write('All data for geolocations we can find in our GitHub repository:', 'https://github.com/Oryngaliyev21/FinalProject')
st.write('Date when information updated:', current_time, '-', current_day, '(GMT+6)')

#Parser block
url = 'https://www.worldometers.info/coronavirus/'
req = requests.get(url)
Covid_test = pd.read_html(req.text, displayed_only=False)[0]

#Make a pure worksheet without any bugs
Covid = Covid_test.drop(Covid_test.index[[6, 229, 230, 231, 232, 233, 234, 235, 236, 237]])
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
Coordinates = pd.read_csv('Coordinates.csv')
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

#Checkboxes for user input features
default_Attributes = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases']
list_of_columns = list(Covid_Countries.columns)

st.write("""## For filtering and showing data""")
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
    Selected_Countries = st.multiselect('Country', list(sorted(Covid_Countries['Country'])), 'Kazakhstan')
    Selected_Attributes_for_Countries = st.multiselect('Attribute', list_of_columns[1:], default_Attributes)

    Attributes_for_Countries = ['Country']

    for i in Selected_Attributes_for_Countries:
        Attributes_for_Countries.append(i)

    Covid_Countries_filter_test1 = Covid_Countries[Attributes_for_Countries]
    Covid_Countries_filter1 = Covid_Countries_filter_test1[Covid_Countries_filter_test1.Country.isin(Selected_Countries)]
    st.dataframe(Covid_Countries_filter1)
if st.checkbox('Distribution Marker Map'):
    # SELECTBOX widgets for maps
    parameters = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests']
    select_p = st.selectbox('Covid metric to view', parameters)

    # Create the plot layer
    subheading = st.subheader("Covid-19 distribution Marker Map")

    # Load Data for MAPS
    Country = Covid_Countries['Country']
    lat = Covid_Countries['latitude']
    lon = Covid_Countries['longitude']
    elevation = Covid_Countries[select_p]


    def color_change(el):
        if el < 1000:
            return 'green'
        elif 1000 <= el < 10000:
            return 'orange'
        else:
            return 'red'


    map_marker = folium.Map(location=[0, 0], zoom_start=2)

    marker_cluster = MarkerCluster().add_to(map_marker)

    for lat, lon, elevation, Country in zip(lat, lon, elevation, Country):
        folium.Marker(location=[lat, lon], popup=[Country, elevation],
                      icon=folium.Icon(color=color_change(elevation))).add_to(map_marker)
    folium_static(map_marker)

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

# Create the plot layer
subheading = st.subheader("Covid-19 distribution Heatmap")

#Create base map for Heatmap
map_heat = folium.Map(location=[0, 0], zoom_start=2)
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
    bins=[min_totalcases, 10**4, 5*10**4, 10**5, 3*10**5, 5*10**5, 10**6, 5*10**6, 15*10**6, max_totalcases+1],
    fill_color='YlOrRd',
    fill_opacity=0.9, line_opacity=0.6,
    legend_name='Total Cases',
    highlight=True).add_to(map_heat)
folium.GeoJson(Covid_Json, style_function=lambda feature: {
    'fillColor': '#ffff00',
    'color': 'black',
    'weight': 0.2,
    'dashArray': '5, 5'},
    tooltip=tooltip,
    popup=popup).add_to(heatmap)

folium_static(map_heat)

#Scraping and filtering data for vaccination plot
Vaccine = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')

empty_df = {}
world_vac_data = pd.DataFrame(empty_df)

for i, item in enumerate(Vaccine.location.tolist()):
    if item == 'World':
        world_vac_data = world_vac_data.append(Vaccine.loc[[i]], ignore_index=True)

date = world_vac_data.date.tolist()
total_vaccinations = world_vac_data.total_vaccinations.tolist()
people_vaccinated = world_vac_data.people_vaccinated.tolist()
people_fully_vaccinated = world_vac_data.people_fully_vaccinated.tolist()

np_date = np.array([np.datetime64(x) for x in date])
np_v = np.array(total_vaccinations)
np_pv = np.array(people_vaccinated)
np_pfv = np.array(people_fully_vaccinated)

world_vac_data = world_vac_data.rename(columns={
    'total_vaccinations': 'Administrated doses',
    'people_vaccinated': 'At least 1 dose',
    'people_fully_vaccinated': 'Fully vaccinated',
    'daily_vaccinations_raw': 'Daily change'
})
for_table_world_vac_data = pd.DataFrame(world_vac_data.tail(1).reset_index(drop=True), columns=['location', 'date', 'Administrated doses', 'At least 1 dose', 'Fully vaccinated', 'Daily change'])

#Simple_plot options
fig = plt.figure()
axes = fig.add_axes([1, 1, 1, 1])
axes.plot(np_date, np_v, 'r', label='total number of doses administered')
axes.plot(np_date, np_pv, 'b', label='total number of people who received at least one vaccine dose')
axes.plot(np_date, np_pfv, 'g', label='total number of people who received all doses')
axes.set_yscale('log')
axes.grid(color='purple', alpha=0.3, linestyle='dashed', linewidth=1)
axes.set_xlabel('Date')
axes.set_ylabel('Vaccination')
axes.set_title('Vaccination statistic')
axes.spines[:].set_color('red')
plt.legend(loc=0)
st.set_option('deprecation.showPyplotGlobalUse', False)

st.write("""
### Today vaccination against Covid-19 Pandemic has his own role and also an important in statistics.""")
st.write(""" """)
st.pyplot()
st.table(for_table_world_vac_data)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Covid-19 Data.csv">Download CSV File</a>'
    return href

st.write("""
### Here you can download preferred dataset in csv format
#### We hope that it will be helpful!""")
dfs = ['World data table', 'Continent data table', 'Country data table', 'Vaccination data']
Ch = st.selectbox('Download one of tables as csv', dfs)

if Ch == 'World data table':
    st.markdown(filedownload(data_continents), unsafe_allow_html=True)
elif Ch == 'Continent data table':
    st.markdown(filedownload(Covid_Countries_filter0), unsafe_allow_html=True)
elif Ch == 'Country data table':
    st.markdown(filedownload(Covid_Countries_filter1), unsafe_allow_html=True)
else:
    st.markdown(filedownload(for_df_world), unsafe_allow_html=True)

st.write("""
## Contact US
#### Please don't hesitate to contact us if you have any questions:
E-mail: 200101059@stu.sdu.edu.kz or 200101053@stu.sdu.edu.kz       
Phone numbers(WhatsApp and Telegram 24/7): +7(707)358-04-06 +7(776)852-52-92
""")
