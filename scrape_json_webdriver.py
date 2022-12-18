# DOES NOT WORK, DATA SCRIPT FORMAT HAS CHANGED

from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import date
import pandas as pd
import pgeocode
import json
import csv

brands = [
    'Mercedes-Benz', 'BMW', 'Toyota', 'Volkswagen', 'Audi',
    'Renault', 'Subaru', 'Nissan', 'Porsche', 'Volvo', 'Land Rover', 'Mazda',
    'Mitsubishi', 'Alfa Romeo', 'Lexus', 'Skoda', 'Honda'
]

# url of search results (page 1)
query = "lst/{}?sort=price&asc=0&ustate=N,U&atype=C&cy=B&priceto=8000"

# for getting distance
distance = pgeocode.GeoDistance('BE')
zip_code = '2910'

# for getting age
today = date.today()

base_url = 'https://www.autoscout24.be/nl/'
driver = webdriver.Chrome('chromedriver.exe')
driver.maximize_window()

# full json data for listings
data = []

# reduce json data to relevant data
def handleListing(l):
    try:
        # calculate distance
        listing_zip_code = l['location']['zip']
        dis = distance.query_postal_code(zip_code, listing_zip_code)

        # calculate vehicle age in days
        reg_date_str = l['tracking']['firstRegistration']
        if reg_date_str in ['new', 'unknown']:
            reg_age = 0
        else:
            month, year = reg_date_str.rsplit('-')
            reg_date = date(int(year), int(month), 1)
            reg_age = (today - reg_date).days

        # listing age in days
        listing_date_str = l['createdTimestampWithOffset']
        year, month, day = listing_date_str[:10].rsplit('-')
        listing_date = date(int(year), int(month), int(day))
        listing_age = (today - listing_date).days

        # return as dict
        return {
            'guid': l['id'],
            'make': l['vehicle']['make'],
            'model': l['vehicle']['model'],
            'vehicle-type': l['vehicle']['bodyType']['formatted'],
            'seller-type': l['seller']['type'],
            'price': l['prices']['public']['priceRaw'],
            'fuel-type': l['tracking']['fuelType'],
            'mileage': l['tracking']['mileage'],
            'year': l['tracking']['firstRegistration'],
            'img-url': l['images'][0],
            'zip-code': listing_zip_code,
            'distance': dis,
            'reg-age': reg_age,
            'listing-age': listing_age,
        }
    except:
        return None

for brand in brands:
    brand_listings = []

    # brand results url
    url = base_url + query.format(brand.lower().replace(' ','-'))

    # iterate pages
    page = 1
    while True:
        print('page', page)

        driver.get(url + "&page=" + str(page))
        driver.implicitly_wait(1)
        elements = driver.find_elements(By.ID, '__NEXT_DATA__')
        if not elements:
            print('not elements')
            break
        script = elements[0].get_attribute("innerHTML")
        page_data = json.loads(script)
        page_listings = page_data['props']['pageProps']['listings']

        # if max page count is reached, start over with current price as minimum
        if page == 20:
            if len(page_listings) == 20:
                print('len(page_listings) == 20')
                print(page_listings)
                price = page_listings[19]['prices']['public']['priceRaw']
                url = base_url + query.format(brand.lower()) + "&pricefrom=" + str(price)
                page = 1
            else:
                break
        else:
            page += 1

        if page_listings:
            if brand_listings and brand_listings[-1] == page_listings[-1]:
                print('get fucked')
                break
            else:
                brand_listings.extend(page_listings)
        else:
            break

    formatted = [x for x in map(handleListing, brand_listings) if x is not None]
    df = pd.DataFrame(formatted) 
    df.to_csv("listings/" + brand + ".csv", index=False, encoding='utf-8')

driver.close()

# formatted = [x for x in map(handleListing, data) if x is not None]

# # store as CSV
# fn = "".join(brands)
# df = pd.DataFrame(formatted) 
# df.to_csv("csv/" + fn + ".csv", index=False, encoding='utf-8')

# store JSON data
# file_name = query.replace('/', '').replace('?', '') + '.json'
# file = open("json/" + file_name, 'a')
# file.write(json.dumps(data))
