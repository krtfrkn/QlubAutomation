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
    sleep(8)
    driver.find_element(By.XPATH,'//button[.="Cancel"]').click()
    sleep(5)

    driver.find_element(By.XPATH, '//*[@id="restaurants-menu-item"]').click()
    sleep(3)
    #EmptyConfigsClick
    driver.find_element(By.XPATH,'/html/body/div/div/div[1]/main/div/div/div/div[1]/div[2]/div/div[5]/div/div/div').click()
    sleep(3)
    #PG
    driver.find_element(By.XPATH,'//*[@id="menu-"]/div[3]/ul/li[1]').click()
    sleep(2)
    #POS
    driver.find_element(By.XPATH,'//*[@id="menu-"]/div[3]/ul/li[2]').click()
    sleep(2)
    #VENDOR
    driver.find_element(By.XPATH,'//*[@id="menu-"]/div[3]/ul/li[3]').click()
    sleep(2)
    #ORDER
    driver.find_element(By.XPATH,'//*[@id="menu-"]/div[3]/ul/li[4]').click()
    sleep(2)

    # EmptyConfigsUnClick
    # PG
    driver.find_element(By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[1]').click()
    sleep(2)
    # POS
    driver.find_element(By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[2]').click()
    sleep(2)
    # VENDOR
    driver.find_element(By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[3]').click()
    sleep(2)
    # ORDER
    driver.find_element(By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[4]').click()
    sleep(3)

