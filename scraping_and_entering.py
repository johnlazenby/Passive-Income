#!/usr/bin/env python3
from scrape_numberfire import scrape_numberfire
from DK_ID_template import DK_ID_template
from merge_and_optimize import merge_and_optimize
from upload_and_enter import upload_and_enter
from os import environ, path
from dotenv import load_dotenv

# load inputs
load_dotenv(dotenv_path='scraping_and_entering_inputs.env')

#get predictions from numberfire (name, team, prediction)
nf_username = environ.get('nf_username')
nf_password = environ.get('nf_password')
predictions = scrape_numberfire(username = nf_username,password = nf_password)

#download ID's, 
dk_username = environ.get('dk_username')
dk_password = environ.get('dk_password')
downloads_path = environ.get('downloads_path')
#driver, df = DK_ID_template(username = dk_username, password = dk_password, downloads_path = downloads_path)

#merge prediction and template, find optimal lineup, download file for upload and file for record.
merge_and_optimize(df = df,points_df = predictions, upload_path = upload_path, record_path = lineup_path)

#upload template and enter contest with title of contest_title
contest_title = environ.get("contest_title")
upload_and_enter(driver = driver,upload_path = upload_path,contest_title = contest_title)
