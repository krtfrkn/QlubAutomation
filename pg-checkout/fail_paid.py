from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    driver = webdriver.Chrome()
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-checkout/76/_/_/bd8d756533')
    driver.get(location)
    sleep(10)



    #Fetch order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(10)


    #Add tip
def test_tip(): 
    driver.find_element(By.CLASS_NAME, "Tips_tipLabel__FJ_Dg").click()    
    sleep(5)
    
    
    
    #Enter Visa Card Number
def test_checkout_wrong():    
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-card-number"]').send_keys('4544249167673670')
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


    
def test_finish():
    driver.quit()
    print('Successful Test')