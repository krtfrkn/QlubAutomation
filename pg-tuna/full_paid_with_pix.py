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


    #Add tip
def test_add_tip():
    driver.find_element(By.CLASS_NAME, "Tips_tipLabel__FJ_Dg").click()
    sleep(6)


    #Click on pix
def test_pix():
    driver.find_element(By.ID, 'panel1bh-header').click()
    sleep(15)

    
def test_finish():
    driver.quit()
    print('Successful Test')