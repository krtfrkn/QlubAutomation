'''   
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from driver import Driver
from elements_page import ElementsPage
from selenium.webdriver.support import expected_conditions as EC
from ConfigurationReader import Configuration
import time

#CREATE DRIVER    
driver = Driver.get_instance()
    
#CREATE CONFIGURATION OBJECT
config = Configuration()

#MAXIMIZE PAGE
driver.maximize_window()
    
#GO TO QR
location = ElementsPage.get_URL(50)    
driver.get(location)   
    
#CREATING WEB ELEMENT
pay_button_on_landing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
pay_button_on_landing.click()

#GO TO END OR HEAD OF THE PAGE
driver.find_element(By.TAG_NAME,'body').send_keys(Keys.HOME)
driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
	 
#SCROLL DOWN TO THE END OF THE PAGE (ANOTHER WAY)
lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
match=False
while(match==False):
    lastCount = lenOfPage
    time.sleep(3)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    if lastCount==lenOfPage:
        match=True
            
#SWITCH TO IFRAME
driver.switch_to.frame(driver.find_element(By.XPATH,config.get('iframe_element')))
    
#SWITCH TO DEFAULT CONTENT
driver.switch_to.default_content()
    
#SWITCH TO IFRAME
driver.switch_to.frame(driver.find_element(By.XPATH,config.get('iframe_element')))

#WAIT
wait = WebDriverWait(driver, 50)
wait.until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
    
#ASSERTION
successful_payment_message = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
assert successful_payment_message.text == config.get('success_message')
    
#QUIT BROWSER
Driver.quit_instance()

@classmethod
def get_URL(cls,table_number):
    base_url = 'https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/{}/_/_/ec10b51db5'
    modified = base_url.format(table_number)
    return modified    
    
'''
