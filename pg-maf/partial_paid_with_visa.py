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
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy-maf/5/_/_/ebb42ce7dd')
    driver.get(location)
    sleep(20)
    

    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(15)


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
def test_maf():
    driver.find_element(By.ID, "cardNumber").send_keys("376000000000006")
    driver.find_element(By.ID, "cardExpiry").send_keys("12/26")
    driver.find_element(By.ID, "cardCvc").send_keys("100")
    sleep(5)
    

    #Click On Pay Now
def test_pay():    
    driver.find_element(By.CLASS_NAME, 'mafpay-default-card-submit').click()
    sleep(12)

