from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest


def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    driver.maximize_window()

    location = ('https://app-staging.qlub.cloud/qr/sa/SezaiMoyasarDiscount/2/_/_/3c2e4ff4ab')
    driver.get(location)
    sleep(10)

    # Fetch Order
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div/div/div/div[2]/main/div/div/div[3]/button[1]').click()
    sleep(7)

    #AddTip
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[1]/div[2]/div/div[1]/div/div').click()
    sleep(3)

    # Enter card info
    driver.find_element(By.ID, "mysr-cc-name").send_keys("Sezai Bayhan")
    driver.find_element(By.ID, "mysr-cc-number").send_keys("4111111111111111")
    driver.find_element(By.XPATH,'//*[@id="mysr-form-form-el"]/div[2]/div/form/div[2]/div[2]/div[2]/input[1]').send_keys("12/26")
    driver.find_element(By.XPATH,'//*[@id="mysr-form-form-el"]/div[2]/div/form/div[2]/div[2]/div[2]/input[2]').send_keys("100")
    sleep(5)



    # Click On Pay Now
    driver.find_element(By.XPATH, '//*[@id="mysr-form-form-el"]/div[2]/div/form/button').click()
    sleep(12)

    driver.find_element(By.XPATH, '//*[@id="acs_code"]').send_keys('12345')
    sleep(3)

    driver.find_element(By.XPATH, '/html/body/div/div/section[3]/form/div[2]/button[1]').click()
    sleep(35)