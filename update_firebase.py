import sys
import requests
import os
import time
import pytz
import json
import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("firebaseKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

DATA_GO_KR_API_KEY = os.environ.get("DATA_GO_KR_API_KEY")
API_URL = "http://apis.data.go.kr/6260000/BusanRainfalldepthInfoService/getRainfallInfo"

now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))


def get_rainfall_info(pageNo=1, numOfRows=25):

    params = {
        "serviceKey": DATA_GO_KR_API_KEY,
        "pageNo": 1,
        "numOfRows": 25,
        "resultType": "json",
    }

    # Get response from API (JSON)
    response = requests.get(API_URL, params=params)

    if response.status_code != 200 or response.text[0] == '<':
        while response.status_code != 200 or response.text[0] == '<':
            print("API Error: ", response.status_code)
            time.sleep(1)
            response = requests.get(API_URL, params=params)

    # Parse JSON
    data = json.loads(response.text)

    return data


def add_data_to_firebase(data):
    for item in data["getRainfallInfo"]["body"]["items"]["item"]:
        doc_ref = db.collection("rain").document(
            item["timeDay"]).collection("data").document(item["clientName"])

        item = {
            "accRain": item["accRain"],
            "accRainDt": item["timeDay"],
            "lastRainDt": item["lastRainDt"],
            "clientId": item["clientId"],
            "level6": item["level6"],
            "level12": item["level12"],
            "clientName": item["clientName"],
            "createdAt": now,
        }

        doc_ref.set(item)

    return "Data added to Firebase"


data = get_rainfall_info()
result = add_data_to_firebase(data)
print(result)
