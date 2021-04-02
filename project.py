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
st.write('For geolocation:', 'https://www.kaggle.com/paultimothymooney/latitude-and-longitude-for-every-country-and-state?select=world_country_and_usa_states_latitude_and_longitude_values.csv')
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

#Separate DataFrame for Continents
Covid_Continents_test = Covid.drop(Covid.index[7:])
Covid_Continents = Covid_Continents_test.sort_values(by=['TotalCases'], ascending=False)
Covid_Continents = Covid_Continents.reset_index(drop=True)
Covid_Continents = Covid_Continents.fillna('-')

#Separate DataFrame for Countries
Covid_Countries_test = Covid.drop(Covid.index[0:7])
Covid_Countries = Covid_Countries_test.reset_index(drop=True)
Covid_Countries = Covid_Countries.fillna(0)

#Creating Sidebars for User Input to sort Country dataframe
st.sidebar.header('User Input Features for Countries')
Selected_Continent = st.sidebar.multiselect('Continent', list(sorted(set(Covid_Countries['Continent']))))
Selected_Countries = st.sidebar.multiselect('Country', list(sorted(Covid_Countries['Country,Other'][8:])))
Selected_Attributes = st.sidebar.multiselect('Attribute', list(Covid_Countries.columns[1:]))

#For test tables and graphs
data_continents = pd.DataFrame(Covid_Continents, columns=['Country,Other', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases'])
st.table(data_continents)
st.dataframe(Covid_Countries)

#For taking geolocation(latitude, longitude) for each country
Lat = []
Lon = []
Cou = []

data = pd.read_csv('Coordinates.csv') #Used data from kaggle(link above)
df = pd.DataFrame(data)
Lat = list(df['latitude'])
Lon = list(df['longitude'])
Cou = list(df['country'])

latitude = []
longitude = []

for i in (Covid_Countries['Country,Other']):
    for k, index in enumerate(Cou):
        if i == index:
            latitude.append(Lat[k])
            longitude.append(Lon[k])
        else:
            continue

Covid_Countries['latitude'] = latitude
Covid_Countries['longitude'] = longitude

#SELECTBOX widgets
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
# Run pydeck_chart in streamlit app
map = st.pydeck_chart(r)



