import string
from asyncore import loop
import webbrowser
from random import random
from telnetlib import EC

from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

def test_login():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    location = ('https://admin-panel-staging.qlub.cloud/login')
    driver.get(location)
    sleep(3)

    #Login
    driver.find_element(By.XPATH,'//*[@id="email-field"]').send_keys('sezai.bayhan@qlub.io')
    sleep(2)
    driver.find_element(By.XPATH,'//*[@id="password-field"]').send_keys('sezhat2016')
    sleep(2)
    driver.find_element(By.ID,'login-button').click()
    sleep(5)
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div/main/div/div[3]').click()
    sleep(5)


    #FILTERS_BOX

    driver.find_element(By.ID, 'discounts-menu-item').click()
    sleep(4)
    #1_Filters
    #driver.find_element(By.ID,'table-filters').click()
    #sleep(3)

    #2_Countries
    #driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/main/div/div/div/div[1]/div[2]/div/div[2]/div').click()
    #sleep(4)

    #3_Restaurants
    #driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/main/div/div/div/div[1]/div[2]/div/div[1]').send_keys('newReleaseSezai')
    #sleep(3)
    #driver.find_element(By.ID, 'restaurant-select-discounts-restaurant').send_keys(Keys.ENTER)
    #sleep(3)

    #DiscountUpdate
    driver.find_element(By.ID,'Discounts-action-btn-0').click()
    sleep(3)

    driver.find_element(By.ID,'Discounts-action-activity_logs').click()
    sleep(4)
