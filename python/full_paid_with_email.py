#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.alert import Alert
import pytest


def test_setup():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Run Test With One Participant [Full Paid]
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-checkout/90/_/_/1827c10c80')
    driver.get(location)
    sleep(10)


def test_fetch_order(): 
    #Fetch Order
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(10)    


def test_checkout():
    #Enter Visa Card Number
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-card-number"]').send_keys('4242424242424242')
    driver.switch_to.default_content()
    sleep(2)
    #Enter ExirayDate
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys('1030')
    driver.switch_to.default_content()
    sleep(1)
    #Enter Cvv
    driver.switch_to.frame("cvv")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-cvv"]').send_keys('100')
    driver.switch_to.default_content()
    sleep(3)


def test_pay():    
    #Click On Pay Now
    driver.find_element(By.XPATH, '//*[@id="checkout-action-btn"]').click()
    sleep(15)


def test_email():    
    driver.find_element(By.NAME, "email").send_keys("sasan@qlub.io")
    sleep(2)
    #Click On Send
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[2]/form/div/div[2]/div/div/div/button').click()
    sleep(2)


    
def test_finish():
    driver.quit()
    print('Successful Test')
