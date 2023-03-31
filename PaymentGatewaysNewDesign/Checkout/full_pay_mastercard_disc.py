from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest
def test_qr():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    location = ('https://app-staging.qlub.cloud/qr/ae/SezaiCheckoutDiscount/2/_/_/4728e35293')
    driver.get(location)
    sleep(10)

    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div/div[2]/main/div/div/div[3]/button[1]').click()
    sleep(10)

    # Enter mastercard
    driver.switch_to.frame("cardNumber")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-card-number"]').send_keys('5436031030606378')
    driver.switch_to.default_content()
    sleep(2)

    # Enter ExpiryDate
    driver.switch_to.frame("expiryDate")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-expiry-date"]').send_keys('1030')
    driver.switch_to.default_content()
    sleep(1)

    # Enter Cvv
    driver.switch_to.frame("cvv")
    driver.find_element(By.XPATH, '//*[@id="checkout-frames-cvv"]').send_keys('200')
    driver.switch_to.default_content()
    sleep(3)

    # Click On Pay Now
    driver.find_element(By.ID,'checkout-action-btn').click()
    sleep(25)

    driver.quit()
    print('Successfull Payment')