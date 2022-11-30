from selenium import webdriver
from selenium.webdriver.common.by import By
import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options, executable_path="chromedriver")

url = 'https://www.autoscout24.be/nl/uitgebreid-zoeken'

driver.get(url)

# submit button
locator = (By.CLASS_NAME, "DetailSearchPage_button__c_w8_")

wait = WebDriverWait(driver, 999)
wait.until(lambda d: not bool(d.find_elements(*locator)))

# print search query
url = driver.current_url
query = re.sub('.+/lst', 'lst', url)
query = re.sub('&search_id=.+', '', query)
print(query)

driver.close()
