from asyncore import loop
import webbrowser
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_login():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    location = ('https://vendor-staging.qlub.cloud')
    driver.get(location)
    sleep(3)

    driver.find_element(By.ID,'mui-1').send_keys('sezai.bayhan+Automation@qlub.io')
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="mui-2"]').send_keys('sezhat2016')
    sleep(3)

    driver.find_element(By.ID,'login-btn').click()
    sleep(10)

    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[2]/div/div/div/div[2]/div/div/form/div/div[1]/div/div/div').click()
    sleep(4)

    driver.find_element(By.XPATH,'//*[@id="select-restaurant-autocomplete"]').send_keys('dummyCheckoutSezai')
    sleep(10)

    driver.find_element(By.CSS_SELECTOR,'.MuiAutocomplete-option').click()
    sleep(5)

    driver.find_element(By.ID,'select-res-btn').click()
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/header/div/div[1]/button').click()
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="Table View"]').click()
    sleep(3)

    driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div[1]/header/div/div[3]/button[1]').click()
    sleep(3)
    driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div[2]/div[1]').click()
    sleep(4)
    driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/button').click()
    sleep(4)

    driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/header/div/div[3]/button[1]').click()
    sleep(3)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[2]').click()
    sleep(4)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/button').click()
    sleep(4)

    driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/header/div/div[3]/button[1]').click()
    sleep(3)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[3]').click()
    sleep(4)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/button').click()
    sleep(4)

    driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/header/div/div[3]/button[1]').click()
    sleep(3)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[4]').click()
    sleep(4)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/button').click()
    sleep(4)

    driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/header/div/div[3]/button[1]').click()
    sleep(3)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[5]').click()
    sleep(4)
    driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/button').click()
    sleep(4)


    driver.quit()
    print('Success!')


