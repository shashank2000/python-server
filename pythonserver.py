from flask import Flask
import requests
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

RESULTS = 'results'
BILLS = 'bills'
DESCRIPTION = 'description'
GOOGLE_API_KEY = 'AIzaSyA6msAMADzxXZxANboADutjj6RkQSPAyuA'

@app.route("/")
def hello():
    header_data = {'X-API-Key' : 'uxPHJm5m3RLJn1UrnpcX6VkNNFsCALUmv5xb3Mvb'}
    data = requests.get('https://api.propublica.org/congress/v1/bills/upcoming/house.json', headers=header_data)
    data = data.json()
    myDict = {}
    for item in data[RESULTS][0][BILLS]:
        billDescription = item[DESCRIPTION]
        billno = item['bill_number']
        googlepage = requests.get("https://www.google.com/search?q="+billno)
        soup = BeautifulSoup(googlepage.content)
        if soup.find(id="resultStats"):
            aboutStuff = soup.find(id="resultStats").text
            associatedNumber = aboutStuff.split("About ")[1].split(" results")[0].replace(',', '')
        else:
            associatedNumber = 1
        myDict[billDescription] = int(associatedNumber)
    sorted_dict = sorted(myDict, reverse=True)
    return json.dumps(sorted_dict)

@app.route("/latlng/<lat>/<lng>")
def latlng(lat, lng):
    data = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(lng)+ '&key='+ GOOGLE_API_KEY)

    # Phone2Action
    first_address = get_first_address(data.text)
    # Get senate data
    level = 'NATIONAL_UPPER'
    header_data = {'X-API-Key' : '2e1uvo7yeX50ZGHvctPxi8ZWubhggyOydIWvOa5c'}
    base_url = 'https://q4ktfaysw3.execute-api.us-east-1.amazonaws.com/treehacks/legislators'
    url = base_url + "?address=" + first_address + "&level=" + level
    data = requests.get(url, headers=header_data)
    json_output = json.loads(data.text)
    return get_serialized_data(json_output)

# Input the return value from latlng to this function to get the first address as a string
def get_first_address(data):
    json_response = json.loads(data)
    first_address = json_response['results'][0]['formatted_address']
    return first_address

def get_serialized_data(data):
    officials = data['officials']
    officials_data = []
    for official in officials:
        official_dict = {}
        official_dict['name'] = official['first_name'] + ' ' + official['last_name']
        official_dict['phone_number'] = official['office_location']['phone_1']
        official_dict['state'] = official['office_details']['district']['state']
        officials_data.append(official_dict)
    return json.dumps(officials_data)

