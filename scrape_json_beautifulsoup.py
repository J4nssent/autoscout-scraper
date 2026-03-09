import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import time
import pgeocode
import csv
import os

MAX_PRICE = 50000
MAX_DISTANCE = 150
FIRST_REG_DATE = 1965

BODY_TYPES = list(range(1, 15))  # 1 to 14

BRANDS = [
    'BMW', 
    # 'Mercedes-Benz', 
    # 'Toyota', 
    # 'Volkswagen', 
    # 'Audi',
    # 'Subaru', 
    # 'Nissan', 
    # 'Porsche', 
    # 'Volvo', 
    # 'Renault', 
    # 'Land Rover', 
    # 'Mazda',
    # 'Mitsubishi', 
    # 'Alfa Romeo', 
    # 'Lexus', 
    # 'Skoda', 
    # 'Honda',
    # 'Opel',
    # 'Kia',
    # 'Suzuki',
    # 'Hyundai',
    # 'Ford',
    # 'Fiat'
]

# build autoscout search url
base_query = "lst/{}?"

params = {
    "zip": "2910%20Essen",
    "zipr": MAX_DISTANCE,
    "priceto": MAX_PRICE,
    "fregfrom": FIRST_REG_DATE,

    "ustate": "N%2CU",
    "atype": "C",
    # "body": "4%2C5%2C1",  # Will be set per body type
    "damaged_listing": "exclude",
    # "fuel": "2%2CB",
    # "gear": "A",

    "sort": "price",
    "asc": 0
}

def build_query(brand: str, body_type: int = None):
    query_parts = []
    for key, value in params.items():
        if value != -1:
            query_parts.append(f"{key}={value}")
    if body_type is not None:
        query_parts.append(f"body={body_type}")
    return base_query.format(brand) + "&".join(query_parts)


base_url = 'https://www.autoscout24.be/nl/'

# for getting distance
distance = pgeocode.GeoDistance('BE')
zip_code = '2910'

# for getting age
today = date.today()

# full json data for listings
data = []

# reduce json data to dict of relevant data
def handleListing(l, body_type):
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
        # listing_date_str = l['createdTimestampWithOffset'] # field removed from json data
        # year, month, day = listing_date_str[:10].rsplit('-')
        # listing_date = date(int(year), int(month), int(day))
        # listing_age = (today - listing_date).days

        # return as dict
        return {
            'guid': l['id'],
            'make': l['vehicle']['make'],
            'model': l['vehicle']['model'],
            'version': l['vehicle']['modelVersionInput'],
            'transmission': l['vehicle']['transmission'],
            'fuel': l['vehicle']['fuel'],
            'seller-type': l['seller']['type'],
            'price': l['tracking']['price'],
            # 'fuel-type': l['tracking']['fuelType'],
            'mileage': int(l['tracking']['mileage']),
            'first-reg-date': l['tracking']['firstRegistration'],
            # 'listing-date': l['createdTimestampWithOffset'],
            'zip-code': l['location']['zip'],   
            'images': ' '.join(l['images']),
            'distance': int(dis),
            'reg-age': reg_age,
            # 'listing-age': listing_age
            'body-type': body_type
        }
    except:
        return None

# iterate brands
for brand in BRANDS:
    print("Collecting {} listings:".format(brand))

    brand_formatted_listings = []

    # brand results url
    brand_string = brand.lower().replace(' ','-')

    # iterate body types
    for body_type in BODY_TYPES:
        print("\tSearching for body type {}".format(body_type))
        url = base_url + build_query(brand_string, body_type)

        # iterate pages
        page = 1
        tries = 0
        while True:
            page_url = url + "&page=" + str(page)
            html = requests.get(page_url)
            soup = BeautifulSoup(html.content, 'html.parser')

            # JSON script of listings data
            data_script = soup.find(id="__NEXT_DATA__")

            if data_script is None:
                print('\t\tUnable to get data:', page_url)
                if tries > 3:
                    print('\t\tFailed to get data after 3 tries, aborting')
                    break

                print('\t\tWaiting 5 seconds and trying page again...')
                time.sleep(5)
                tries += 1
                continue

            data_string = data_script.string
            page_data = json.loads(data_string)
            page_listings = page_data['props']['pageProps']['listings']
            
            # Reset tries counter after successful request
            tries = 0

            # page limit has been removed
            # if max page count is reached, start over with current price as minimum
            # if page == 20:
            #     if len(page_listings) == 20:
            #         price = page_listings[19]['tracking']['price']
            #         url = base_url + build_query(brand_string) + f"&pricefrom={price}"
            #         page = 0
                    
            #         print('\treached end of results, setting new min price to', price)
            #     else:
            #         break

            page += 1

            if page_listings:
                # Format listings with current body_type immediately
                formatted_page = [x for x in map(lambda l: handleListing(l, body_type), page_listings) if x is not None]
                brand_formatted_listings.extend(formatted_page)
            else:
                break

    # save brand listings
    formatted = brand_formatted_listings
    print("\tCollected {} listings".format(len(formatted)))

    print("\tSaving listings")
    os.makedirs("AutoScrape24/src/data", exist_ok=True)
    out_path = os.path.join("AutoScrape24/src/data", f"{brand}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

print("Finished saving all brands")