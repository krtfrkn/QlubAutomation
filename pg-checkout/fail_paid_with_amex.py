from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-checkout/93/_/_/f71b845bda')
    driver.get(location)
    sleep(10)

    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(10)


    #Enter Card
def test_checkout():    
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-card-number"]').send_keys('345678901234564')
    driver.switch_to.default_content()
    sleep(2)
    #Enter ExirayDate
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys('1030')
    driver.switch_to.default_content()
    sleep(1)
    #Enter Cvv
    driver.switch_to.frame("cvv")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-cvv"]').send_keys('1234')
    driver.switch_to.default_content()
    sleep(3)


    #Click On Pay Now
def test_pay():    
    driver.find_element(By.XPATH, '//*[@id="checkout-action-btn"]').click()
    sleep(15)
    
def test_finish():
    driver.quit()
    print('Successful Test')