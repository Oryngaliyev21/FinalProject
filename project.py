import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import *
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import numpy as np

#Block for current time and date
time = datetime.now()
day = date.today()
current_time = time.strftime("%H:%M:%S")
current_day = day.strftime("%B %d, %Y")

#Application title and basic info
st.title('COVID-19 pandemic tracker')
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
st.sidebar.header('User Input Features')
Selected_Continent = st.sidebar.multiselect('Continent', list(sorted(set(Covid_Countries['Continent']))))
Selected_Countries = st.sidebar.multiselect('Country', list(sorted(Covid_Countries['Country,Other'][8:])))
Selected_Attributes = st.sidebar.multiselect('Attribute', list(Covid_Countries.columns[1:]))

#For test tables and graphs
data_continents = pd.DataFrame(Covid_Continents, columns=['Country,Other','TotalCases','NewCases','TotalDeaths','NewDeaths','TotalRecovered','NewRecovered','ActiveCases'])
st.table(data_continents)
st.dataframe(Covid_Countries)

df1 = pd.DataFrame(Covid_Continents, columns=['TotalCases','NewCases','TotalDeaths','NewDeaths','TotalRecovered','NewRecovered','ActiveCases'])
df2 = pd.DataFrame(Covid_Countries)
#st.bar_chart(df1)
#st.line_chart(df2)

#Part to find coordinates for each country
longitude = []
latitude = []

def findGeocode(country):
    try:
        geolocator = Nominatim(user_agent="your_app_name")
        return geolocator.geocode(country)
    except GeocoderTimedOut:
        return findGeocode(country)

for i in (df2["Country,Other"]):
    if findGeocode(i)!=None:
        loc = findGeocode(i)
        latitude.append(loc.latitude)
        longitude.append(loc.longitude)
    else:
        latitude.append(np.nan)
        longitude.append(np.nan)
df2["longitude"] = longitude
df2["latitude"] = latitude
st.map(df2[["latitude","longitude"]])