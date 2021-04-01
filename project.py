import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

#Application title and basic info
st.title('COVID-19 pandemic tracker')

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
Covid_Continents = Covid_Continents.reset_index()
Covid_Continents = Covid_Continents.drop('index', 1)
Covid_Continents = Covid_Continents.fillna('-')

#Separate DataFrame for Countries
Covid_Countries_test = Covid.drop(Covid.index[0:7])
Covid_Countries = Covid_Countries_test.reset_index()
Covid_Countries = Covid_Countries.drop('index', 1)
Covid_Countries = Covid_Countries.fillna(0)

#Creating Sidebars for User Input to sort Country dataframe
st.sidebar.header('User Input Features')
Selected_Continent = st.sidebar.multiselect('Continent', list(sorted(set(Covid_Countries['Continent']))))
Selected_Countries = st.sidebar.multiselect('Country', list(sorted(Covid_Countries['Country,Other'][8:])))
Selected_Attributes = st.sidebar.multiselect('Attribute', list(Covid_Countries.columns[1:]))

#For test
st.dataframe(Covid_Continents)
st.dataframe(Covid_Countries)

