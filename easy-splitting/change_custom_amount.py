from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from driver import Driver
from elements_page import ElementsPage
from selenium.webdriver.support import expected_conditions as EC
from configuration_reader import Configuration

table_number = 50
custom_amount_1 = '3.00'
custom_amount_2 = '5.00'

def test_change_custom_amount():  
       
    #CREATE DRIVER    
    driver = Driver.get_instance()
    
    #CREATE WAIT
    wait = WebDriverWait(driver, 50)
    
    #CREATE CONFIGURATION OBJECT
    config = Configuration()
    
    #MAXIMIZE PAGE
    driver.maximize_window()
    
    #GO TO QR
    location = ElementsPage.get_URL(table_number)    
    driver.get(location) 
    
    #WAIT UNTIL LANDING PAGE IS LOADED
    wait.until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    
    #VERIFY LANDING PAGE OR NOT
    assert ElementsPage.get_title(driver) == "Qlub_ | "+config.get("restaurant_unique")  
    
    #CLICK PAY THE BILL BUTTON ON LANDING PAGE
    pay_now_button_on_landing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    pay_now_button_on_landing.click()
    
    #WAIT UNTIL BILLING PAGE IS LOADED
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #VERIFY BILLING PAGE OR NOT         
    assert ElementsPage.get_title(driver) == 'Qlub_ | Invoice '+config.get("restaurant_unique")+', Table '+str(table_number)
    
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLICK ON CUSTOM SPLIT BUTTON
    split_by_custom_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_by_custom_button))
    split_by_custom_button.click()
    
    #ENTER CUSTOM AMOUNT
    custom_amount_input_box = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.custom_amount_input_box))
    custom_amount_input_box.send_keys(custom_amount_1)
    
    #CLICK CONFIRM BUTTON
    confirm_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.confirm_button))
    confirm_button.click()
    
    #WAIT UNTIL YOU PAY IS VISIBLE
    wait.until(EC.visibility_of_element_located((ElementsPage.you_pay)))
    
    #VERIFY YOU PAY
    assert ElementsPage.get_you_pay(driver) == custom_amount_1
    
    #SCROLL UP TO THE TOP OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.HOME)
    
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLEAR INPUT BOX
    custom_amount_input_box = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.custom_amount_input_box))
    custom_amount_input_box.send_keys(Keys.BACK_SPACE)
    
    #ENTER CUSTOM AMOUNT
    custom_amount_input_box = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.custom_amount_input_box))
    custom_amount_input_box.send_keys(custom_amount_2)
    
    #CLICK CONFIRM BUTTON
    confirm_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.confirm_button))
    confirm_button.click()
    
    #WAIT UNTIL YOU PAY IS VISIBLE
    wait.until(EC.visibility_of_element_located((ElementsPage.you_pay)))
    
    #VERIFY YOU PAY
    assert ElementsPage.get_you_pay(driver) == custom_amount_2
    
    #QUIT BROWSER
    Driver.quit_instance()