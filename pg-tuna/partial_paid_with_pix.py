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

    #Click on pix
def test_pix():
    driver.find_element(By.ID, 'panel1bh-header').click()
    sleep(15)

    
def test_finish():
    driver.quit()
    print('Successful Test')