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
    global driver
    #Run Test With One Participant [Full Paid + Change English To Japanese]
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy/80/_/_/a868cf40f6')
    driver.get(location)
    sleep(15)


def test_fetch_order():    
    #Fetch order
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(10)


def test_language():    
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[3]/div/div/div').click()
    sleep(2)
    driver.find_element(By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[2]').click()
    sleep(5)


def test_stipe():    
    #Enter Card Number
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.NAME, "number").send_keys("4242424242424242")
    driver.switch_to.default_content()
    sleep(5)
    #Enter Expiry Date
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    expiryDate = driver.find_element(By.NAME, "expiry").send_keys("1230")
    driver.switch_to.default_content()
    sleep(5)
    #Enter CVC
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cvc = driver.find_element(By.NAME, "cvc").send_keys("100")
    driver.switch_to.default_content()
    sleep(5)


def test_pay():    
    #Click On Pay Now
    driver.find_element(By.ID, 'stripe-action-btn').click()
    sleep(10)

    
def test_finish():    
    driver.quit()
    print('Successful Test')