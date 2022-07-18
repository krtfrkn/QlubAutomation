from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#from selenium.webdriver.common.alert import Alert


def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Run Test With One Participant [Full Paid With Wrong ExpiryDate on Purpose]
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-checkout/15/_/_/4b9cd5380c')
    driver.get(location)
    
def test_fetch_order():
    sleep(10) 
    #Fetch Order
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click() 


def test_checkout1():
    sleep(7)
    #Enter Visa Card Number
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-card-number"]').send_keys('4242424242424242')
    driver.switch_to.default_content()
    sleep(2)


    #Enter Wrong ExpiryDate
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys('1010')
    driver.switch_to.default_content()
    sleep(1)


    #Enter Cvv
    driver.switch_to.frame("cvv")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-cvv"]').send_keys('100')
    driver.switch_to.default_content()
    sleep(3)


    #Click On Pay Now
    driver.find_element(By.XPATH, '//*[@id="checkout-action-btn"]').click()
    sleep(7)

def test_checkout2():
    #Enter Visa Correct ExpiryDate
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys(Keys.BACKSPACE, Keys.BACKSPACE)
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys('30')
    driver.switch_to.default_content()
    sleep(6)

def test_pay():
    #Click On Pay Now
    driver.find_element(By.XPATH, '//*[@id="checkout-action-btn"]').click()
    sleep(7)


    driver.quit()
    print('Successful Test')