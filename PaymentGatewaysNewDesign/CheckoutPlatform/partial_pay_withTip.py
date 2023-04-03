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
    location = ('https://app-staging.qlub.cloud/qr/ae/SezaiChckPltfmDisc/7/_/_/1e42b1af2d')
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

    # EnterCardInformation
    # Card HolderName
    driver.find_element(By.ID, ':r2:').send_keys('Captured')
    sleep(3)
    # CardNumber
    driver.find_element(By.ID, ':r3:').send_keys('4111111111111111')
    sleep(3)
    # ExpiryDate
    driver.find_element(By.ID, ':r4:').send_keys('1129')
    sleep(3)
    # CVV
    driver.find_element(By.ID, ':r5:').send_keys('224')
    sleep(5)

    # ClickOnPayNow
    driver.find_element(By.ID, 'tuna-card-pay-button').click()
    sleep(35)

    driver.quit()
    print('Successfull Payment')
