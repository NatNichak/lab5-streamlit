import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"
DATA_URL = []
for i in range(1,6):
  data_url_temp = (f"https://raw.githubusercontent.com/Maplub/odsample/master/2019010{i}.csv")
  DATA_URL.append(data_url_temp)

@st.cache(persist=True)
def load_data_start(nrows,day):
    data_start = pd.read_csv(DATA_URL[day-1], nrows=nrows)
    data_start = data_start[['timestart','latstartl','lonstartl']].copy()
    data_start = data_start.rename(columns = {'timestart': 'Date/Time', 'latstartl': 'Lat', 'lonstartl': 'Lon'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    data_start.rename(lowercase, axis="columns", inplace=True)
    data_start[DATE_TIME] = pd.to_datetime(data_start[DATE_TIME],format= '%d/%m/%Y %H:%M')
    return data_start

@st.cache(persist=True)
def load_data_stop(nrows,day):
    data_stop = pd.read_csv(DATA_URL[day-1], nrows=nrows)
    data_stop = data_stop[['timestop','latstop','lonstop']].copy()
    data_stop = data_stop.rename(columns = {'timestop': 'Date/Time', 'latstop': 'Lat', 'lonstop': 'Lon'}, inplace = False)
    lowercase = lambda x: str(x).lower()
    data_stop.rename(lowercase, axis="columns", inplace=True)
    data_stop[DATE_TIME] = pd.to_datetime(data_stop[DATE_TIME],format= '%d/%m/%Y %H:%M')
    return data_stop

# CREATING FUNCTION FOR MAPS

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((1,1))

with row1_1:
    st.title("BKK travelling Data")
    hour_selected = st.slider("Select hour of pickup", 0, 23)

with row1_2:
    st.write(
    """
    ##
    Travelling started and stoped information in BKK between January 1 and January 5, 2019.
   
    by Natnicha Klabdee 6130806221
    """)
    select_date = st.selectbox("Select Date",("01/01/2019", "02/01/2019","03/01/2019","04/01/2019","05/01/2019"))
    date_dict = {"01/01/2019":1,
                 "02/01/2019":2,
                 "03/01/2019":3,
                 "04/01/2019":4,
                 "05/01/2019":5}
    date_day = date_dict[select_date]
# FILTERING DATA BY HOUR SELECTED

datastart = load_data_start(100000,date_day)
datastop = load_data_stop(100000,date_day)

datastart = datastart[(datastart[DATE_TIME].dt.hour == hour_selected)]
datastop = datastop[(datastop[DATE_TIME].dt.hour == hour_selected)]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2 = st.columns((1,1))
midpoint = [13.736717, 100.523186]
with row2_1:
    st.write("**Travelling started information in BKK from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(datastart, midpoint[0], midpoint[1], 11)

with row2_2:
    st.write("**Travelling stoped information in BKK from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    map(datastop, midpoint[0], midpoint[1], 11)


# FILTERING DATA FOR THE HISTOGRAM
filteredstart = datastart[(datastart[DATE_TIME].dt.hour >= hour_selected) & (datastart[DATE_TIME].dt.hour < (hour_selected + 1))]
histstart = np.histogram(filteredstart[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data_start = pd.DataFrame({"minute": range(60), "pickups": histstart})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of travelling started per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data_start)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)

# FILTERING DATA FOR THE HISTOGRAM
filteredstop = datastop[(datastop[DATE_TIME].dt.hour >= hour_selected) & (datastop[DATE_TIME].dt.hour < (hour_selected + 1))]
histstop = np.histogram(filteredstop[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data_stop = pd.DataFrame({"minute": range(60), "arrive": histstop})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of travelling stoped per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data_stop)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("arrive:Q"),
        tooltip=['minute', 'arrive']
    ).configure_mark(
        opacity=0.5,
        color='red'
    ), use_container_width=True)
