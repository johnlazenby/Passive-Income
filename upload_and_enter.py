from datetime import date
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
import time
import os


def upload_and_enter(driver,contest_title):

    #upload csv file
    
    selector = '[name="fileUpload"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    file_name = os.path.join("/Users/johnlazenby/projects/DraftKings/export/for_upload","lineup_{}.csv".format(date.today()))
    driver.find_element_by_css_selector(selector).send_keys("{}".format(file_name))
    time.sleep(5)

    #lineups tab
    selector = '[alt="Lineups"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    #click join (not unique) hopefully there is only one linup here
    selector = "//*[contains(text(), 'Join')]"
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, selector)))
    element = driver.find_element_by_xpath(selector)
    driver.execute_script("arguments[0].click();", element)

    #click load lineup
    selector = '[data-test-id="lineupEntries-Submit"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    #click double ups and 50/50s
    selector = '[data-contest-type="IsFiftyfifty"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)

    #select contest with title of "title"
    xpath = "//*[contains(text(), '{}')]/parent::*/parent::*/div[6]/button".format(contest_title)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
    element = driver.find_element_by_xpath(xpath)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    time.sleep(5)
    driver.quit()