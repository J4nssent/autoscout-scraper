from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
import pandas as pd
import pgeocode

# url of search results (page 1)
query = "lst/mazda?sort=standard&desc=0&cy=B&atype=C&ustate=N%2CU&powertype=kw"

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

# list to store data
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

# iterate pages
for current_page in range(1, page_count + 1):
    driver.get(base_url + query + "&page=" + str(current_page))
    driver.implicitly_wait(1)

    articles = driver.find_elements(By.TAG_NAME, 'article')

    for e in articles:
        listing_data = {}

        # simple data types
        for key, lookup in article_attributes.items(): 
            listing_data[key] = e.get_attribute(lookup)

        # calculate distance
        listing_zip_code = e.get_attribute('data-listing-zip-code')
        listing_data['distance'] = distance.query_postal_code(zip_code, listing_zip_code)

        # calculate age
        listing_date_str = e.get_attribute('data-first-registration')
        if listing_date_str in ['new', 'unknown']:
            listing_data['age'] = 0
            continue
        month, year = listing_date_str.rsplit('-')
        listing_first_reg = date(int(year), int(month), 1)
        listing_data['age'] = (today - listing_first_reg).days

        # listing image url
        ActionChains(driver).move_to_element(e).perform() # scroll down to load image
        imgs = e.find_elements(By.TAG_NAME, 'source')
        if imgs:
            listing_data['img-url'] = imgs[len(imgs)-1].get_attribute('srcset')
        
        data.append(listing_data)

# store data
file_name = query.replace('/', '').replace('?', '') + '.csv'

df = pd.DataFrame(data) 
df.to_csv('queries/' + file_name, index=False, encoding='utf-8')

driver.close()
