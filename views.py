import os
from dotenv import load_dotenv
import json
import requests
from requests.structures import CaseInsensitiveDict
import holidayapi
from pydantic import BaseModel
from typing import List, Dict


load_dotenv()
HOLIDAYAPI_KEY = os.getenv('HOLIDAYAPI_KEY')
GEOAPI_KEY = os.getenv('GEOAPI_KEY')
'''I went with an approach that makes this a simple fastapi app using json for ease of setup for now...'''


# Let's write the models
class Address(BaseModel):
    street: str
    line1: str
    line2: str
    country: str
    postcode: str


class Timeslot(BaseModel):
    start_time: str
    end_time: str
    supported_addresses: List[Address]


class Delivery(BaseModel):
    delivery_id: str
    user: str
    timeslot: Timeslot
    status: str


# validate address and return an Address object
def resolve_address(search_term: str) -> Address:
    headers = CaseInsensitiveDict()
    headers['Accept'] = 'application/json'
    with requests.get(f'https://api.geoapify.com/v1/geocode/search?text={search_term}&apiKey={GEOAPI_KEY}',
                      headers=headers) as resp:
        response_text = resp.text
        # Parse the response text into a JSON object
        response_data = json.loads(response_text)

        # Extract the address information from the response data
        address_data = response_data['features'][0]['properties']
        street = address_data['street']
        line1 = address_data['housenumber']
        line2 = address_data['suburb']
        postcode = address_data['postcode']
        country = address_data['country']
        # Create and return an Address model object
        return Address(street=street, line1=line1, line2=line2, country=country, postcode=postcode)


# can only extract data for last year. lets flow with it...
def get_holidays(year: str = '2021'):
    hapi = holidayapi.v1(HOLIDAYAPI_KEY)

    parameters = {'country': 'US', 'year': year}

    holidays_response = hapi.holidays(parameters)

    # Save the holiday dates in the database
    with open('holidays.json', 'w') as f:
        json.dump({'holidays': holidays_response['holidays']}, f)
        return holidays_response['holidays']


with open('courier_timeslots.json', 'r') as f:
    courier_timeslots = json.load(f)

with open('holidays.json', 'r') as f:
    holidays = json.load(f)

# Calculate the resulted timeslots by intersecting the courier's timeslots
# and the non-holiday timeslots
def get_resulted_timeslots(courier_timeslots: List[Timeslot], holidays) -> List[Timeslot]:
    resulted_timeslots = []
    for timeslot in courier_timeslots:
        start_time = timeslot['start_time']
        end_time = timeslot['end_time']
        if start_time not in holidays and end_time not in holidays:
            resulted_timeslots.append(timeslot)
    return resulted_timeslots


if __name__ == '__main__':
    # get_holidays('2021')
    get_resulted_timeslots(courier_timeslots, holidays)
