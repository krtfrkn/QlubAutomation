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
    #Add restaurant link
    location = ('https://app-demo.qlub.cloud/qr/br/tuna-test/12/_/_/b762e1ae29')
    driver.get(location)
    sleep(10)
    

    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(9)

    #Split Bill
def test_split():
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[2]/div/div[2]/button[1]').click()
    sleep(10)


    #Pay a custom amount
def test_bycustom():
    driver.find_element(By.ID, 'select-custom').click()
    sleep(7)

def test_select():
    driver.find_element(By.NAME, 'amount').send_keys('5')
    sleep(7)

def test_confirm():    
    driver.find_element(By.ID, 'confirm-split').click()
    sleep(15)


    #Enter card info
def test_tuna():
    driver.find_element(By.NAME, "cardHolderName_creditCard").send_keys("Captured")
    sleep(6)
    driver.find_element(By.NAME, "cardNumber_creditCard").send_keys("4111111111111111")
    sleep(5)
    driver.find_element(By.NAME, "expirationDate_creditCard").send_keys("12/26")
    sleep(3)
    driver.find_element(By.NAME, "cvv_creditCard").send_keys("100")
    sleep(7)


    #Click on pay
def test_pay():    
    driver.find_element(By.ID, 'tuna-action-btn').click()
    sleep(15)


    
def test_finish():
    driver.quit()
    print('Successful Test')