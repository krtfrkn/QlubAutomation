from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver,driver2
    #Run Test With Two Participant [Full Paid]
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    driver2 = webdriver.Firefox(executable_path='/home/sasan/Documents/Python/geckodriver')
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy/21/_/_/e9c134f231')
    driver.get(location)
    driver2.get(location)
    sleep(15)


def test_fetch_order():    
    #Fetch Order
    driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div/div[3]/div').click()
    sleep(3)
    driver2.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div/div[3]/div').click()
    sleep(10)


def test_stripe():    
    #Enter Card Number
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element_by_name("number").send_keys("4242424242424242")
    driver.switch_to.default_content()
    sleep(5)
    #Enter Expiry Date
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    expiryDate = driver.find_element_by_name("expiry").send_keys("1230")
    driver.switch_to.default_content()
    sleep(3)
    #Enter CVC
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cvc = driver.find_element_by_name("cvc").send_keys("100")
    driver.switch_to.default_content()
    sleep(5)


def test_pay():    
    #Click On Pay Now
    driver.find_element_by_id('stripe-action-btn').click()
    sleep(15)


def test_refresh_button():    
    #Click On Refresh Button
    driver2.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[1]/div/div[1]/div/div/div/button').click()
    sleep(15)

    
def test_finish():
    driver.quit()
    print('Successful Test')  