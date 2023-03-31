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

    #Click Role
    driver.find_element(By.ID,'roles-menu-item').click()
    sleep(3)
    driver.find_element(By.ID,'roles-action-btn-0').click()
    sleep(3)
    driver.find_element(By.ID,'roles-action-assign-route').click()
    sleep(3)
    driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/form/div[1]/div/div[1]/div/div/label[1]/span[1]').click()
    sleep(2)
    driver.find_element(By.XPATH,'//*[@id="saved-routes-field"]').send_keys('*')
    sleep(3)
    driver.find_element(By.XPATH,'//*[@id="saved-routes-field"]').send_keys(Keys.ENTER)
    sleep(3)
    driver.find_element(By.ID,'create-gateway-cancel-btn').click()
    sleep(4)