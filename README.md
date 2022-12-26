# Home Assignment DropitShopping (to Rotem)

## INTRO 
### I went with an approach that makes this a simple fastapi app using json for ease of setup for now...
I did do my best to create the methods in a good way, tweaking to improve should be added. The task at least to me is not a short one, taking into consideration that there are two
basic api implementations, various endpoints, etc. I appreciate the opportunity given for the home assignment and I
hope it's ok.
I had no time for creating a tests folder in order to test all the methods.

## SETUP
### venv and installing dependencies
1. clone repository
2. python -m venv myenv
3. myenv\Scripts\activate.bat
4. pip install -r requirements.txt 

## USAGE
### run the uvicorn server:
uvicorn main:app --reload --host 0.0.0.0 --port 8080

## endpoints:
### /resolve-address?search_term=  leave empty for testing
takes an address and returns it in the right format.

### /timeslots  leave empty for testing
takes an address and checks availabilty

### /deliveries?user=John&timeslot_id=12345  as an example
takes a user name and a timeslot_id . if it exists it will generate a delivery

### /deliveries/{delivery_id}/complete 
takes a delivery_id after a delivery is created. marks delivery as complete

### /deliveries/{delivery_id}/cancel 
takes a delivery_id after a delivery is created. marks delivery as cancelled

### /deliveries/daily
returns a list of daily tasks

### /deliveries/weekly
returns a list of this weeks tasks