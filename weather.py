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
def get_weather(park, stationid, datasetid, begin_date, end_date, mytoken, base_url):

    token = {'token': mytoken}

    # passing as string instead of dict because NOAA API does not like percent encoding
    # results limited to 1,000 per response (10,000 requests per day) by NOAA
    params = 'datasetid=' + str(datasetid) + '&' + 'stationid=' + str(stationid) + '&' + 'startdate=' + str(
        begin_date) + '&' + 'enddate=' + str(end_date) + '&' + 'limit=1000' + '&' + 'units=standard' + \
             '&' + 'datatypeid=TMAX' + '&' + 'datatypeid=TMIN' + '&' + 'datatypeid=PRCP'

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

# Set constants
base_url_data = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
base_url_stations = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'
datasetid = 'GHCND'

# Load weather station IDs
os.chdir(os.getcwd() + "/data")
stations = pd.read_csv("national_parks_weather_stations.csv")
stations_notna = stations[stations['Weather Station ID'].notna()]
stations_dict = pd.Series(stations_notna['Weather Station ID'].values, index=stations_notna['National Park']).to_dict()

# Get user inputs for token and date range
mytoken = input('Enter your NOAA API token: ')
year = input("Enter year of weather data to obtain: ")
start_date = year + "-01-01"
end_date = year + "-12-31"

# Create empty dataframe to append station weather data to
df = []

# Get weather data per weather station ID
for park, id in stations_dict.items():
    station_weather = get_weather(park, id, datasetid, start_date, end_date, mytoken, base_url_data)

    max_date = str(pd.to_datetime(str(station_weather.tail(1).date.item())).date())
    year = max_date[0:4]
    max_month_day = max_date[5:10]

    while max_date[5:10] != '12-31':
        new_start_date = year + '-' + max_month_day
        more_weather = get_weather(park, id, datasetid, new_start_date, end_date, mytoken, base_url_data)
        station_weather = station_weather.append(more_weather, ignore_index=True)
        max_date = str(pd.to_datetime(str(more_weather.tail(1).date.item())).date())[5:10]
    else:
        continue

    df.append(station_weather)

df = pd.concat(df)

# output to file
df.to_csv('weather_data_' + year + '.csv', index=False)
