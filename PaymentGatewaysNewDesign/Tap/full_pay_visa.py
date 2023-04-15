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
    location = ('https://app-staging.qlub.cloud/qr/sa/dummyTapSezai/2/_/_/5936d8f6e4')
    driver.get(location)
    sleep(10)

    #fetchOrder
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div/div[2]/main/div/div/div[3]/button[1]/span[1]').click()
    sleep(10)

    # ScrollDownPage
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)

    #EnterCardnumber
    driver.switch_to.frame(By.XPATH,'//*[@id="tapp-frame-container"]')
    driver.find_element(By.XPATH, '//input[@id="card-number"]').send_keys('4012000033330026')
    driver.switch_to.default_content()
    sleep(2)