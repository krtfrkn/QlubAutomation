from asyncore import loop
#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
#Run Test With Two Participant [Partial Paid]
import pytest

def test_two_participant():
    global driver,driver2
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    driver2 = webdriver.Firefox(executable_path='/home/sasan/Documents/Python/geckodriver')


def test_qr():
    #Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy/14/_/_/c41e8ba6bf')
    driver.get(location)
    driver2.get(location)


def test_fetch_order():    
    sleep(15)
    #Fetch Order
    driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div/div[3]/div').click()
    sleep (5)
    driver2.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div/div[3]/div').click()
    sleep(15)


def test_edit_name():    
    #Edit Name 1,2
    driver.find_element_by_xpath('//*[@id="name"]').send_keys('Sasan')
    driver2.find_element_by_xpath('//*[@id="name"]').send_keys('Sharifian')
    sleep(7)


def test_set_amount():    
    #Set Partial Amount 1,2
    driver.find_element_by_xpath('//*[@id="amount"]').send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE)
    driver.find_element_by_xpath('//*[@id="amount"]').send_keys('10')
    driver2.find_element_by_xpath('//*[@id="amount"]').send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE)
    driver2.find_element_by_xpath('//*[@id="amount"]').send_keys('15')


def test_stripe_p1():    
    #Enter Card Number
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element_by_name("number").send_keys("4242424242424242")
    driver.switch_to.default_content()
    sleep(5)
    #Enter Expiry Date
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    expiryDate = driver.find_element_by_name("expiry").send_keys("1230")
    driver.switch_to.default_content()
    sleep(3)
    #Enter CVC
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cvc = driver.find_element_by_name("cvc").send_keys("100")
    driver.switch_to.default_content()
    sleep(5)


def test_pay_p1():    
    #Click On Pay Now
    driver.find_element_by_id('stripe-action-btn').click()
    sleep(15)


def test_stripe_p2():    
    #Enter Card Number 2
    driver2.switch_to.frame(frame_reference=driver2.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cardnumber = driver2.find_element_by_name("number").send_keys("4242424242424242")
    driver2.switch_to.default_content()
    sleep(5)
    #Enter Expiry Date 2
    driver2.switch_to.frame(frame_reference=driver2.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    expiryDate = driver2.find_element_by_name("expiry").send_keys("1230")
    driver2.switch_to.default_content()
    #Enter CVC 2
    driver2.switch_to.frame(frame_reference=driver2.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cvc = driver2.find_element_by_name("cvc").send_keys("100")
    driver2.switch_to.default_content()
    sleep(5)


def test_pay_p2():    
    #Click On Pay Now 2
    driver2.find_element_by_id('stripe-action-btn').click()
    sleep(15)

    
def test_finish():    
    driver.quit()
    driver2.quit()
    print('Successful Test')