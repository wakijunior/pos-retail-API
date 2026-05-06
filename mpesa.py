import time
import math
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os


load_dotenv()

consumerKey = os.getenv("consumerKey")
consumerSecret = os.getenv("consumerSecret")
saf_api_url = os.getenv("saf_api_url")
saf_stk_push_url = os.getenv("saf_stk_push_url")
shortCode = os.getenv("shortCode")
passKey = os.getenv("passKey")
my_callback_url = os.getenv("my_callback_url")

#time will be sent to the stk push 
#the reuest is for sending http like axios
#math is for converting floats to the nearest integer
#base64 is for encoding the password to base64 format
#httpBasicAuth is for authenticating the request to get the access token

def get_mpesa_access_token():
    try:
        res = requests.get(
            saf_api_url,
            auth=HTTPBasicAuth(consumerKey, consumerSecret),
        )
        token = res.json()['access_token']

    except Exception as e:
        print(str(e), "error getting access token")
        raise e

    return token

mpesaToken = get_mpesa_access_token()

print(mpesaToken)

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

headers = {
            "Authorization": f"Bearer {mpesaToken}",
            "Content-Type": "application/json"
        }

def generate_password():
    password_str = shortCode + passKey + timestamp
    password_bytes = password_str.encode()
    
    return base64.b64encode(password_bytes).decode("utf-8")

password = generate_password()
print(password)

def make_stk_push(payload):
        print("Payload:--------", payload)
        amount = payload['amount']
        phone_number = payload['phone_number']

        push_data = {
            "BusinessShortCode": shortCode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(amount)),
            "PartyA": phone_number,
            "PartyB": shortCode,
            "PhoneNumber": phone_number,
            "CallBackURL": my_callback_url,
            "AccountReference": "Whatever you call your app",
            "TransactionDesc": "description of the transaction",
        }

        response = requests.post(
            saf_stk_push_url,
            json=push_data,
            headers=headers)

        response_data = response.json()
        print("STK Push Response:--------", response_data)

        return response_data
