import http.client
import json
from .misc import add_slash_if_needed
from .constants import *
from .store import *
from ..lib import fusion360utils as futil

def getToken():
    return loadVariable(INPUT_API_TOKEN)

def getSecret():
    return loadVariable(INPUT_API_SECRET,"xx")

def getApiEndpoint():
    return add_slash_if_needed(loadVariable(INPUT_API_URL))

def split_url(url):
    # Remove http:// or https:// if present
    url = url.replace("http://", "").replace("https://", "")

    # Split URL into host and path
    if '/' in url:
        host, path = url.split('/', 1)
        path = '/' + path  # Add back the leading slash
    else:
        host = url
        path = '/'

    return host, path


def make_api_request(url, token):
    
    
    
    
    futil.log("Request: %s %s" % (url, token))
    
    host, path = split_url(url)
    
    # Establish connection to the API server
    if url.startswith("https://"):    
        sanitized_url = url.replace("https://","")
        futil.log("sanitized_url: %s" % sanitized_url)
        connection = http.client.HTTPSConnection(host, timeout=2)
    else:
        sanitized_url = url.replace("http://","")
        futil.log("sanitized_url: %s" % sanitized_url)
        connection = http.client.HTTPConnection(host, timeout=2)

    # Define headers including Authorization
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json',
        'GreenAiToken': getSecret()
    }

    # Send GET request
    connection.request('GET', path, headers=headers)

    # Get response
    response = connection.getresponse()
    
    # Check if the request was successful
    if 200 <= response.status <= 301:
        # Read response data        
        futil.log("Request successful!")
    else:
        futil.log(f"Request failed with status code: {response.status}")
        raise Exception(f"Request failed with status code: {response.status}")

    # Read response data
    response_data = response.read().decode()

    # Print response
    return response_data


def getCustomers():
    url = getApiEndpoint() + "ui/customers/"
    try:
        data = json.loads(make_api_request(url, getToken()))
    except:
        futil.log("Could not load customers..")
        return []
    return data
    #futil.log(data)
    
    
def getInsoles(customer_id):
    url = getApiEndpoint() + "ui/insoles/?customer=%s" % customer_id
    try:
        data = json.loads(make_api_request(url, getToken()))
    except:
        futil.log("Could not load Insoles..")
        return []
                          
    return data


def getInsole(insole_id):
    url = getApiEndpoint() + "ui/insoles/%s/insole/" % insole_id
    data = json.loads(make_api_request(url, getToken()))
    return data


def getParticipants():
    url = getApiEndpoint() + "ui/participants/"
    try:
        data = json.loads(make_api_request(url, getToken()))
    except:
        futil.log("Could not load Participants..")
        return []
    return data
    #futil.log(data)
    

def getParticipantInsole(public_id):
    url = getApiEndpoint() + "ui/participants/%s/insole/" % public_id
    data = json.loads(make_api_request(url, getToken()))
    return data
    #futil.log(data)