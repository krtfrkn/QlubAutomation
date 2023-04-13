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

    location = ('https://app-staging.qlub.cloud/qr/sa/dummyMoyasarSezai/8/_/_/85f72b231e')
    driver.get(location)
    sleep(10)

    # fetchOrder
    driver.find_element(By.XPATH, '//span[@class="wrapper"]/span').click()
    sleep(10)

    # SplitBill
    # Split
    driver.find_element(By.XPATH, '//span[@class="wrapper"][.="Split bill"]').click()
    sleep(3)
    # ClickCustom
    driver.find_element(By.ID, 'select-custom').click()
    sleep(3)
    # AddAmount
    driver.find_element(By.XPATH, '//*[@id="fullWidth"]').send_keys('5')
    sleep(4)
    # ConfirmSplitt
    driver.find_element(By.ID, 'split-bill').click()
    sleep(5)

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