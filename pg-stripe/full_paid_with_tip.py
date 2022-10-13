from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pytest

def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy/60/1/_/5763a83750')
    driver.get(location)
    sleep(10)


    #Fetch Order
def test_fetch_order(): 
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    try:
        test_fetch_order = driver.find_element(By.ID,"__next")
        test_fetch_order.click()
    except NoSuchElementException :
        print('No Order To Pay') 
    sleep(7)
    

   #Add Tip
def test_tip(): 
    driver.find_element(By.CLASS_NAME, "Tips_tipLabel__FJ_Dg").click()    
    sleep(5) 


    #Enter card
def test_stripe():
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[4]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.NAME, "number").send_keys("4242424242424242")
    driver.switch_to.default_content()
    #Enter Expiry Date
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[4]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.NAME, "expiry").send_keys("1230")
    driver.switch_to.default_content()
    #Enter CVC
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div[4]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.NAME, "cvc").send_keys("100")
    driver.switch_to.default_content()
    sleep(5)

    #Click on pay
def test_pay():    
    driver.find_element(By.ID, 'stripe-action-btn').click()
    sleep(15)

    
def test_finish():
    driver.quit()
    print('Successful Test')

