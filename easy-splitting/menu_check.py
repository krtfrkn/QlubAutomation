from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#from selenium.webdriver.common.alert import Alert
import pytest


def test_qr():
    #Run Test With One Participant After Update From POS [Partial Paid + Tip + With Refresh Button]
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Run Test With One Participant [Partial Paid]
    location = ('https://app-staging.qlub.cloud/qr/ae/sasan-release/7/2/_/a0844809c5')
    driver.get(location)
    sleep(20)


def test_menu(): 
    #Click on menu
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[4]/div').click()
    sleep(10)


def test_scroll():
    #Scrolling    
    driver.maximize_window()
    driver.execute_script("window.scrollBy(0, 1000);")


    