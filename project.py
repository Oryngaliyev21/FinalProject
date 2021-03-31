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
Covid_test1 = pd.read_html(str(table), displayed_only=False)[0]

#Make a pure worksheet without any bugs
Covid = Covid_test1.drop(Covid_test1.index[[6, 229, 230, 231, 232, 233, 234, 235, 236]])
Covid['Continent'] = Covid['Continent'].replace([None], 'Cruise ship')
Covid = Covid.drop('#', 1)
Covid = Covid.fillna(0)
Covid_Continents = Covid.drop(Covid.index[7:])
Covid_Countries = Covid.drop(Covid.index[0:7])

#Creating Sidebars
st.sidebar.header('User Input Features')
Selected_Continent = st.sidebar.multiselect('Continent', list(sorted(set(Covid_Countries['Continent']))))
Selected_Countries = st.sidebar.multiselect('Country', list(sorted(Covid_Countries['Country,Other'][8:])))
Selected_Attributes = st.sidebar.multiselect('Attribute', list(Covid_Countries.columns[1:]))


