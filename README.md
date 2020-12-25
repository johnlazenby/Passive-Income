# DraftKings

The goal of this project is to make money playing fantasy basketball on draftkings in a completely automated manner. Running one script, `scraping_and_entering.py` collects fantasy point projections for players playing in today's games, creates the optimal lineup based on those projections, uploads this lineup to draftkings, and enters a contest with the lineup. Currently the player projections are scraped from https://www.numberfire.com. 

The following inputs are required and should be specified in a file, `scraping_and_entering_inputs.env`:
1. nf_username: username for a yahoo account that is signed up for numberfire (https://www.numberfire.com/)
2. nf_password: password for a yahoo account that is signed up for numberfire (https://www.numberfire.com/)
3. dk_username: username for draftkings account
4. dk_password: password for draftkings account
5. downloads_path: full file path to location chrome downloads to
6. contest_title: name of title of contest program will enter

Example of a `scraping_and_entering_inputs.env` file: <br>

```
nf_username="email@yahoo.com"
nf_password='cool_password'
dk_username='email@gmail.com'
dk_password='another_cool_password'
downloads_path='/Users/joesmith/Downloads'
contest_title="NBA Single Entry $5 Double Up"
```

## To Do 
* fix absolute path in upload and enter
* change path to chromedriver
* look into why there was a bug in the upload function on 12/22
* enter into multiple contests
* select a different lineup not just most recent lineup
* sort lineups so those with many entries are on the top
* scrape results db (https://rotogrinders.com/resultsdb/site/draftkings/date/2020-12-23/sport/nba/slate/5fe4b217bb4f154ed960c2cc) and research cash lines for various contest types
* deal with players with questionable status
* look for and scrape more predictions
    - https://www.lineups.com/nba/nba-fantasy-basketball-projections#howprojectionschangethroughouttheday (has a download option)
    - https://www.rotowire.com/daily/nba/optimizer.php
    - https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections (already done)
* set up computer to run this half hour before datest that have at least a certain number of games
