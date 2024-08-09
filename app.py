import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
# from lxml import html
from collections import ChainMap
from PIL import Image


st.set_page_config(
    page_title="WDPA Analysis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={

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

# Establish the order of of columns
status_area = status_area[['Country', 'Protection status', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by gov_type.
gov_groups = pa_data.groupby(['ISO3', 'GOV_TYPE'])

gov_area = pd.DataFrame()
gov_area['Total area in square km'] = gov_groups['GIS_M_AREA'].sum()
gov_area.reset_index(inplace = True)
gov_area.rename(columns={'ISO3': 'Country', 'GOV_TYPE': 'Governing body'}, 
                   inplace=True)

gov_area = gov_area.apply(total_protected_area_calc, axis=1)
gov_area = gov_area[['Country', 'Governing body', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by owner type.
owner_groups = pa_data.groupby(['ISO3', 'OWN_TYPE'])

owner_area = pd.DataFrame()
owner_area['Total area in square km'] = owner_groups['GIS_M_AREA'].sum()
owner_area.reset_index(inplace = True)
owner_area.rename(columns={'ISO3': 'Country', 'OWN_TYPE': 'Land-owning body'}, 
                   inplace=True)

owner_area = owner_area.apply(total_protected_area_calc, axis=1)
owner_area = owner_area[['Country', 'Land-owning body', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by IUCN category type.
IUCN_groups = pa_data.groupby(['ISO3', 'IUCN_CAT'])

IUCN_area = pd.DataFrame()
IUCN_area['Total area in square km'] = IUCN_groups['GIS_M_AREA'].sum()
IUCN_area.reset_index(inplace = True)
IUCN_area.rename(columns={'ISO3': 'Country', 'IUCN_CAT': 'IUCN category'}, 
                   inplace=True)

IUCN_area = IUCN_area.apply(total_protected_area_calc, axis=1)
IUCN_area = IUCN_area[['Country', 'IUCN category', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by verification type.
verif_groups = pa_data.groupby(['ISO3', 'VERIF'])

verif_area = pd.DataFrame()
verif_area['Total area in square km'] = verif_groups['GIS_M_AREA'].sum()
verif_area.reset_index(inplace = True)
verif_area.rename(columns={'ISO3': 'Country', 'VERIF': 'Verification type'}, 
                   inplace=True)

verif_area = verif_area.apply(total_protected_area_calc, axis=1)
verif_area = verif_area[['Country', 'Verification type', 'Total area in square km', "Percent of country's total protected area"]]


# Then, we'll get the total area of PAs in a country, organized by parent country.
parentiso_groups = pa_data.groupby(['ISO3', 'PARENT_ISO3'])

parentiso_area = pd.DataFrame()
parentiso_area['Total area in square km'] = parentiso_groups['GIS_M_AREA'].sum()
parentiso_area.reset_index(inplace = True)
parentiso_area.rename(columns={'ISO3': 'Country', 'PARENT_ISO3': 'Country with jurisdictional power'}, 
                   inplace=True)

parentiso_area = parentiso_area.apply(total_protected_area_calc, axis=1)
parentiso_area = parentiso_area[['Country', 'Country with jurisdictional power', 'Total area in square km', "Percent of country's total protected area"]]


with st.sidebar:
    st.header("Key Descriptions")
    st.subheader("Status")
    st.write("How a protected area is recognized.")
    with st.expander("See more"):
        st.write('''
            *Proposed:* The protected area is in the process of being legally/formally designated.
                It should be noted that sites may sometimes be functioning as protected areas or OECMs while proposed, 
                as the legal processes of designation may take a long time.
                ''')
        st.write('''
            *Inscribed:* This protected area is designated under the World Heritage Convention.
                ''')
        st.write('''
            *Adopted:* This protected area is designated as Specially Protected Area of Marine Importance under the Barcelona Convention.
                ''')
        st.write('''
            *Designated:* This protected area is recognized or dedicated through legal/formal means. 
                This *implies* specific binding commitment to conservation in the long term.
                ''')
        st.write('''
            *Established:* This protected area is recognized or dedicated through other effective means. 
                This implies commitment to conservation outcomes in the long term, but not necessarily with legal or formal recognition.
                ''')
    st.divider()

    st.subheader("Governing body types")
    st.write("The governance type describes the entity responsible and accountable for making decisions about how a protected area is managed.")
    with st.expander("See more"):
        st.write('''
            *Federal or national ministry or agency:* Government at the federal level.
                ''')
        st.write('''
            *Sub-national ministry or agency:* Government at a lower level
                ''')
        st.write('''
            *Government-delegated management:* Management is delegated to another organization (e.g. to a non-governmental organization)
                ''')
        st.write('''
            *Transboundary governance:* Formal arrangements between one or more sovereign States or Territories
                ''')
        st.write('''
            *Collaborative governance:* When governance is through various ways in which diverse actors and institutions work together
                ''')
        st.write('''
            *Joint governance:* For example, pluralist board or other multi-party governing body
                ''')
        st.write('''
            *Individual landowners:* Under the governance of one person, family or trust
                ''')
        st.write('''
            *Non-profit organizations:* For example, non-governmental organizations or universities
                ''')
        st.write('''
            *For-profit organizations:* For example, corporate landowners
                ''')
        st.write('''
            *Indigenous peoples:* Under the governance of indigenous peoples
                ''')
        st.write('''
            *Local communities:* Under the governance of local communities
                ''')
        st.write('''
            *Not Reported:* Governance type is not known
                ''')
    st.divider()

    st.subheader("Land-owning body types")
    st.write("Ownership type is often independent of governance and management structures. It is the individual, organization or group"
             " that holds legal ownership of the land or waters under management.")
    with st.expander("See more"):
        st.write('''
            *State:* Owned by the state
                ''')
        st.write('''
            *Communal:* Under communal ownership
                ''')
        st.write('''
            *Individual landowners:* Owned by individual landowners
                ''')
        st.write('''
            *For-profit organizations:* Owned by for-profit organizations
                ''')    
        st.write('''
            *Non-profit organizations:* Owned by non-profit organizations
                ''')
        st.write('''
            *Joint ownership:* Under the joint ownership of more than one actor, representing more than one accepted value 
                 (e.g. non-profit organizations and for-profit organizations)
                ''')
        st.write('''
            *Multiple ownership:* Different parts of the land and/or waters are owned by different actors, representing more than one accepted value
                ''')
        st.write('''
            *Contested:* Ownership is contested
                ''')
        st.write('''
            *Not Reported:* When ownership type is not known or given by the data provider
                ''')
    st.divider()

    st.subheader("IUCN Categories")
    st.write("The degree to which an area is protected and the kinds of rules in place.")
    with st.expander("See more"):
        st.write('''
        *Ia: Strict Nature Reserve.* This is an area which is protected from all but light human use in order to protect its biodiversity
        and also possibly its geological/geomorphical features.
             ''')
        st.write('''
        *Ib: Wilderness Area.* This is similar to a strict nature reserve, but generally larger and protected in a slightly less stringent manner.
             ''')
        st.write('''
        *II: National Park*. Its main objective is to protect functioning ecosystems, but these areas tend to be more lenient with human visitation
         and its supporting infrastructure. They're managed in a way that may contribute to local economies through promoting educational and recreational
         tourism on a scale that will not reduce the effectiveness of conservation efforts.
             ''')
        st.write('''
        *III: National Monument or Feature.* This is a comparatively smaller area that is specifically allocated to protect a natural monument 
                 and its surrounding habitats. 
             ''')
        st.write('''
        *IV: Habitat or Species Management Area.* This is similar to a natural monument or feature, but focuses on more specific areas of conservation, 
                 like an identifiable species or habitat that requires continuous protection rather than that of a natural feature. 
                 These protected areas will be sufficiently controlled to ensure the maintenance, conservation, and restoration of particular species and habitats
             ''')
        st.write('''
        *V: Protected Landscape or Seascape.* A protected landscape or protected seascape covers a body of land or ocean with an explicit natural conservation plan, 
                 but usually also accommodates a range of for-profit activities.
             ''')
        st.write('''
        *VI: Protected Area with Sustainable Use of Natural Resources.* Though human involvement is a large factor in the management of these protected areas, 
                 developments are not intended to allow for widescale industrial production.  
             ''')
        st.write('''
        *Not Reported.* For protected areas where an IUCN management category is unknown and/or the data provider has not provided any related information.
             ''')
        st.write('''
        *Not Applicable.* The IUCN Management Categories are considered to not be applicable to some designation types. In the WDPA, 
                 this currently applies only to World Heritage Sites and UNESCO MAB Reserves.
             ''')
        st.write('''
        *Not Assigned.* The data provider has chosen not to use the IUCN Protected Area Management Categories.
             ''')
    st.divider()

    st.subheader("Verification types")
    st.write('''
             The body that recognizes the establishment of this protected area and its operations. This matters, because there is there is no body to make sure
             that a protection status is enforced. A state can claim a protected area without an external body checking it. Expert-verified sites have an external
             level of accountability.
             ''')
    with st.expander("See more"):
        st.write('''
        *State:* The site has been verified by the country or territory's national government.
             ''')
        st.write('''    
        *Expert:* The site has been verified by an expert non-government source.
             ''')
        st.write('''
        *Not Reported:* Only applies to sites submitted to the WDPA before the introduction of this attribute. 
                 'Not Reported' indicates that the site has not been through a verification process.
             ''')
    st.divider()

    st.subheader("Parent country")
    st.write('''
             The *parent country* the country that the protected area jurisdictionally resides within. 
             ''')

        
    


# read the selected option and return the value. 
# using the value (iso3 code), filter the country column and return 
# the rows where the value = the IS03 value from status_area


if len(options) == 0:
    image = Image.open('world_pas.png')
    st.image(image)

else:
    st.write(f"Sweet. Let's learn about", ' and '.join(options), "!")

# what we want to happen is, in each column, return the table results for a single country. 

    cols = st.columns([3, 3, 3], gap='large')

    for option, col in zip(options, cols): 
        o = country_codes[option]
        return_status_rows = status_area.loc[status_area['Country'] == o]
        return_gov_rows = gov_area.loc[gov_area['Country'] == o]
        return_owner_rows = owner_area.loc[owner_area['Country'] == o]
        return_IUCN_rows = IUCN_area.loc[IUCN_area['Country'] == o]
        return_verif_rows = verif_area.loc[verif_area['Country'] == o]
        return_parentiso_rows = parentiso_area.loc[parentiso_area['Country'] == o]

        with col:
            st.header(f"Results for {option}")
            st.write("PAs by Status")
            return_status_rows
            st.divider()


            st.write("PAs by Governing type")
            return_gov_rows
            st.divider()


            st.write("PAs by Owner type")
            return_owner_rows
            st.divider()


            st.write("PAs by IUCN category")
            return_IUCN_rows
            st.divider()


            st.write("PAs by Verification type")
            return_verif_rows
            st.divider()


            st.write("PAs by Parent country")
            return_parentiso_rows

