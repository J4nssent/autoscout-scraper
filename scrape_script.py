from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
import pandas as pd
import pgeocode
import json

# url of search results (page 1)
query = "lst/audi?offer=U&sort=standard&desc=0&cy=B&atype=C&ustate=N%2CU&fuel=B&powertype=kw&adage=14&search_id=g5o2ja6vlu"

# for getting distance
distance = pgeocode.GeoDistance('BE')
zip_code = '2910'

# for getting age
today = date.today()

base_url = 'https://www.autoscout24.be/nl/'
driver = webdriver.Chrome("chromedriver")
driver.get(base_url + query)

# wait for site to be rendered
driver.implicitly_wait(1)

# get page count
last_page_button = driver.find_element(By.XPATH, "//nav[@class='scr-pagination FilteredListPagination_pagination__q28U0']/ul/li[last()-2]/button")
page_count = int(last_page_button.text)

# string to hold data
data = []

# data to get from the article element
article_attributes = {
    'guid': 'data-guid',
    'make': 'data-make',
    'model': 'data-model',
    'vehicle-type': 'data-vehicle-type',
    'seller-type': 'data-seller-type',
    'price': 'data-price',
    'zip-code': 'data-listing-zip-code',
    'fuel-type': 'data-fuel-type',
    'mileage': 'data-mileage',
    'year': 'data-first-registration'
}

element = driver.find_element(By.ID, '__NEXT_DATA__')
script = element.get_attribute("innerHTML")

print(element.text)
print(script)

# store data
file_name = query.replace('/', '').replace('?', '') + '.json'
file = open("json/" + file_name, 'a')
file.write(script)



driver.close()
