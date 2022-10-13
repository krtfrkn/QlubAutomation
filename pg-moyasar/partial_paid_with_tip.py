from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    #Run Test With One Participant [Full Paid with Tip]
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/sa/sasan-moyasar/6/6/_/aa5568569b')
    driver.get(location)
    sleep(15)
    

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
def test_moyasar():
    driver.find_element(By.ID, "mysr-cc-name").send_keys("Sasan Sharifian")
    driver.find_element(By.ID, "mysr-cc-number").send_keys("4111111111111111")
    driver.find_element(By.XPATH, '//*[@id="mysr-form-form-el"]/div[2]/div/form/div[2]/div[2]/div[2]/input[1]').send_keys("12/26")
    driver.find_element(By.XPATH, '//*[@id="mysr-form-form-el"]/div[2]/div/form/div[2]/div[2]/div[2]/input[2]').send_keys("100")
    sleep(5)
    

    #Click On Pay Now
def test_pay():    
    driver.find_element(By.XPATH, '//*[@id="mysr-form-form-el"]/div[2]/div/form/button').click()
    sleep(12)


