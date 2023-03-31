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
    location = ('https://app-staging.qlub.cloud/qr/au/dummyVostroSezai/1/_/_/0af0c60973')
    driver.get(location)
    sleep(10)

    #fetchOrder
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div/div[2]/main/div/div/div[3]/button[1]/span[1]').click()
    sleep(10)

    #EnterCardNumber
    driver.switch_to.frame("Card Number")
    driver.find_element(By.XPATH, '//*[@id="pan"]').send_keys('4111111111111111')
    driver.switch_to.default_content()
    sleep(2)
    #EnterExpiryDate
    driver.find_element(By.ID,'vostro_exp_date').send_keys('1032')
    sleep(3)
    #EnterCVV
    driver.find_element(By.XPATH,'//*[@id="cvv"]').send_keys('124')
    sleep(3)
    #ClickPayNow
    driver.find_element((By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[1]/div/div/div/div/div[2]/div/div[2]')).click()
    sleep(3)