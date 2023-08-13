from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from driver import Driver
from elements_page import ElementsPage
from selenium.webdriver.support import expected_conditions as EC
from configuration_reader import Configuration

#CREATE DRIVER (it is created outside the methods because we want to use same driver inside all)
driver = Driver.get_instance()

#MAXIMIZE PAGE
driver.maximize_window()

#CREATE CONFIGURATION OBJECT
config = Configuration()

#NUMBER OF TABLE
table_number = 53

#CREATE WAIT OBJECT
wait = WebDriverWait(driver, 50)

#CREATE GLOBAL PAYABLE AMOUNT
payable_amount = None

def test_remove_by_custom():    
    global payable_amount
    #GO TO QR
    location = ElementsPage.get_URL(table_number)    
    driver.get(location)
    
    #WAIT UNTIL LANDING PAGE IS LOADED
    wait.until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    
    #VERIFY LANDIGN PAGE OR NOT
    assert ElementsPage.get_title(driver) == "Qlub_ | "+config.get("restaurant_unique")  
    
    #CLICK PAY THE BILL BUTTON ON LANDING PAGE
    pay_now_button_on_landing = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.pay_now_button_on_landing))
    pay_now_button_on_landing.click()
    
    #WAIT UNTIL BILLING PAGE IS LOADED
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #VERIFY BILLING PAGE OR NOT         
    assert ElementsPage.get_title(driver) == 'Qlub_ | Invoice '+config.get("restaurant_unique")+', Table '+str(table_number)
    
    #GET PAYABLE AMOUNT
    payable_amount = ElementsPage.get_payable_amount(driver)
    
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLICK ON SPLIT BY CUSTOM BUTTON
    split_by_custom_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_by_custom_button))
    split_by_custom_button.click()
    
    #ENTER CUSTOM AMOUNT
    custom_amount_input_box = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.custom_amount_input_box))
    custom_amount_input_box.send_keys('5')
    
    #CLICK CONFIRM BUTTON
    confirm_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.confirm_button))
    confirm_button.click()
    
    #SCROLL UP TO THE TOP OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.HOME)
    
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #REMOVE SPLIT
    remove_split_button = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.remove_split_button))
    remove_split_button.click()
    
    #WAIT FOR PAYABLE AMOUNT IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #SCROLL DOWN TO THE END OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
    
    #WAIT YOU PAY IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.you_pay)) 
    
    #GET YOU PAY
    you_pay = ElementsPage.get_you_pay(driver)
    
    #VERIFY THAT SPLIT IS REMOVED
    assert payable_amount == you_pay    
    
def test_remove_by_item():
    global payable_amount
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLICK ON SPLIT BY ITEM BUTTON
    split_by_item_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_by_item_button))
    split_by_item_button.click()
    
    #CHOOSE ITEM
    select_item_button = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.get_choose_items(1)))
    select_item_button.click()
    
    #REMOVE SPLIT
    remove_split_button = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.remove_split_button))
    remove_split_button.click()
    
    #WAIT FOR PAYABLE AMOUNT IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #SCROLL DOWN TO THE END OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
    
    #WAIT YOU PAY IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.you_pay))
    
    #GET YOU PAY
    you_pay = ElementsPage.get_you_pay(driver)
    
    #VERIFY THAT SPLIT IS REMOVED
    assert payable_amount == you_pay 
    
def test_remove_by_share():
    global payable_amount
    #CLICK ON SPLIT THE BILL BUTTON
    split_the_bill_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_the_bill_button))
    split_the_bill_button.click()
    
    #CLICK ON SPLIT BY SHARE BUTTON
    split_by_share_button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(ElementsPage.split_by_share_button))
    split_by_share_button.click()
    
    #REMOVE SPLIT
    remove_split_button = WebDriverWait(driver, 60).until(EC.visibility_of_element_located(ElementsPage.remove_split_button))
    remove_split_button.click()
    
    #WAIT FOR PAYABLE AMOUNT IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.payable_amount))
    
    #SCROLL DOWN TO THE END OF THE PAGE
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.END)
    
    #WAIT YOU PAY IS VISIBLE
    wait.until(EC.visibility_of_element_located(ElementsPage.you_pay))
    
    #GET YOU PAY
    you_pay = ElementsPage.get_you_pay(driver)
    
    #VERIFY THAT SPLIT IS REMOVED
    assert payable_amount == you_pay    
    
    #QUIT BROWSER
    Driver.quit_instance()