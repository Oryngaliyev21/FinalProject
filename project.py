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

#Creating Sidebars
st.sidebar.header('User Input Features')
Selected_Countries = st.sidebar.selectbox('Country', list(sorted(Covid['Country,Other'])))
Selected_Continent = st.sidebar.selectbox('Continent', list(sorted(set(Covid['Continent']))))


