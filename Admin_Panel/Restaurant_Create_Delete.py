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

import string
import random # define the random module

#RandomClass for Restaurantunique
def generateRestaurantCode():
    S = 5
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    print(str(ran))
    return ran

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
    driver.find_element(By.XPATH,'//button[.="Cancel"]').click()
    sleep(5)

    #CREATE RESTAURANT
    driver.find_element(By.XPATH,'//*[@id="restaurants-menu-item"]').click()
    sleep(3)
    driver.find_element(By.XPATH,'//*[@id="restaurants-add-btn"]').click()
    sleep(4)

    #Click Multistep
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[1]/main/div/div/div/h5/label').click()
    sleep(4)
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/main/div/div/div/h5/label').click()
    sleep(5)

    #Select Country
    driver.find_element(By.XPATH,'//*[@id="country-select-country_code"]').click()
    sleep(2)
    driver.find_element(By.XPATH,'//*[@id="country-select-country_code-option-1"]').click()
    sleep(3)

    #Select TimeZone
    driver.find_element(By.XPATH,'//*[@id="timezone-select-timezone"]').send_keys('Asia/Dubai')
    sleep(2)
    driver.find_element(By.XPATH, '//*[@id="timezone-select-timezone"]').send_keys(Keys.ENTER)

    #SelectBrand
    driver.find_element(By.ID,'brand-select-brand_id').send_keys('SEZAI-UAE')
    sleep(4)
    driver.find_element(By.ID,'brand-select-brand_id').send_keys(Keys.ENTER)

    #AddRestaurantUnique
    rstUnique = generateRestaurantCode()
    driver.find_element(By.XPATH,'//*[@id="restaurant-unique-field"]').send_keys(rstUnique)
    sleep(2)

    #FillRestaurantInformations
    driver.find_element(By.XPATH,'//*[@id="name-field"]').send_keys('sezaiAutomation')
    sleep(2)

    driver.find_element(By.XPATH,'//*[@id="title-field"]').send_keys('sezaiAutomation')
    sleep(2)

    driver.find_element(By.XPATH,'//*[@id="email-field"]').send_keys('sezai.bayhan@qlub.io')
    sleep(2)

    driver.find_element(By.XPATH,'//*[@id="phone-field"]').send_keys('111) 111-1111')
    sleep(2)

    driver.find_element(By.XPATH,'//*[@id="city-field"]').send_keys('Dubai')
    sleep(2)

    driver.find_element(By.ID,'address-1-field').send_keys('Dubai')
    sleep(2)

    driver.find_element(By.ID,'ops-mode-select-field').click()
    sleep(2)

    driver.find_element(By.XPATH,'//*[@id="menu-ops_mode"]/div[3]/ul/li[2]').click()
    sleep(2)

    driver.find_element(By.ID,'create-update-user').click()
    sleep(3)

    #DeleteRestaurant
    driver.find_element(By.ID,'restaurants-action-btn-0').click()
    sleep(3)

    driver.find_element(By.ID,'restaurants-action-delete').click()
    sleep(3)

    driver.find_element(By.ID,'restaurants-confirm-delete-btn').click()
    sleep(3)





