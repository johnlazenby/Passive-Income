# DraftKings

The goal of this project is to make money playing fantasy basketball on draftkings in a completely automated manner. Running one script, `scraping_and_entering.py` collects fantasy point projections for players playing in today's games, creates the optimal lineup based on those projections, uploads this lineup to draftkings, and enters a contest with the lineup. Currently the player projections are scraped from three sources: [numberfire](https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections), [sportsline](https://www.sportsline.com/nba/expert-projections/simulation/), and [lineups.com](https://www.lineups.com/nba/nba-fantasy-basketball-projections). Player's injury status comes from [nbcsports.com](https://www.nbcsports.com/edge/basketball/nba/injury-report). Because the injury status data are pulled all at once before the first game is played, they will be more accurate for early games. The `research` directory contains scripts that evaluate the performance of the lineups based on various sources. Refer to `research/success_vs_median.png`, `research/win_percentage.png`, and `research/average_cash_line_minus_score.png` for the latest results.

The following inputs are required and should be specified in a file, `scraping_and_entering_inputs.env`:
1. nf_username: username for a yahoo account that is signed up for [numberfire](https://www.numberfire.com/)
2. nf_password: password for a yahoo account that is signed up for [numberfire](https://www.numberfire.com/)
3. dk_username: username for draftkings account
4. dk_password: password for draftkings account
5. downloads_path: full file path to location chrome downloads to
6. contest_titles: name of titles of contest program will enter seperated by "|"
7. excluded_players: string of players you do not want to consider in your lineup
8. version: either "nf", "sl", "lu', "nf_lu", "nf_sl", "sl_lu", or "nf_sl_lu" depending on which source(s) you want to use to create the lineup.

Example of a `scraping_and_entering_inputs.env` file: <br>

```
nf_username="email@yahoo.com"
nf_password='cool_password'
dk_username='email@gmail.com'
dk_password='another_cool_password'
downloads_path='/Users/joesmith/Downloads'
contest_titles="'NBA Single Entry $5 Double Up'|'NBA Single Entry $10 Double Up'"
excluded_players = 'KYRIE IRVING|LEBRON JAMES'
version = "nf"
```

## To Do 
* specify correct slate template to download (currently relying on relevant slate always being first)
* enter into multiple contests with more sophistication
* select a different lineup not just most recent lineup (currently only submitting one lineup so no problem)
* sort contests so those with many entries are on the top
* create selenium wrapper to remove redundent code
