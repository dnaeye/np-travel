import requests
import datetime
import numpy as np
import pandas as pd
import os
import sys

pd.set_option('display.max_columns', None)

mytoken = input('Enter your NOAA API token: ')

base_url_data = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
base_url_stations = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'

datasetid = 'GHCND'

begin_date = '2019-01-01'
end_date = '2019-01-31'


def get_weather(park, stationid, datasetid, begin_date, end_date, mytoken, base_url):

    token = {'token': mytoken}

    # passing as string instead of dict because NOAA API does not like percent encoding
    # results limited to 1000 by NOAA
    params = 'datasetid=' + str(datasetid) + '&' + 'stationid=' + str(stationid) + '&' + 'startdate=' + str(
        begin_date) + '&' + 'enddate=' + str(end_date) + '&' + 'limit=1000' + '&' + 'units=standard'

    r = requests.get(base_url, params=params, headers=token)
    print("Request status code: " + str(r.status_code))

    try:
        # results comes in json form. Convert to dataframe
        df = pd.DataFrame.from_dict(r.json()['results'])
        print("Successfully retrieved " + str(park))
        dates = pd.to_datetime(df['date'])
        print("Last date retrieved: " + str(dates.iloc[-1]))

        return df

    # Catch all exceptions for a bad request or missing data
    except:
        print("Error converting weather data to dataframe. Missing data?")


# load weather station IDs
stations = pd.read_csv("national_parks_weather_stations.csv")
stations_notna = stations[stations['Weather Station ID'].notna()]
stations_dict = pd.Series(stations_notna['Weather Station ID'].values, index=stations_notna['National Park']).to_dict()

df = []

# get weather data per weather station ID
for park, id in stations_dict.items():
    station_weather = get_weather(park, id, datasetid, begin_date, end_date, mytoken, base_url_data)
    df.append(station_weather)

df = pd.concat(df)

# output to file
df.to_csv('weather_data.csv')
