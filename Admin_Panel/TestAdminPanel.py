from asyncore import loop
import webbrowser
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import pytest


class TestAdminPanel:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=self.options)
        self.location = ('https://admin-panel-staging.qlub.cloud/login')

    def testLogin(self):
        # Add restaurant link
        self.driver.get(self.location)
        sleep(2)

        self.driver.find_element(By.ID, 'email-field').send_keys('sezai.bayhan@qlub.io')

        self.driver.find_element(By.ID, 'password-field').send_keys('sezhat2016')
        sleep(2)

        self.driver.find_element(By.XPATH, '// *[ @ id = "login-button"]').click()
        sleep(5)

        self.driver.find_element(By.XPATH, '//button[.="Cancel"]').click()
        sleep(5)

    def createRestaurant(self):
        try:
            self.driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/div/div[2]/div[3]/li[4]').click()
            

        except:
            self.driver.close()

    def createUser(self):
        return


test = TestAdminPanel()
test.testLogin()
test.createRestaurant()
