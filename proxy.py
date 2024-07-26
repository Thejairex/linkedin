
import random
import time
import requests
import json
import os


class Proxies:
    def __init__(self):
        if not os.path.exists("proxies.json"):
            response = requests.get("https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=json")
            data = response.json()["proxies"]
            
            with open("Data/proxies.json", 'w') as file:
                json.dump(data, file, indent=4)
            self.proxies = json.load(open("Data/proxies.json"))
            del data, response
        else:
            self.proxies = json.load(open("Data/proxies.json"))

    def get_bs4(self):
        proxy = random.choice(self.proxies)
        return {f"{proxy["protocol"]}": f"http://{proxy["proxy"]}",} 
    
    def get(self):
        proxy = random.choice(self.proxies)
        return proxy["proxy"]