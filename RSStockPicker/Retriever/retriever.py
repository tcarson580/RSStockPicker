'''
Created on Jun 18, 2019

@author: FN-1776
'''

import requests
import datetime
import json
import time
import os

if __name__ == '__main__':
    t0 = time.time()
    itemPriceList = {}
    itemNumber = 1050
    link = "http://services.runescape.com/m=itemdb_rs/api/graph/" + str(itemNumber) + ".json"
    f = requests.get(link)
    loaded_json = json.loads(f.text)
    for date in loaded_json["daily"]:
        price = loaded_json["daily"][date]
        # convert date from milliseconds to YEAR-MO-DA
        date = datetime.datetime.fromtimestamp(float(date)/1000.0).strftime('%Y-%m-%d')
        itemPriceList[date] = price
      
    print(itemPriceList)
    
#     with open('validItemNumbers.txt', 'w') as f:
#         itemNumber = 0
#         while itemNumber < 2000:
#             itemNumberString = str(itemNumber)
#             link = "http://services.runescape.com/m=itemdb_rs/api/graph/" + itemNumberString + ".json"
#             openedLink = requests.get(link)
#             try:
#                 loaded_json = json.loads(openedLink.text)
#                 f.write(itemNumberString + ",") 
#             except:
#                 None
# 
#             itemNumber += 1
#         os.fsync(f.fileno())
        
    t1 = time.time()
    total = t1-t0
    print(total, "seconds")