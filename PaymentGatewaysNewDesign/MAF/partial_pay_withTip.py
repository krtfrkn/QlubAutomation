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
    location = ('https://app-staging.qlub.cloud/qr/ae/dummyMAFSezai/8/_/_/d105e60542')
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

    # AddTip
    driver.find_element(By.XPATH, '(//div[@class="Tips_tips__9J2Ze"]/div/div)[1]').click()
    sleep(4)

    #OpencardOption
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[2]').click()
    sleep(3)

    # Enter Card Number
    driver.find_element(By.XPATH, '//*[@id="cardNumber"]').send_keys("4456530000001005")
    sleep(2)
    # Enter Expiry Date
    driver.find_element(By.ID,'cardExpiry').send_keys("1033")
    sleep(2)
    # Enter CVC
    driver.find_element(By.NAME,'securityCode').send_keys("101")
    sleep(2)

    # ScrollDownPage
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)

    # Click On Pay Now
    driver.find_element(By.XPATH, '//span[normalize-space()="Pay Now"]').click()
    sleep(35)