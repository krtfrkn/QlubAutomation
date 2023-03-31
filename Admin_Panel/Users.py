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
    driver.find_element(By.XPATH,'//button[.="Cancel"]').click()
    sleep(5)

    #UsersCreate-Restaurant
    driver.find_element(By.ID,'users-add-btn').click()
    sleep(4)
    driver.find_element(By.ID,'user-type-restaurant').click()
    sleep(4)
    driver.find_element(By.ID,'cancel-user').click()
    sleep(3)

    #UsersCreate-Qlub
    driver.find_element(By.ID, 'users-add-btn').click()
    sleep(4)
    driver.find_element(By.ID, 'user-type-office').click()
    sleep(4)
    driver.find_element(By.ID, 'cancel-user').click()
    sleep(3)

    #Users-FILTERS
    #Role
    driver.find_element(By.ID,'role-select-Role').click()
    sleep(3)

    #UsersType
    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div/main/div/div/div/div[1]/div[2]/div/div[2]/div').click()
    sleep(3)

    #Search
    driver.find_element(By.XPATH,'//*[@id="search-field"]').send_keys('sezai')
    sleep(5)

    driver.find_element(By.ID,'users-action-btn-0').click()
    sleep(4)
    driver.find_element(By.ID,'users-action-edit').click()
    sleep(4)
    driver.find_element(By.ID,'create-update-user').click()
    sleep(3)



