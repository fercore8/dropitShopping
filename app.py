import threading
import uvicorn
import uuid
import datetime
from typing import List, Dict
from fastapi import FastAPI, HTTPException

from views import *


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


# start the app
app = FastAPI()

# fetch and download all holidays for the given year. in our example 2021 is the earliest we can fetch
get_holidays()

# add a lock to make sure we don't have issues with multiple requests
deliveries_lock = threading.Lock()

address1 = Address(street='Main Street', line1='123', line2='', country='USA', postcode='12345')  # testing

# Load the courier's timeslots from the static existing JSON file.
with open('courier_timeslots.json', 'r') as f:
    courier_timeslots = json.load(f)


# Load the holidays from a static JSON file
with open('holidays.json', 'r') as f:
    holidays = json.load(f)

# Initialize the deliveries
deliveries = []


@app.get("/resolve-address")  # tested and working leave empty to check if working.
async def resolve_address_handler(
        search_term: str = '38%20Upper%20Montagu%20Street%2C%20Westminster%20W1H%201LJ%2C%20United%20Kingdom') -> \
        Address:
    address = resolve_address(search_term)
    return address


@app.get("/timeslots")  # tested and works locally leave empty to check if working
async def timeslots_handler(
        street: str = 'Main+Street',
        line1: str = '123',
        line2: str = '',
        country: str = 'USA',
        postcode: str = '12345') -> List[Timeslot]:
    # Create an address object from the query parameters
    address = Address(street=street, line1=line1, line2=line2, country=country, postcode=postcode)
    # Calculate the resulted timeslots
    resulted_timeslots = get_resulted_timeslots(courier_timeslots, holidays)
    # Filter the resulted timeslots by the supported addresses
    supported_timeslots = [timeslot for timeslot in resulted_timeslots if address in timeslot['supported_addresses']]
    return supported_timeslots


@app.get("/deliveries")  # test using user john, timeslot_id 12345
async def create_delivery(user: str, timeslot_id: str) -> Delivery:
    # Find the selected timeslot
    timeslot = [timeslot for timeslot in courier_timeslots if timeslot['timeslot_id'] == timeslot_id]
    if not timeslot:
        raise HTTPException(status_code=404, detail="Timeslot not found")

    # Get the first element in the timeslot list (there should only be one element in the list)
    timeslot = timeslot[0]

    # Check if the business capacity has not been exceeded for the day
    daily_capacity = 10
    with deliveries_lock:
        current_day_deliveries = [delivery for delivery in deliveries if
                                  delivery['start_time'].date() == timeslot['start_time'].date()]
        if len(current_day_deliveries) >= daily_capacity:
            raise HTTPException(status_code=400, detail="Business capacity exceeded for the day")

    # Check if the timeslot is still available
    timeslot_capacity = 2
    booked_deliveries = [delivery for delivery in current_day_deliveries if
                         delivery['timeslot_id'] == timeslot_id]
    if len(booked_deliveries) >= timeslot_capacity:
        raise HTTPException(status_code=400, detail="Timeslot is not available")

    # Create a new delivery
    delivery_id = str(uuid.uuid4())
    print(delivery_id)  # for testing
    delivery = {
        'delivery_id': delivery_id,
        'user': user,
        'timeslot': timeslot,
        'status': 'booked'
    }
    deliveries.append(delivery)

    # Return the created delivery
    return Delivery(**delivery)


@app.get("/deliveries/{delivery_id}/complete")  # after creating a delivery, fetch the delivery_id and use it here
async def complete_delivery(delivery_id: str) -> Dict[str, str]:
    # Find the delivery
    delivery = [delivery for delivery in deliveries if delivery['delivery_id'] == delivery_id]
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Update the delivery status
    delivery[0]['status'] = 'completed'
    return {'message': 'Delivery completed successfully'}


@app.get("/deliveries/{delivery_id}/cancel")  # after creating a delivery, fetch the delivery_id and use it here
async def cancel_delivery(delivery_id: str) -> Dict[str, str]:
    # Find the delivery
    delivery = [delivery for delivery in deliveries if delivery['delivery_id'] == delivery_id]
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Remove the delivery from the list
    deliveries.remove(delivery[0])
    return {'message': 'Delivery cancelled successfully'}


@app.get("/deliveries/daily")
async def get_daily_deliveries() -> List[Delivery]:
    # Filter the deliveries by the current date
    today = datetime.date.today()  # for production
    # datetime.date(2022, 1, 1)
    daily_deliveries = [delivery for delivery in deliveries if
                        datetime.datetime.strptime(delivery['timeslot']['start_time'], '%Y-%m-%d').date() == today]

    return daily_deliveries


@app.get("/deliveries/weekly")
async def get_weekly_deliveries() -> List[Delivery]:
    # Filter the deliveries by the current week
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    weekly_deliveries = [delivery for delivery in deliveries if
                         start_of_week <= datetime.datetime.strptime(delivery['timeslot']['start_time'],
                                                                     '%Y-%m-%d').date() <= end_of_week]
    return weekly_deliveries


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8001)
