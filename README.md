# NBA_Tickets_Predictor

StubHub_ticket_scraper.py is a Python script that uses two StubHub APIs to scrape current NBA ticket pricing data for all non-expired games in the 2017-2018 season, excluding playoff games. The game list is obtained from the file "game_id_list_clean.csv". After downloading the csv file, the user should modify Stubhub_ticket_scraper.py on line 49 with the correct path to the downloaded file. Also, line 154 should also be modified with the intended path to the location of the final csv file.

The column descriptions in the clean dataframe are as follows:

game_id: StubHub game id
event_name: e.g. Warriors at Knicks
event_date: game date
venue: name of the venue
location: city where game is played
home_team: the home team
away_team: the away team
snapshot_date: the current date
days_to_event: days remaining until the game
days_to_endofseason: days from the game to the end of the regular season
