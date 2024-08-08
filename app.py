import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
# from lxml import html
from collections import ChainMap

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


# Create a menu for users to choose up to three countries that they want to see results for. 
options = st.multiselect(
    "What country/countries do you want to know about?",
    list(country_codes.keys()),
    max_selections= 3
)


# Now, return country details for the country the user selected. 

# First, read in the data. 
# pa_data = pd.read_csv('WDPA_Aug2024_Public_csv.csv')
pa_data = pd.read_feather('WDPA_Aug2024_Public.feather')


# Then, we determine what data we want from it. 
# The very first thing is capture the total protected area in a country
country_pa_area = pd.DataFrame()
country_pa_area['total_area'] = pa_data.groupby('ISO3')['GIS_M_AREA'].sum()
country_pa_area.reset_index(inplace = True)
country_pa_area = country_pa_area.to_dict(orient='records')
country_pa_area = {d['ISO3']:d['total_area'] for d in country_pa_area}


# Then we need a function to capture the total acreage of PA in a country
def total_protected_area_calc(row):
    country = row['Country']
    if country_pa_area[country] > 0:
        row["Percent of country's total protected area"] = round((row['Total area in square km']/country_pa_area[country])*100,2)
    return row


# First, we'll get the total area of PAs within a country, organized by status.
status_groups = pa_data.groupby(['ISO3', 'STATUS'])

status_area = pd.DataFrame()
status_area['Total area in square km'] = status_groups['GIS_M_AREA'].sum()
status_area.reset_index(inplace = True)
status_area.rename(columns={'ISO3': 'Country', 'STATUS': 'Protection status'}, 
                   inplace=True)
# Here's where we call on the total acreage of PA so we can calculate percentage
status_area = status_area.apply(total_protected_area_calc, axis=1)

status_area = status_area[['Country', 'Protection status', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by gov_type.
gov_groups = pa_data.groupby(['ISO3', 'GOV_TYPE'])

gov_area = pd.DataFrame()
gov_area['Total area in square km'] = gov_groups['GIS_M_AREA'].sum()
gov_area.reset_index(inplace = True)
gov_area.rename(columns={'ISO3': 'Country', 'GOV_TYPE': 'Governing body'}, 
                   inplace=True)


# Then, we'll get the total area of PAs in a country, organized by owner type.
owner_groups = pa_data.groupby(['ISO3', 'OWN_TYPE'])

owner_area = pd.DataFrame()
owner_area['Total area in square km'] = owner_groups['GIS_M_AREA'].sum()
owner_area.reset_index(inplace = True)
owner_area.rename(columns={'ISO3': 'Country', 'OWN_TYPE': 'Land-owning body'}, 
                   inplace=True)


# Then, we'll get the total area of PAs in a country, organized by IUCN category type.
IUCN_groups = pa_data.groupby(['ISO3', 'IUCN_CAT'])

IUCN_area = pd.DataFrame()
IUCN_area['Total area in square km'] = IUCN_groups['GIS_M_AREA'].sum()
IUCN_area.reset_index(inplace = True)
IUCN_area.rename(columns={'ISO3': 'Country', 'IUCN_CAT': 'IUCN Category'}, 
                   inplace=True)


# Then, we'll get the total area of PAs in a country, organized by verification type.
verif_groups = pa_data.groupby(['ISO3', 'VERIF'])

verif_area = pd.DataFrame()
verif_area['Total area in square km'] = verif_groups['GIS_M_AREA'].sum()
verif_area.reset_index(inplace = True)
verif_area.rename(columns={'ISO3': 'Country', 'VERIF': 'Verification type'}, 
                   inplace=True)


# Then, we'll get the total area of PAs in a country, organized by parent country.
parentiso_groups = pa_data.groupby(['ISO3', 'PARENT_ISO3'])

parentiso_area = pd.DataFrame()
parentiso_area['Total area in square km'] = parentiso_groups['GIS_M_AREA'].sum()
parentiso_area.reset_index(inplace = True)
parentiso_area.rename(columns={'ISO3': 'Country', 'PARENT_ISO3': 'Country with jurisdictional power'}, 
                   inplace=True)


# read the selected option and return the value. 
# using the value (iso3 code), filter the country column and return 
# the rows where the value = the IS03 value from status_area

if options is None:
    status_area
else:
    st.write(f"Sweet. Let's learn about", ' and '.join(options), "!")

# what we want to happen is, in each column, return the table results for a single country. 
# that means, 6 tables in a col with the rows matching a single country (referred to as o)
# search terms is a list of up to 3 country codes that match the options a user selected (of country names)

    cols = st.columns([3, 3, 3, 1])

    # search_terms = []
    for option, col in zip(options, cols): 
        o = country_codes[option]
        return_status_rows = status_area.loc[status_area['Country'] == o]
        return_gov_rows = gov_area.loc[gov_area['Country'] == o]
        return_owner_rows = owner_area.loc[owner_area['Country'] == o]

        with col:
            st.write(f"Results for {option}")
            return_status_rows
            
        # search_terms.append(o)

    # search_terms

#     return_status_rows = status_area.loc[status_area['Country'].isin(search_terms)]
#     return_gov_rows = gov_area.loc[gov_area['Country'].isin(search_terms)]
#     return_owner_rows = owner_area.loc[owner_area['Country'].isin(search_terms)]
#     # return_IUCN_rows = IUCN_area.loc[IUCN_area['Country'] == search_term]
#     # return_verif_rows = verif_area.loc[verif_area['Country'] == search_term]
#     # return_parentiso_rows = parentiso_area.loc[parentiso_area['Country'] == search_term]

# col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

# with col1:
#     st.write("Results for [country 1]")
#     return_status_rows

# with col2:
#     st.write("Results for country 2")
#     return_gov_rows

# with col3:
#     st.write("Results for country 3")
#     return_owner_rows
#     # return_IUCN_rows
#     # return_verif_rows
#     # return_parentiso_rows

