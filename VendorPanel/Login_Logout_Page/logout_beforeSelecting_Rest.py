from asyncore import loop
import webbrowser
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_login():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    location = ('https://vendor-staging.qlub.cloud')
    driver.get(location)
    sleep(3)

    driver.find_element(By.ID,'mui-1').send_keys('sezai.bayhan+Automation@qlub.io')
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="mui-2"]').send_keys('sezhat2016')
    sleep(3)

    driver.find_element(By.ID,'login-btn').click()
    sleep(10)

    driver.find_element(By.ID,'logout-btn').click()
    sleep(5)

    