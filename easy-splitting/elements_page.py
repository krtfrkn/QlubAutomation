from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElementsPage:
         
    pay_now_button_on_landing = By.XPATH, '//span[@class="wrapper"]/span'
    
    split_the_bill_button = By.XPATH, '(//button[@type="submit"])[1]'
    
    split_by_custom_button = By.ID, 'select-custom'
    
    split_by_item_button = By.ID, 'select-byItem'
    
    split_by_share_button = By.ID, 'select-byShare'
    
    custom_amount_input_box = By.XPATH, '//input[@inputmode="decimal"]'
    
    confirm_button = By.XPATH,'//span[.="Confirm"]'    
    
    edit_split_button = By.XPATH, "//span[.='Edit split']/parent::*"
    
    remove_split_button = By.ID, 'remove-split'
    
    pay_full_bill_button = By.ID, 'pay-full-bill'
    
    card_number_input = By.ID, 'Field-numberInput'
    
    card_expired_date_input = By.ID, 'Field-expiryInput'
    
    card_cvc_input = By.ID, 'Field-cvcInput'
    
    pay_now_button_on_billing = By.XPATH, '//span[.="Pay Now"]/parent::*'
    
    successful_payment_message = By.XPATH, '//p[.="Payment was successful!"]'
    
    title_element = By.TAG_NAME, 'title'
    
    payable_amount = By.XPATH, '(//div[@data-testid="cardContent"]/span)[1]'
    
    you_pay = By.XPATH, '(//div[@data-testid="cardContent"]/span)[2]'
    
    @classmethod
    def get_URL(cls,table_number):
        url = {
        50: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/50/_/_/ec10b51db5",
        51: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/51/_/_/8b0c4bec3b",
        52: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/52/_/_/c46ceee4c5",
        53: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/53/_/_/ea6e5cf198",
        54: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/54/_/_/6b11313607",
        55: "https://app-staging.qlub.cloud/qr/ae/dummyStripeSezai/55/_/_/b3b23292cd"
        }
        return url.get(table_number)
    
    @classmethod
    def get_choose_items(cls,num_of_item):
        element = 'add-item-{}'
        modified_element = element.format(num_of_item)
        select_item_button = By.ID, modified_element
        return select_item_button
    
    @classmethod
    def get_title(cls, driver):
        wait = WebDriverWait(driver, 10)
        title_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        page_title = title_element.get_attribute("text")
        return page_title
    
    @classmethod
    def get_you_pay(cls, driver):
        wait = WebDriverWait(driver, 10)
        you_pay_element = wait.until(EC.presence_of_element_located((By.XPATH, '(//div[@data-testid="cardContent"]/span)[2]')))
        you_pay_amount = you_pay_element.text.split("AED", 1)[-1]
        return you_pay_amount
    
    @classmethod
    def get_payable_amount(cls, driver):
        wait = WebDriverWait(driver, 10)
        you_pay_element = wait.until(EC.presence_of_element_located((By.XPATH, '(//div[@data-testid="cardContent"]/span)[1]')))
        you_pay_amount = you_pay_element.text.split("AED", 1)[-1]
        return you_pay_amount