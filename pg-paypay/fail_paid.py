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
    location = ('https://app-staging.qlub.cloud/qr/jp/sasan-paypay/1/_/_/5cbbaa03e5')
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

    #Click on paypay
def test_paypay():    
    driver.find_element(By.ID, 'pay-pay-action-btn').click()
    sleep(15)

   
def test_pay():
    driver.find_element(By.XPATH, '//*[@id="control"]/div/form[1]/input[1]').click()


def test_finish():
    driver.quit()
    print('Successful Test')