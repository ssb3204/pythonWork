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

API_URL = "http://apis.data.go.kr/6260000/BusanWaterImrsnInfoService/getWaterImrsnInfo"
BRIDGE_KEY=os.environ.get("BRIDGEKEY")

now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))


def get_waterfall_info(pageNo=1, numOfRows=25):
    params = {
        "serviceKey": BRIDGE_KEY,
        "pageNo": pageNo,
        "numOfRows": numOfRows,
        "resultType": "json",
    }

    # API 호출 및 응답 확인
    response = requests.get(API_URL, params=params)
    while response.status_code != 200 or response.text[0] == '<':
        print("API Error: ", response.status_code)
        time.sleep(1)
        response = requests.get(API_URL, params=params)

    # JSON 응답 파싱
    data = json.loads(response.text)

    return data

def add_data_to_firebase(data):
    for item in data["getWaterImrsnInfo"]["body"]["items"]["item"]:
        obsr_date = item["obsrTime"].split(" ")[0]  # Extract the date part of obsrTime
        obsr_time = item["obsrTime"]

        doc_ref = db.collection("bridge").document(obsr_date).collection("data").document(item["siteName"])
        
        item_data = {
            "siteCode": item["siteCode"],
            "siteName": item["siteName"],
            "alertLevel3": item["alertLevel3"],
            "alertLevel3Nm": item["alertLevel3Nm"],
            "alertLevel4": item["alertLevel4"],
            "alertLevel4Nm": item["alertLevel4Nm"],
            "fludLevel": item["fludLevel"],
            "obsrTime": item["obsrTime"],
            "sttus": item["sttus"],
            "sttusNm": item["sttusNm"],
            "createdAt": now
        }

        doc_ref.set(item_data)

    return "Data added to Firebase"


data = get_waterfall_info()
result = add_data_to_firebase(data)
print(result)
