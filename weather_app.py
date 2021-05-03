import os
from pyowm.utils import weather
from pyowm.utils.formatting import timeformat
import pytz
import pyowm
import streamlit as st
from matplotlib import dates
from datetime import datetime
from matplotlib import pyplot as plt
import requests
import numpy as np


def bar_chart(days, temp_max, temp_min):
    x = np.arange(len(days))
    fig = plt.figure()
    w = 0.2
    plt.bar(x-0.2, temp_max, width = w, color = 'orange')
    plt.bar(x+0.2, temp_min, width = w, color = 'blue')
    plt.xticks(x, days)
    st.pyplot(fig)


def line_chart(days, temp_max, temp_min):
    fig = plt.figure()
    plt.plot(days, temp_max, color = 'orange')
    plt.plot(days, temp_min, color = 'blue')
    st.pyplot(fig)


def tempFormat(temp, unit):
    changed_temperatue = []
    if unit.lower() == 'celsius':
        for t in temp:
            changed_temperatue.append(t - 273.15)
    else:
        for t in temp:
            changed_temperatue.append((t - 273.15) * 9 / 5 + 32)
    return changed_temperatue



def preparedata(daily_weather, unit):
    days = []
    temp_min = []
    temp_max = []
    
    for day, temp in daily_weather.items():
        con_day = datetime.strptime(day, "%Y-%m-%d")
        con_day = con_day.strftime('%m-%d')
        days.append(con_day)
        temp_min.append(float(temp['min']))
        temp_max.append(float(temp['max']))
    temp_max = tempFormat(temp_max, unit)
    temp_min = tempFormat(temp_min, unit)
    return days, temp_max, temp_min
    



def temperature_daily_weather(weather):
    temperature_daily = {}
    list_of_weather = weather['list']
    for daily_weather in list_of_weather:
        date, hour = daily_weather['dt_txt'].split()
        temp_min, temp_max = daily_weather['main']['temp_min'], daily_weather['main']['temp_max']
        if date not in temperature_daily:
            temperature_daily[date] = {'max': temp_max, 'min': temp_min}
        else:
            temperature_daily[date]['max'] = max(temperature_daily[date]['max'], temp_max)
            temperature_daily[date]['min'] = min(temperature_daily[date]['min'], temp_min)
    return temperature_daily


def processing(url, g_type, unit):
    forcast_api = requests.get(url)
    daily_weather_forcast = (temperature_daily_weather(forcast_api.json()))
    days, temp_max, temp_min = preparedata(daily_weather_forcast, unit)
    if g_type.lower() == "bar graph":
        bar_chart(days, temp_max, temp_min)
    else:
        line_chart(days, temp_max, temp_min)

    
def weather_changes(forcaster):
    st.title("Weather Change")
    isRain = forcaster.will_have_rain()
    isStorm = forcaster.will_have_storm()
    isSnow = forcaster.will_have_snow()
    isClear = forcaster.will_have_clear()

    if isRain:
        rainy_weather = forcaster.when_rain()[0].reference_time(timeformat = 'iso')
        icon = forcaster.when_rain()[0].weather_icon_url()
        st.write ("Rainy at ", rainy_weather)
        st.image(icon)
    
    if isStorm:
        stormy = forcaster.when_storm()[0]
        st.write ("Will be stormy at", stormy.reference_time(timeformat = 'iso'))
        st.image (stormy.weather_icon_url())

    if isSnow:
        snow_weather = forcaster.when_snow()[0]
        snow_at = snow_weather.reference_time(timeformat = 'iso')
        st.write("Will be snowy at ", snow_at )
        st.image(snow_weather.weather_icon_url())

    if isClear:
        clear_weather = forcaster.when_clear()[0]
        clear_at = clear_weather.reference_time(timeformat = 'iso')
        st.write("Sky will be clear in ", clear_at)
        st.image(clear_weather.weather_icon_url())
    



owm=pyowm.OWM("4ae36ab46c25e5e4911800d4ec047498")
mgr=owm.weather_manager()

st.title("5 Day Weather Forecast")
st.write("### Write the name of a City and select the Temperature Unit and Graph Type from the sidebar")

place=st.text_input("NAME OF THE CITY :", "")

if place == None:
    st.write("Input a CITY!")
unit = st.selectbox("Select Temperature Unit",("Celsius","Fahrenheit"))
g_type = st.selectbox("Select Graph Type",("Line Graph","Bar Graph"))

url = "http://api.openweathermap.org/data/2.5/forecast?q=" + place + "&appid=4ae36ab46c25e5e4911800d4ec047498"


processing(url, g_type, unit)
forcaster = mgr.forecast_at_place(place, '3h')
print(forcaster)
weather_changes(forcaster)






