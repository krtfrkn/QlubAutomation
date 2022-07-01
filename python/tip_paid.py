#from http.client import ACCEPTED
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest

# Run Test With One Participant [Set Amount to 0 + Tip]


def test_qr():
    global driver
    driver = webdriver.Chrome('/home/sasan/Documents/Python/chromedriver')
    # Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummy/2/_/_/39854773cd')
    driver.get(location)
    sleep(20)


def test_fetch_order():
    # Fetch Order
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[3]/div').click()
    sleep(15)


def test_lets_split():
    # Open Split Section
    driver.find_element(By.XPATH, '//*[@id="split-bill"]').click()
    sleep(2)


def test_edit_name():
    # Edit Name
    driver.find_element(By.XPATH, '//*[@id="name"]').send_keys('Sasan Sharifian')
    sleep(2)


def test_set_amount():
    # Set 0 Amount
    driver.find_element(By.XPATH, '//*[@id="amount"]').send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE)
    sleep(5)


def test_add_tip():
    # Add Tip
    driver.find_element(By.CLASS_NAME, "Tips_tipLabel__FJ_Dg").click()
    sleep(6)


def test_strip():
    # Enter Card Number
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.NAME, "number").send_keys("4242424242424242")
    driver.switch_to.default_content()
    sleep(5)
    # Enter Expiry Date
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    expiryDate = driver.find_element(By.NAME, "expiry").send_keys("1230")
    driver.switch_to.default_content()
    sleep(3)
    # Enter CVC
    driver.switch_to.frame(frame_reference=driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div/div[4]/div/div/div/div/form/div[1]/div[1]/div/iframe'))
    cvc = driver.find_element(By.NAME, "cvc").send_keys("100")
    driver.switch_to.default_content()
    sleep(5)


def test_pay():
    # Click On Pay Now
    driver.find_element(By.ID, 'stripe-action-btn').click()
    sleep(15)


def test_email():    
    driver.find_element(By.NAME, "email").send_keys("sasan@qlub.io")
    sleep(2)
    #Click On Send
    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/div/div[2]/form/div/div[2]/div/div/div/button').click()
    sleep(2)


def test_finish():
    driver.quit()
    print('Successful Test')
