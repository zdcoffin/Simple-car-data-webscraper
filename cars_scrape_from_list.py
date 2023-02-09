
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from datetime import datetime
import sqlite3
import os

os.chdir("C:/Users/zcoff/OneDrive/Desktop/SQL")

carscomlist_response = requests.get('https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=30000&list_price_min=20000&makes[]=mazda&maximum_distance=75&mileage_max=&models[]=mazda-cx_9&page_size=100&sort=list_price&stock_type=all&trims[]=mazda-cx_9-grand_touring&trims[]=mazda-cx_9-signature&year_max=&year_min=&zip=76205')

carscomlist_webpage = carscomlist_response.content

# full cars.com list of results page
ccl = BeautifulSoup(carscomlist_webpage, 'html.parser')

# list of all the partial vehicle listing links
all_cars = ccl.find_all(attrs={'class':'vehicle-card-link'})

# loops through all the car listings, turns the partial link into a full link, and appends them to a list
car_links = []
for car in all_cars:
    car_partial_link = car.get('href')
    car_full_link = 'https://www.cars.com' + car_partial_link
    car_links.append(car_full_link)

# realized i was requesting the webpage over and over for each new piece of data i needed, so i made a list that contains the webpage data AFTER being requested    
car_webpages = []
for car_link in car_links:
    car_response = requests.get(car_link)
    car_webpage = car_response.content
    car_webpages.append(car_webpage)

# finds the price class after taking the webpage and parsing it with beautifulsoup, finds the price text within the text, strips '$' and ',', then converts it to int type
# for future reference, you must include the BeautifulSoup parser within the function to use beautifulsoups .find() instead of pythons built in .find()
def get_price(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    price_class = car_webpage_final.find(attrs={'class':'primary-price'})
    price_unstripped = (price_class.get_text())
    stripped_price = re.sub('[$,]', '', price_unstripped)
    price = int(stripped_price)
    return price


def get_year(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    ymmt_class = car_webpage_final.find(attrs={'class':'listing-title'})
    ymmt_unstripped = (ymmt_class.get_text())
    year_make_model_trim = ymmt_unstripped.split()
    year_final = year_make_model_trim[0]
    return year_final

def get_make(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    ymmt_class = car_webpage_final.find(attrs={'class':'listing-title'})
    ymmt_unstripped = (ymmt_class.get_text())
    year_make_model_trim = ymmt_unstripped.split()
    make_final = year_make_model_trim[1]
    return make_final

def get_model(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    ymmt_class = car_webpage_final.find(attrs={'class':'listing-title'})
    ymmt_unstripped = (ymmt_class.get_text())
    year_make_model_trim = ymmt_unstripped.split()
    model_final = year_make_model_trim[2]
    return model_final

def get_trim(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    ymmt_class = car_webpage_final.find(attrs={'class':'listing-title'})
    ymmt_unstripped = (ymmt_class.get_text())
    year_make_model_trim = ymmt_unstripped.split()
    trim_final = year_make_model_trim[3:]
    trim_final = ' '.join(trim_final[:])
    return trim_final

def get_miles(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    miles_class = car_webpage_final.find(attrs={'class':'listing-mileage'})
    miles_unstripped = (miles_class.get_text())
    miles_almost = miles_unstripped.replace(',', '')
    miles_split = miles_almost.split()
    miles_final = miles_split[0]
    return miles_final
    
def get_stocknumber(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    giant_data_clump = car_webpage_final.find_all(attrs={'class':'fancy-description-list'})
    data_into_string = str(giant_data_clump)
    data_string_list = data_into_string.split()
    stock_index = data_string_list.index('<dt>Stock')
    stock_index_actual = stock_index + 3
    stock_number_final = data_string_list[stock_index_actual]
    return stock_number_final

# returns a giant string of date changes seperated by commmas
# need to find a way to insert either a graph or a list of the date changes into sql
# FIX
def get_date_changes(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    all_date_changes_list = []
    td_tags = car_webpage_final.find_all('td')
    for tag in td_tags[0::3]:
        all_date_changes_list.append(tag.text)
    empty_string = ", "
    return empty_string.join(all_date_changes_list)

# returns a giant string of price changes seperated by ' --> ' 
# same as above, need to turn into a graph or a list and insert into sql
# FIX
def get_price_changes(car_webpage):
    car_webpage_final = BeautifulSoup(car_webpage, 'html.parser')
    all_price_changes_list = []
    td_tags = car_webpage_final.find_all('td')
    for tag in td_tags[2::3]:
        all_price_changes_list.append(tag.text)
    empty_string = " --> "
    return empty_string.join(all_price_changes_list)
    

# empty dataframe and empty list to add the days listed cars to
cdf = pd.DataFrame()
car_list = []

#starts with an empty dictionary within the loop, essentially creates a row (as a dictionary) for the table, and appends that dictionary/row to a list outside of the loop
count = 0
tl = [1, 2, 3, 4]
for wp in car_webpages:
    cid = {}
    cid['Stock #'] = get_stocknumber(wp)
    cid['Year'] = get_year(wp)
    cid['Make'] = get_make(wp)
    cid['Model'] = get_model(wp)
    cid['Trim'] = get_trim(wp)
    cid['Miles'] = get_miles(wp)
    cid['Price'] = get_price(wp)
    cid['URL'] = car_links[count]
    cid['Date Changes'] = get_date_changes(wp)
    cid['Price Changes'] = get_price_changes(wp)
    car_list.append(cid)
    count += 1

cdf = pd.DataFrame(car_list)   
print(cdf)

#connects to sqlite, saves a .sqlite file to my SQL folder
conn = sqlite3.connect('Car Database.sqlite')
cdf.to_sql('Todays Available Mazda CX9', conn, if_exists='replace', index=False)
conn.close()











    





