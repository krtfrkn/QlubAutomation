from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from driver import Driver
from elements_page import ElementsPage
from selenium.webdriver.support import expected_conditions as EC
from configuration_reader import Configuration

table_number = 52

def test_first_participant_payment_partially():    
   
    #CREATE DRIVER    
    driver = Driver.get_instance()
    
    #CREATE CONFIGURATION OBJECT
    config = Configuration()
    
    #MAXIMIZE PAGE
    driver.maximize_window()
    
    #GO TO QR
    location = ElementsPage.get_URL(table_number)    
    driver.get(location)
    
    #WAIT UNTIL LANDING PAGE IS LOADED
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    
    #VERIFY LANDING PAGE OR NOT
    assert ElementsPage.get_title(driver) == "Qlub_ | "+config.get("restaurant_unique")
    
    #CLICK PAY THE BILL BUTTON ON LANDING PAGE
    pay_now_button_on_landing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    pay_now_button_on_landing.click()
    
    #WAIT UNTIL BILLING PAGE IS LOADED
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #VERIFY BILLING PAGE OR NOT         
    assert ElementsPage.get_title(driver) == 'Qlub_ | Invoice '+config.get("restaurant_unique")+', Table '+str(table_number)
    
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLICK ON SPLIT BY SHARE BUTTON
    split_by_share_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_by_share_button))
    split_by_share_button.click()
    
    #CLICK CONFIRM BUTTON
    confirm_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.confirm_button))
    confirm_button.click()
    
    #SCROLL DOWN TO THE END OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
            
    #SWITCH TO IFRAME
    wait.until(EC.visibility_of_element_located((By.XPATH,config.get('iframe_element'))))
    driver.switch_to.frame(driver.find_element(By.XPATH,config.get('iframe_element')))
    
    #ENTER CARD NUMBER
    card_number_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_number_input))
    card_number_input.send_keys(config.get('visa_card'))
    
    #ENTER EXPIRED DATE
    card_expired_date_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_expired_date_input))
    card_expired_date_input.send_keys(config.get('expired_date'))
    
    #ENTER CVC
    card_cvc_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_cvc_input))
    card_cvc_input.send_keys(config.get('cvc'))
    
    #SWITCH TO DEFAULT CONTENT
    driver.switch_to.default_content()    
    
    #CLICK PAY NOW
    pay_now_button_on_billing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_billing))
    pay_now_button_on_billing.click()
    
    #WAIT UNTIL SUCCESSFUL MESSAGE
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
    
    #ASSERTION
    successful_payment_message = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
    assert successful_payment_message.text == config.get('success_message')
    
    #QUIT BROWSER
    Driver.quit_instance()
    
def test_second_participant_payment_fully():    
    
    #CREATE DRIVER
    driver = Driver.get_instance()
    
    #CREATE CONFIGURATION OBJECT
    config = Configuration()
    
    #MAXIMIZE PAGE
    driver.maximize_window()
    
    #GO TO QR
    location = ElementsPage.get_URL(table_number) 
    driver.get(location)
    
    #WAIT UNTIL LANDING PAGE IS LOADED
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    
    #VERIFY LANDING PAGE OR NOT
    assert ElementsPage.get_title(driver) == "Qlub_ | "+config.get("restaurant_unique")
    
    #CLICK PAY THE BILL BUTTON ON LANDING PAGE
    pay_now_button_on_landing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    pay_now_button_on_landing.click()
    
    #WAIT UNTIL BILLING PAGE IS LOADED
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #VERIFY BILLING PAGE OR NOT         
    assert ElementsPage.get_title(driver) == 'Qlub_ | Invoice '+config.get("restaurant_unique")+', Table '+str(table_number)
    
    #SCROLL DOWN TO THE END OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
            
    #SWITCH TO IFRAME
    wait.until(EC.visibility_of_element_located((By.XPATH,config.get('iframe_element'))))
    driver.switch_to.frame(driver.find_element(By.XPATH,config.get('iframe_element')))
    
    #ENTER CARD NUMBER
    card_number_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_number_input))
    card_number_input.send_keys(config.get('visa_card'))
    
    #ENTER EXPIRED DATE
    card_expired_date_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_expired_date_input))
    card_expired_date_input.send_keys(config.get('expired_date'))
    
    #ENTER CVC
    card_cvc_input = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.card_cvc_input))
    card_cvc_input.send_keys(config.get('cvc'))
    
    #SWITCH TO DEFAULT CONTENT
    driver.switch_to.default_content()    
    
    #CLICK PAY NOW
    pay_now_button_on_billing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_billing))
    pay_now_button_on_billing.click()
    
    #WAIT UNTIL SUCCESSFUL MESSAGE
    wait = WebDriverWait(driver, 50)
    wait.until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
    
    #ASSERTION
    successful_payment_message = WebDriverWait(driver, 50).until(EC.visibility_of_element_located(ElementsPage.successful_payment_message))
    assert successful_payment_message.text == config.get('success_message')
    
    #QUIT BROWSER
    Driver.quit_instance()