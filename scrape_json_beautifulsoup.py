import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import pgeocode
import csv

MAX_PRICE = 10000

BRANDS = [
    'Mercedes-Benz', 'BMW', 'Toyota', 'Volkswagen', 'Audi',
    'Renault', 'Subaru', 'Nissan', 'Porsche', 'Volvo', 'Land Rover', 'Mazda',
    'Mitsubishi', 'Alfa Romeo', 'Lexus', 'Skoda', 'Honda'
]

# url of search results
query = "lst/{}?sort=price&asc=0&ustate=N,U&atype=C&cy=B&priceto={}"

base_url = 'https://www.autoscout24.be/nl/'

# for getting distance
distance = pgeocode.GeoDistance('BE')
zip_code = '2910'

# for getting age
today = date.today()

# full json data for listings
data = []

# reduce json data to relevant data
def handleListing(l):
    # try:
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
        # listing_date_str = l['createdTimestampWithOffset']
        # year, month, day = listing_date_str[:10].rsplit('-')
        # listing_date = date(int(year), int(month), int(day))
        # listing_age = (today - listing_date).days

        # return as dict
        return {
            'guid': l['id'],
            'make': l['vehicle']['make'],
            'model': l['vehicle']['model'],
            'version': l['vehicle']['modelVersionInput'],
            'seller-type': l['seller']['type'],
            'price': l['tracking']['price'],
            'fuel-type': l['tracking']['fuelType'],
            'mileage': l['tracking']['mileage'],
            'first-reg-date': l['tracking']['firstRegistration'],
            # 'listing-date': l['createdTimestampWithOffset'],
            'zip-code': l['location']['zip'],   
            'images': ' '.join(l['images']),
            'distance': dis,
            'reg-age': reg_age,
            # 'listing-age': listing_age
        }
    # except:
    #     return None

for brand in BRANDS:
    print("scraping {} listings".format(brand))

    brand_listings = []

    # brand results url
    brand_query = brand.lower().replace(' ','-')
    url = base_url + query.format(brand_query, MAX_PRICE)

    # iterate pages
    page = 1
    while True:
        page_url = url + "&page=" + str(page)
        html = requests.get(page_url)
        soup = BeautifulSoup(html.content, 'html.parser')

        data_script = soup.find(id="__NEXT_DATA__")

        if data_script is None:
            print('unable to get data')
            break

        data_string = data_script.string
        page_data = json.loads(data_string)
        page_listings = page_data['props']['pageProps']['listings']

        # if max page count is reached, start over with current price as minimum
        if page == 20:
            if len(page_listings) == 20:
                price = page_listings[19]['tracking']['price']
                url = base_url + query.format(brand_query, MAX_PRICE) + "&pricefrom=" + str(price)
                page = 0
                
                print('\treached end of results, setting new min price to', price)
            else:
                break

        page += 1

        if page_listings:
            brand_listings.extend(page_listings)
        else:
            break

    # save brand listings
    formatted = [x for x in map(handleListing, brand_listings) if x is not None]
    print("\tconverted {} out of {} listings".format(len(formatted), len(brand_listings)))
    print("\tsaving listings")
    df = pd.DataFrame(formatted) 
    df.to_csv("listings/" + brand + ".csv", index=False, encoding='utf-8')

# # store as CSV
# fn = "".join(brands)
# df = pd.DataFrame(formatted) 
# df.to_csv("csv/" + fn + ".csv", index=False, encoding='utf-8')

# store JSON data
# file_name = query.replace('/', '').replace('?', '') + '.json'
# file = open("json/" + file_name, 'a')
# file.write(json.dumps(data))
