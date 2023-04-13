from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest


def test_qr():
    global driver
    # Run Test With One Participant [Partial Paid with Tip]
    driver = webdriver.Chrome()
    # Add restaurant link
    location = ('https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/58/_/_/0ca4aa02b3')
    driver.get(location)
    sleep(10)





    # fetchOrder
    driver.find_element(By.XPATH, '//span[@class="wrapper"]/span').click()
    sleep(10)

    # Split Bill

    driver.find_element(By.XPATH, '//span[@class="wrapper"][.="Split bill"]').click()
    sleep(3)

    # Pay a custom amount
    driver.find_element(By.ID, 'select-custom').click()
    sleep(7)

    driver.find_element(By.NAME, 'amount').send_keys('5')
    sleep(7)

    driver.find_element(By.ID, 'split-bill').click()
    sleep(5)

    #Edit
    driver.find_element(By.XPATH,'//span[normalize-space()="Edit split"]').click()
    sleep(3)
    driver.find_element(By.NAME, 'amount').send_keys(Keys.BACK_SPACE)
    sleep(1)
    driver.find_element(By.NAME, 'amount').send_keys('10')
    sleep(7)
    driver.find_element(By.ID, 'split-bill').click()
    sleep(5)



    # Enter Card Number
    driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[1]/div/div/div/div/div[2]/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.XPATH, '//*[@id="Field-numberInput"]').send_keys("4242424242424242")
    driver.switch_to.default_content()
    # Enter Expiry Date
    driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[1]/div/div/div/div/div[2]/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.XPATH, '//*[@id="Field-expiryInput"]').send_keys("1030")
    driver.switch_to.default_content()
    # Enter CVC
    driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[1]/div/div/div/div/div[2]/form/div[1]/div[1]/div/iframe'))
    driver.find_element(By.XPATH, '//*[@id="Field-cvcInput"]').send_keys("100")
    driver.switch_to.default_content()
    sleep(5)

    # Click On Pay Now
    driver.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div/div/div/div[2]/div[1]/div[2]/main/div/div/div[5]/div/div/div[4]/div[1]/div/div/div/div/div[2]/form/div[2]').click()
    sleep(35)

    driver.quit()
    print('Successfull Payment')

