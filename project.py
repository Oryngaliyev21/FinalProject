import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import *
import pydeck as pdk

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

#Filtering data by Continents

default_Attributes = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases']
list_of_columns = list(Covid_Countries.columns)

st.write("""## For filtering data by Continents""")
For_Continent = []
for i in list_of_columns:
    if i != 'Continent' and i != 'Country':
        For_Continent.append(i)
Selected_Continent = st.multiselect('Continent and Other', list(sorted(set(Covid_Countries['Continent']))))
Selected_Attributes_for_Continent = st.multiselect('Attribute', For_Continent, default_Attributes)

Attributes_for_Continent = ['Continent', 'Country']

for i in Selected_Attributes_for_Continent:
    Attributes_for_Continent.append(i)

Covid_Countries_filter_test1 = Covid_Countries[Attributes_for_Continent]
Covid_Countries_filter1 = Covid_Countries_filter_test1[Covid_Countries_filter_test1.Continent.isin(Selected_Continent)]
st.dataframe(Covid_Countries_filter1)

#Filtering data by Countries
st.write("""## For filtering data by Countries""")

Selected_Countries = st.multiselect('Country', list(sorted(Covid_Countries['Country'])))
Selected_Attributes_for_Countries = st.multiselect('Attribute', list_of_columns[1:], default_Attributes)

Attributes_for_Countries = ['Country']

for i in Selected_Attributes_for_Countries:
    Attributes_for_Countries.append(i)

Covid_Countries_filter_test = Covid_Countries[Attributes_for_Countries]
Covid_Countries_filter = Covid_Countries_filter_test[Covid_Countries_filter_test.Country.isin(Selected_Countries)]
st.dataframe(Covid_Countries_filter)

#SELECTBOX widgets MAP
metrics = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests']
cols = st.selectbox('Covid metric to view', metrics)

# let's ask the user which column should be used as Index
if cols in metrics:
    metric_to_show_in_covid_Layer = cols
# Set viewport for the deckgl map
view = pdk.ViewState(latitude=0, longitude=0, zoom=0.2, )

# Create the scatter plot layer
covidLayer = pdk.Layer(
    "ScatterplotLayer",
    data=Covid_Countries,
    pickable=False,
    opacity=0.3,
    stroked=True,
    filled=True,
    radius_scale=10,
    radius_min_pixels=5,
    radius_max_pixels=60,
    line_width_min_pixels=1,
    get_position=["longitude", "latitude"],
    get_radius=metric_to_show_in_covid_Layer,
    get_fill_color=[252, 136, 3],
    get_line_color=[255, 0, 0],
    tooltip="test test")

# Create the deck.gl map
r = pdk.Deck(
    layers=[covidLayer],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/light-v10")

subheading = st.subheader("Covid-19 distribution map")

#Run pydeck_chart in Streamlit app
map = st.pydeck_chart(r)


