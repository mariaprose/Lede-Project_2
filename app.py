import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
# from lxml import html

st.set_page_config(
    page_title="WDPA Analysis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("What's the status of protected areas around the world?")

# Here is where we read in the country codes from a website that knows country codes.
# We do this so the user can get a list of all the country names, 
# and so, on the backend, we can keep the ISO3 code to fetch the data.

html_response = requests.get('https://www.iban.com/country-codes')
html = html_response.text
soup = BeautifulSoup(html)

table = soup.select("#myTable > tbody > tr")

country_codes = {}

for country_code in table:
    country = country_code.select("td")[0].get_text()
    iso3_code = country_code.select("td")[2].get_text()

    country_codes[country] = iso3_code


# Create a dropdown menu for user to choose what country they want to see.
option = st.selectbox(
    "What country do you want to know about? ",
    list(country_codes.keys()),
    index=None,
    placeholder="Select contact method...",
)

# Now, return country details for the country the user selected. 

# First, determine the data source and what data we want from it.
pa_data = pd.read_csv('WDPA_Aug2024_Public_csv.csv')
pd.set_option('display.max_columns', None)

status_groups = pa_data.groupby(['ISO3', 'STATUS'])
# pd.set_option('display.max_rows', None)

status_area = pd.DataFrame()
status_area['Total area in square km'] = status_groups['GIS_M_AREA'].sum()
status_area.reset_index(inplace = True)
status_area.rename(columns={'ISO3': 'Country', 'STATUS': 'Protection status'}, 
                   inplace=True)

# status_area

# read the selected option and return the value. 
# using the value (iso3 code), filter the country column and return 
# the rows where the value = the IS03 value from status_area

if option is None:
    status_area
else:
    st.write("Sweet. Let's learn about", option, "!")
    search_term = country_codes[option]
    return_rows = status_area.loc[status_area['Country'] == search_term]

    return_rows