#import urllib.request
#import json
import requests
import pandas as pd

# Configure API request
# Note limit parameter is arbitrary value greater than total number of NPS sites

my_key = "xawvi79QXSObt8OZUcDBUHPcXLJidAqJAdto1lDY"

pd.options.display.max_columns = 100

def get_park_list(key):

    headers = {"Authorization": key}
    endpoint = "https://developer.nps.gov/api/v1/parks"

    # Sample non-working Python code from
    # https://github.com/nationalparkservice/nps-api-samples/blob/master/park-name-list.py
    #req = urllib.request.Request(endpoint, headers=headers)
    #response = urllib.request.urlopen(req).read()
    #data = json.loads(response.decode('utf-8'))
    #return data

    r = requests.get(endpoint + "?limit=1000" + "&api_key=" + key)
    print("Request status code: " + str(r.status_code))

    data = pd.DataFrame.from_dict(r.json())
    return data

df = get_park_list(my_key)

column_names = ['id', 'park_code', 'name', 'full_name', 'designation', 'description',
                'street', 'city', 'state', 'zipcode', 'lat_long', 'url']
parks_df = pd.DataFrame(columns=column_names)

for park in df['data']:
    print("Adding " + park['fullName'])

    # Get physical address info
    park_addresses = park['addresses']
    try:
        physical_index = next((index for (index, d) in enumerate(park_addresses) if d['type'] == 'Physical'), None)
        physical_address = park_addresses[physical_index]
        street = physical_address['line1']
        city = physical_address['city']
        state = physical_address['stateCode']
        zipcode = physical_address['postalCode']
    except:
        street = None
        city = None
        state = None
        zipcode = None

    # Get park info
    try:
        description = park['description']
    except:
        description = None

    try:
        latlong = park['latLong']
    except:
        latlong = None

    try:
        url = park['url']
    except:
        url = None

    try:
        park_code = park['parkCode']
    except:
        park_code = None

    parks_data = [park['id'], park_code, park['name'], park['fullName'], park['designation'],
                  description, street, city, state, zipcode, latlong, url]
    parks_series = pd.Series(parks_data, index=column_names)
    parks_df = parks_df.append(parks_series, ignore_index=True)

parks_df.to_csv('parks_data.csv', index=False, encoding='utf-8-sig')