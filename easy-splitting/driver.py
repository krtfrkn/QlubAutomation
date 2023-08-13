import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class Driver:

    _driver = None

    @classmethod
    def get_instance(cls):
        if not cls._driver:
            cls._driver = webdriver.Chrome(ChromeDriverManager().install())           
        return cls._driver

    @classmethod
    def quit_instance(cls):
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
