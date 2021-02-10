#!/usr/bin/env python3
from scrape_yesterday_results import scrape_yesterday_results
import get_predictions
from combine_predictions import combine_predictions
from DK_ID_template import DK_ID_template
from merge_and_optimize import merge_and_optimize
from upload_and_enter import upload_and_enter
from os import environ, path, open
from dotenv import load_dotenv
from datetime import date
import pandas as pd #JL don't need this long-term

if __name__ == "__main__":
    
    #get yesterday's player results
    scrape_yesterday_results()

    # load inputs
    load_dotenv(dotenv_path='scraping_and_entering_inputs.env')

    #get predictions from numberfire (name, team, prediction)
    nf_username = environ.get('nf_username')
    nf_password = environ.get('nf_password')
    nf_predictions = get_predictions.scrape_numberfire(username = nf_username,password = nf_password)

    #get predictions from lineups.com
    downloads_path = environ.get('downloads_path')
    lu_predictions = get_predictions.scrape_lineups(downloads_path=downloads_path)

    #get predictions from sportsline
    sl_predictions = get_predictions.scrape_sportsline()

    '''
    nf_predictions = pd.read_csv('export/predictions/numberfire_2021-01-29.csv')
    lu_predictions = pd.read_csv('export/predictions/lineups_2021-01-29.csv')
    sl_predictions = pd.read_csv('export/predictions/sportsline_2021-01-29.csv')
    '''

    #injuries
    injuries = get_predictions.scrape_injuries()

    #combine predictions from three sources
    excluded_players = [i for i in environ.get("excluded_players").split("|")] 
    all_predictions = combine_predictions(nf_predictions, sl_predictions, lu_predictions, injuries, excluded_players)

    #download ID's, 
    dk_username = environ.get('dk_username')
    dk_password = environ.get('dk_password')
    driver, df = DK_ID_template(username = dk_username, password = dk_password, downloads_path = downloads_path)

    #merge prediction and template, find optimal lineup, download file for upload and file for record.
    merge_and_optimize(df = df,points_df = all_predictions,excluded_players=excluded_players)

    #JL for now while not entering lineup to know when progarm is finished.
    driver.quit()

    #upload template and enter contest with title of contest_title
    contest_title = environ.get("contest_title")
    version = environ.get('version')
    contest_titles = [i for i in environ.get("contest_titles").split("|")] 
    #upload_and_enter(driver = driver,contest_titles = contest_titles, version = version)
