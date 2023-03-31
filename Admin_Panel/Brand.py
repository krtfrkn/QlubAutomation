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
    sleep(12)
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div/main/div/div[3]').click()
    sleep(5)

    #BrandCreate

    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div/div[2]/div[3]/li[3]').click()
    sleep(3)
    #driver.find_element(By.ID,'brands-add-btn').click()
    #sleep(4)

    driver.find_element(By.ID,'search-field').send_keys('sezai')
    sleep(5)