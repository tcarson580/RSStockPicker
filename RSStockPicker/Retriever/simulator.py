import datetime as dt
import time
import requests
import json

class simulator:
    '''
    classdocs
    ''' 
    def __init__(self, maxPurchasePercentage, startingCapital, dataDaysAgo):
        self.maxPurchasePercentage = maxPurchasePercentage
        self.startingCapital = startingCapital
        self.investableCapital = startingCapital
        self.currentNetWorth = startingCapital
     
        self.dataDaysAgo = -1*dataDaysAgo
        self.today = dt.datetime.now()
        self.dateAgo = self.today + dt.timedelta(dataDaysAgo)
        
        self.buyList = {}
        self.currentHeldItems = {}
        self.allItemData = {}
        self.getItemData() 
    
    # Retrieves all dates and prices for given item list for past 180 days
    def getItemData(self):
        itemNumbers = [3138, 453, 1779, 225, 991, 40310, 28445, 28451, 28453, 28447, 28455, 28449]  
        
        for itemNumber in itemNumbers:
            itemPriceList = {}
            link = "http://services.runescape.com/m=itemdb_rs/api/graph/" + str(itemNumber) + ".json"
            f = requests.get(link)
            loaded_json = json.loads(f.text)
            for date in loaded_json["daily"]:
                price = loaded_json["daily"][date]
                # convert date from milliseconds to YEAR-MO-DA
                # if the time is before 1900 UTC, all dates need to be shifted by 1
                if dt.datetime.utcnow().hour < 1900:
                    date = (dt.datetime.fromtimestamp(float(date)/1000.0) + dt.timedelta(1)).strftime('%Y-%m-%d') 
                else:
                    date = dt.datetime.fromtimestamp(float(date)/1000.0).strftime('%Y-%m-%d')
                             
                itemPriceList[date] = price
            self.allItemData[itemNumber] = itemPriceList
        
    # Retrieves all valid item buys for all items in allItemData for the last 180 days until -30 days from today    
    def getBuyList(self):
        daysAgo30 = self.today + dt.timedelta(-30)
        
        for number, item in self.allItemData.items():
            currentItemData = {}
            
            for buyDaysAgo in range(self.dataDaysAgo, -30):   
                buyDateAgo = (self.today + dt.timedelta(buyDaysAgo)).strftime('%Y-%m-%d')
                dateAgo3 = (self.today + dt.timedelta(-3+buyDaysAgo)).strftime('%Y-%m-%d')
                dateAgo6 = (self.today + dt.timedelta(-6+buyDaysAgo)).strftime('%Y-%m-%d')
                dateAgo9 = (self.today + dt.timedelta(-9+buyDaysAgo)).strftime('%Y-%m-%d')
                
                priceToday = int(item[buyDateAgo])
                priceAgo3 = int(item[dateAgo3])
                priceAgo6 = int(item[dateAgo6])
                priceAgo9 = int(item[dateAgo9])
                 
                if priceToday < 0.95*priceAgo3: #and priceToday < 0.97*priceAgo6 and priceToday < 0.97*priceAgo9:
                    currentItemData[buyDateAgo] = priceToday
            
            if currentItemData:      
                self.buyList[number] = currentItemData

        
    def buyItem(self, currentDate):
        currentItem = []
        for number, item in self.buyList.items():
            if currentDate in item and number not in self.currentHeldItems:
                maxPurchase = self.maxPurchasePercentage*self.currentNetWorth
                buyPrice = item[currentDate]
                sellPrice = int(1.1*buyPrice)
                quantity = int(min(maxPurchase/buyPrice, self.investableCapital/buyPrice))
                
                if quantity > 0:
                    currentItem = [currentDate, buyPrice, quantity, sellPrice]
                    self.currentHeldItems[number] = currentItem
                    self.investableCapital -= buyPrice*quantity
            
    def sellItem(self, currentDate):
        itemsToSell = []
        
        for number, currentItem in self.currentHeldItems.items():
            if number in self.buyList and currentDate in self.buyList[number]:
                currentPrice = self.allItemData[number][currentDate]
                buyDate = currentItem[0]
                buyPrice = currentItem[1]
                quantity = currentItem[2]
                sellPrice = currentItem[3]
                if currentPrice >= sellPrice:
                    itemsToSell.append(number)
                    self.investableCapital += int(sellPrice*quantity)
                            
        for number in itemsToSell:
            del self.currentHeldItems[number]
            
    
    def runSimulation(self):
        self.getItemData()
        self.getBuyList()
        
        for day in range(self.dataDaysAgo, 1):
            currentDate = (self.today + dt.timedelta(day)).strftime('%Y-%m-%d')
            self.buyItem(currentDate)
            self.sellItem(currentDate)
            
            # Calculate net worth
            self.currentNetWorth = self.investableCapital
            for number, currentItem in self.currentHeldItems.items():
                currentPrice = self.allItemData[number][currentDate]
                currentQuantity = currentItem[2]
                self.currentNetWorth += currentPrice*currentQuantity
                
        print(self.currentNetWorth)
        

if __name__ == '__main__':
    t0 = time.time()
    
    simulator = simulator(0.05, 170000000.00, 170)
    simulator.runSimulation()
    
    t1 = time.time()           
    total = t1-t0
    print(total, "seconds")  