from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-maf/6/_/_/b7ee90d46c')
    driver.get(location)
    sleep(20)
    

    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(15)


    #Click On Pay Now
def test_pay():    
    driver.find_element(By.ID, 'dgpay-action-btn').click()
    sleep(12)


    #Enter Card Number
def test_dgpay():
    driver.find_element(By.ID, 'CardHolderName').send_keys('AkBank')
    driver.find_element(By.ID, 'CardNO').send_keys('5571135571135575')
    driver.find_element(By.ID, 'ExpireDate').send_keys('1226')
    driver.find_element(By.ID, 'Cvv').send_keys('100')
    sleep(15)
    

    #Click on pay
def test_pay_button():
    driver.find_element(By.ID, "paybtn").click()

