# Weather.py
# Purpose: Get daily weather summaries by weather station from the NOAA Weather API
# Station data can be manually validated with the NOAA Climate Data Online Search
# https://www.ncdc.noaa.gov/cdo-web/search

import requests
import pandas as pd
import os

pd.set_option('display.max_columns', None)

# Core datatype IDs (from https://www.ncdc.noaa.gov/cdo-web/datasets):
# PRCP = Precipitation (mm or inches as per user preference, inches to hundredths)
# SNOW = Snowfall (mm or inches as per user preference, inches to tenths)
# SNWD = Snow depth (mm or inches as per user preference, inches)
# TMAX = Maximum temperature (Fahrenheit or Celsius as per user preference)
# TMIN = Minimum temperature (Fahrenheit or Celsius as per user preference)

# Weather data function pulls by station ID and date range
def get_weather(park, stationid, datasetid, begin_date, end_date, mytoken, base_url, request_type):

    token = {'token': mytoken}

    # passing as string instead of dict because NOAA API does not like percent encoding
    # results limited to 1,000 per response (10,000 requests per day) by NOAA
    if request_type == 'maxdate':
        datatypes = ['TMAX']
    else:
        datatypes = ['TMAX', 'TMIN', 'PRCP']
    datatypeids = ''.join('&datatypeid=' + d for d in datatypes)

    params = 'datasetid=' + str(datasetid) + '&' + 'stationid=' + str(stationid) + '&' + 'startdate=' + \
             str(begin_date) + '&' + 'enddate=' + str(end_date) + '&' + 'limit=1000' + '&' + 'units=standard' + \
             datatypeids

    r = requests.get(base_url, params=params, headers=token)
    print("Request status code: " + str(r.status_code))

    try:
        # results comes in json form. Convert to dataframe
        rf = pd.DataFrame.from_dict(r.json()['results'])
        print("Successfully retrieved " + request_type + " for " + str(park))
        dates = pd.to_datetime(rf['date'])
        print("First date retrieved: " + str(dates.iloc[0]))
        print("Last date retrieved: " + str(dates.iloc[-1]) + "\n")

        return rf

    # Catch all exceptions for a bad request or missing data
    except:
        print("Error converting weather data to dataframe. Missing data?")
        pass

# Set constants
base_url_data = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
base_url_stations = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'
datasetid = 'GHCND'

# Load weather station IDs
if os.getcwd()[-4:] != "data":
    os.chdir(os.getcwd() + "/data")
else:
    pass

# Get station IDs to get weather data for
stations = pd.read_csv("national_parks_weather_stations.csv")
stations_notna = stations[stations['Weather Station ID'].notna()]
stations_dict = pd.Series(stations_notna['Weather Station ID'].values, index=stations_notna['National Park']).to_dict()

# Get user inputs for token and date range
mytoken = input('Enter your NOAA API token: ')
year = input("Enter year of weather data to obtain: ")
start_date = year + "-01-01"
end_date = year + "-12-31"

# Create empty dataframe to add station weather data to
df = pd.DataFrame()

# Get weather data per weather station ID
for park, station_id in stations_dict.items():
    station_weather = pd.DataFrame()
    temp_start_date = start_date
    temp_max_date = ''

    dates_df = get_weather(park, station_id, datasetid, start_date, end_date, mytoken, base_url_data, 'maxdate')

    try:
        max_date = str(pd.to_datetime(str(dates_df.tail(1).date.item())).date())

        while temp_max_date != max_date:
            temp_weather = get_weather(park, station_id, datasetid, temp_start_date, max_date, mytoken, base_url_data,
                                       'weather')
            temp_max_date = str(pd.to_datetime(str(temp_weather.tail(1).date.item())).date())
            temp_start_date = temp_max_date
            station_weather = station_weather.append(temp_weather, ignore_index=True)
        else:
            pass

    except:
        pass

    df = pd.concat([df, station_weather], axis=0)

# output to file
df.to_csv('weather_data_' + year + '.csv', index=False)
