from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_tuna():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    location = ('https://app-staging.qlub.cloud/qr/br/SezaiTunaDisc/7/_/_/21e6953aa2')
    driver.get(location)
    sleep(9)

    #fetchOrder
    driver.find_element(By.XPATH,'//span[@class="wrapper"]/span').click()
    sleep(10)

    #SplitBill
    #Split
    driver.find_element(By.XPATH,'//span[@class="wrapper"][.="Split bill"]').click()
    sleep(3)
    #ClickCustom
    driver.find_element(By.ID,'select-custom').click()
    sleep(3)
    #AddAmount
    driver.find_element(By.XPATH,'//*[@id="fullWidth"]').send_keys('5')
    sleep(4)
    #ConfirmSplitt
    driver.find_element(By.ID,'split-bill').click()
    sleep(5)


    #EnterCardInformation
    #Card HolderName
    driver.find_element(By.ID,':r2:').send_keys('Captured')
    sleep(3)
    #CardNumber
    driver.find_element(By.ID,':r3:').send_keys('4111111111111111')
    sleep(3)
    #ExpiryDate
    driver.find_element(By.ID,':r4:').send_keys('1129')
    sleep(3)
    #CVV
    driver.find_element(By.ID,':r5:').send_keys('224')
    sleep(5)

    # ScrollDownPage
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)

    #ClickOnPayNow
    driver.find_element(By.ID,'tuna-card-pay-button').click()
    sleep(15)

    driver.quit()
    print('Successfull Payment')
