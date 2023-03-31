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
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

def test_menu():
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
    sleep(7)
    driver.find_element(By.XPATH,'//button[.="Cancel"]').click()
    sleep(5)

    driver.find_element(By.XPATH, '//*[@id="restaurants-menu-item"]').click()
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="search-field"]').send_keys('Auto_Sezai')
    sleep(4)

    driver.find_element(By.ID,'restaurants-action-btn-0').click()
    sleep(4)
    driver.find_element(By.ID,'restaurants-action-edit').click()
    sleep(3)
    driver.find_element(By.ID,'restaurant-menu-upload-btn').click()
    sleep(4)

    fileUpload = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div/div')
    fileUpload.click()
    sleep(5)
    fileUpload.send_keys('/Users/sezaibayhan/Downloads/document.pdf')
    sleep(5)
    #fileUpload.submit()
    #sleep(3)








