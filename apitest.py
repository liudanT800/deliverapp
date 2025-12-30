import requests as rq
import json

def search_location(keys:str) -> dict:
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "keywords": keys,
        "types": "",
        "city": "杭州",
        "children": "1",
        "offset": "20",
        "page": "1",
        "extensions": "",
        "output": "JSON",
        "key": "481e2e3a2000c73f55e1d130212a8726"
        }
    response = rq.get(url, params=params)
    data = response.json()
    return data
