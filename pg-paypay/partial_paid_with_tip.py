from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Run Test With One Participant [Full Paid with Tip]
    location = ('https://app-staging.qlub.cloud/qr/jp/sasan-paypay/3/_/_/a10022a2d6')
    driver.get(location)
    sleep(10)


    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(10)


    #Add Tip
def test_add_tip():
    driver.find_element(By.CLASS_NAME, "Tips_tipLabel__FJ_Dg").click()
    sleep(6)


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


    #Click on paypay
def test_paypay():    
    driver.find_element(By.ID, 'pay-pay-action-btn').click()

    
def test_finish():
    driver.quit()
    print('Successful Test')