import pandas as pd
import numpy as np
from pylab import *
import json
import base64
from math import *
import datetime
import time
import requests

## Set up the authorization

app_token = input('Enter app token: ')
consumer_key = input('Enter consumer key: ')
consumer_secret = input('Enter consumer secret: ')
stubhub_username = input('Enter Stubhub username (email): ')
stubhub_password = input('Enter Stubhub password: ')

## Generating basic authorization token

combo = consumer_key + ':' + consumer_secret
basic_authorization_token = base64.b64encode(combo.encode('utf-8'))

headers = {
        'Content-Type':'application/x-www-form-urlencoded',
        'Authorization':'Basic ' + basic_authorization_token.decode('utf-8'),}
body = {
        'grant_type':'password',
        'username':stubhub_username,
        'password':stubhub_password,
        'scope':'PRODUCTION'}
        
url = 'https://api.stubhub.com/login'
r = requests.post(url, headers=headers, data=body)
token_response = r.json()
access_token = token_response['access_token']
user_GUID = r.headers['X-StubHub-User-GUID']

## Scrape inventory data for the complete list of NBA games

inventory_url = 'https://api.stubhub.com/search/inventory/v2'

headers['Authorization'] = 'Bearer ' + access_token
headers['Accept'] = 'application/json'
headers['Accept-Encoding'] = 'application/json'

## Grab list of game IDs from csv file and convert to Pandas dataframe.

gameid_list_df = pd.read_csv('Path_to_csv_file')
gameid_list_df.drop('Unnamed: 0', axis = 1, inplace = True)

## Remove expired games from list.

bool_list = []

for event_date in gameid_list_df['event_date']:
    if datetime.datetime.strptime(event_date, '%Y-%m-%d') <= datetime.datetime.today():
        bool_list.append(False)
    else:
        bool_list.append(True)

gameid_list_df = gameid_list_df[bool_list]

## Create dataframe with one row filled with zeros; this row will be deleted at the end of the scraping process

aggregate_df = pd.DataFrame([{'game_id':'0', 'event_name':'0', 'home_team':'0', 'away_team':'0', \
                              'venue':'0', 'location':'0', 'event_date':'0', 'quantity':'0', 'snapshot_date':'0', \
                              'current_amount':'0', 'listing_amount':'0', 'listingId':'0','dirtyTicketInd':'0', \
                              'sectionName':'0'}])

## Loop through the list of game IDs

for game_id in gameid_list_df['game_id']:

    eventid = str(game_id)
    data = {'eventid':eventid, 'rows':500}

    inventory = requests.get(inventory_url, headers = headers, params = data)
    inv = inventory.json()
    listings_df = pd.DataFrame(inv['listing'])

    listings_df['current_amount'] = listings_df.apply(lambda x: x['currentPrice']['amount'], axis = 1)
    listings_df['listing_amount'] = listings_df.apply(lambda x: x['listingPrice']['amount'], axis = 1)

    ## Scrape event and venue description for the event of interest

    eventinfo_url = 'https://api.stubhub.com/catalog/events/v3/' + eventid
    eventinfo = requests.get(eventinfo_url, headers = headers)

    info_dict = eventinfo.json()

    game_id = info_dict['id']
    event_name = info_dict['name']
    event_date = info_dict['eventDateLocal'][0:10]
    venue = info_dict['venue']['name']
    location = info_dict['geography']['name']
    home_team = info_dict['performers'][0]['name']
    away_team = info_dict['performers'][1]['name']
    
    ## Capture current date

    snapshot_date = datetime.datetime.today().strftime('%Y-%m-%d_%H')

    ## Create new columns for the listings dataframe

    listings_df['game_id'] = game_id
    listings_df['event_name'] = event_name
    listings_df['home_team'] = home_team
    listings_df['away_team'] = away_team
    listings_df['event_date'] = event_date
    listings_df['snapshot_date'] = snapshot_date
    listings_df['venue'] = venue
    listings_df['location'] = location
    
    ## Create a clean dataframe for the current event in the loop cycle and concatenate to accumulated dataframe.

    df_columns = ['game_id', 'event_name', 'home_team', 'away_team', 'venue', 'location', 'event_date', 'quantity', \
                  'snapshot_date', 'current_amount', 'listing_amount', 'listingId','dirtyTicketInd', 'sectionName']

    listings_df_clean = listings_df[df_columns]

    aggregate_df = pd.concat([aggregate_df, listings_df_clean])

aggregate_df = aggregate_df[aggregate_df.game_id != '0']

## Compute the days to the event and days to end of season for every listing in the aggregate dataframe

event_date_array = array(aggregate_df['event_date'])
snapshot_date_array = array(aggregate_df['snapshot_date'])

days_to_event_list = []
days_to_endofseason_list = []

for i in range(len(aggregate_df)):
    
    delta_1 = datetime.datetime.strptime(event_date_array[i], '%Y-%m-%d') \
    - datetime.datetime.strptime(snapshot_date_array[i], '%Y-%m-%d_%H')
    
    delta_2 = datetime.datetime.strptime('2018-04-11', '%Y-%m-%d') \
    - datetime.datetime.strptime(event_date_array[i], '%Y-%m-%d')
    
    ## Convert timedelta object to number of days and append to list
    
    days_to_event_list.append(delta_1.days + delta_1.seconds/86400)
    days_to_endofseason_list.append(delta_2.days + delta_2.seconds/86400)

## Update dataframe with the new columns 'days_to_event' and 'days_to_endofseason'

aggregate_df['days_to_event'] = days_to_event_list
aggregate_df['days_to_endofseason'] = days_to_endofseason_list

## Save dataframe to csv

aggregate_df.to_csv('Path_to_csv_file'.format(snapshot_date))




