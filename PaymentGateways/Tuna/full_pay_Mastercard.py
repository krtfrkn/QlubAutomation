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
    location = ('https://app-staging.qlub.cloud/qr/br/dummyTunaSezai/28/_/_/be77291654')
    driver.get(location)
    sleep(9)

    #fetchOrder
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div/div[2]/main/div/div/div[3]/button[1]/span[1]').click()
    sleep(10)



    #OpenCardOption
    #driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[3]/button/div/div[1]/svg').click()
    #sleep(3)
    #Card HolderName
    driver.find_element(By.ID,':r2:').send_keys('Captured')
    sleep(3)

    #EnterCardNumber
    driver.find_element(By.ID,':r3:').send_keys('5555555555554444')
    sleep(3)
    #EnterExpiryDate
    driver.find_element(By.ID,':r4:').send_keys('1128')
    sleep(3)
    #EnterCVV
    driver.find_element(By.ID,':r5:').send_keys('222')
    sleep(3)

    #ClickOnPayNow
    driver.find_element(By.ID,'tuna-card-pay-button').click()
    sleep(7)

    driver.quit()
    print('Successfull Payment')
