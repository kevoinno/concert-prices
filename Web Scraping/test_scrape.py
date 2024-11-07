from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

# Specify paths and driver
PATH = "C:\\Program Files (x86)\\chromedriver.exe"
service = Service(PATH)
driver = webdriver.Chrome(service=service)

# Specify website to scrape
WEBSITE = 'https://www.ticketmaster.com/event/Z7r9jZ1A7o7qI'

# Open website
driver.get(WEBSITE)

BUTTON_XPATH = "//*[@id='modalContent']/div[3]/div/button"
try:   
    # Press Accept and Continue Button
    button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, BUTTON_XPATH)))
    button.click()
    print("Pressed Accept Button")

    # Search for Lowest Price
    try:
        price = driver.find_element(By.XPATH, "//*[@id='quickpick-buy-button-qp-0']")
        price_output = price.text.replace('$', '')
        print(price_output)
    except Exception as e:
        print("Could not find price", e)

except Exception as e:
    print('Could not find button', e)

time.sleep(5)

driver.close()

