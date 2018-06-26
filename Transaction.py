
# coding: utf-8

# In[500]:


from Action import *
from Match import *
from Asset import *

class Transaction(object):
    def __init__(self, startingPrice):
        self.submissions = []
        self.curStep = 0
        self.longOrders = []
        self.shortOrders = []
        self.price = startingPrice
        self.assetTable = {}
        self.matchTable = {}
        self.marginRate = 0.1
        self.feeRate = 0.0000
        self.unit = 100
        
    
    def match(self):
        i = 0
        while i < len(self.submissions):
            order = self.submissions[i]
            i += 1
            if order[1].isPass is 1:
                pass
            elif order[1].isLong is 0:
                if len(self.longOrders) == 0:
                    self.shortOrders.append(order)
                    self.shortOrders.sort(key = lambda x: x[1].bias, reverse = False)
                elif self.longOrders[0][1].bias >= order[1].bias:
                    isMatch = True
                    matchPrice = self.calculatePrice(self.longOrders[0][1].bias)
                    self.price = matchPrice
                    match0 = Match(matchPrice, 1, 1, self.curStep)
                    match1 = Match(matchPrice, 1, 0, self.curStep)
                    self.matchTable[self.longOrders[0][0]] = match0
                    self.matchTable[order[0]] = match1
                    self.upgradeAsset(self.longOrders[0][0], match0)
                    self.upgradeAsset(order[0], match1)
                    del self.longOrders[0]
                else:
                    self.shortOrders.append(order)
                    self.shortOrders.sort(key = lambda x: x[1].bias, reverse = False)
            else:
                if len(self.shortOrders) == 0:
                    self.longOrders.append(order)
                    self.longOrders.sort(key = lambda x: x[1].bias, reverse = True)
                elif self.shortOrders[0][1].bias <= order[1].bias:
                    isMatch = True
                    matchPrice = self.calculatePrice(self.shortOrders[0][1].bias)
                    self.price = matchPrice
                    match0 = Match(matchPrice, 1, 0, self.curStep)
                    match1 = Match(matchPrice, 1, 1, self.curStep)
                    self.matchTable[self.shortOrders[0][0]] = match0
                    self.matchTable[order[0]] = match1
                    self.upgradeAsset(self.shortOrders[0][0], match0)
                    self.upgradeAsset(order[0], match1)
                    del self.shortOrders[0]
                else:
                    self.longOrders.append(order)
                    self.longOrders.sort(key = lambda x: x[1].bias, reverse = True)


                    
    def calculatePrice(self, bias):
        price = None
        if bias is 0:
            price = self.price * (1 - 0.02)
        elif bias is 1:
            price = self.price * (1 - 0.01)
        elif bias is 2:
            price = self.price * (1 - 0.005)
        elif bias is 3:
            price = self.price * (1 + 0.005)
        elif bias is 4:
            price = self.price * (1 + 0.01)
        elif bias is 5:
            price = self.price * (1 + 0.02)
        return price
    
    def upgradeAsset(self, playerId, match):
        if self.assetTable[playerId].positionVolume is 0:
            total = self.assetTable[playerId].total - (match.price * match.volume * self.unit) * self.feeRate
            margin = self.assetTable[playerId].margin - (match.price * match.volume * self.unit) * (self.feeRate + self.marginRate)
            positionVolume = match.volume
            positionPrice = match.price
            isLong = match.isLong
            self.assetTable[playerId] = Asset(total, margin, positionVolume, positionPrice, isLong)
        elif self.assetTable[playerId].isLong is match.isLong:
            total = self.assetTable[playerId].total - (match.price * match.volume * self.unit) * self.feeRate
            margin = self.assetTable[playerId].margin - (match.price * match.volume * self.unit) * (self.feeRate + self.marginRate)
            positionPrice = (self.assetTable[playerId].positionPrice * self.assetTable[playerId].positionVolume + match.price * match.volume) / (self.assetTable[playerId].positionVolume + match.volume)
            positionVolume = self.assetTable[playerId].positionVolume + match.volume
            isLong = self.assetTable[playerId].isLong
            self.assetTable[playerId] = Asset(total, margin, positionVolume, positionPrice, isLong)
        elif self.assetTable[playerId].isLong is 0:
            total = self.assetTable[playerId].total - (match.price * match.volume * self.unit) * self.feeRate
            margin = self.assetTable[playerId].margin - (match.price * match.volume * self.unit) * self.feeRate
            total += (self.assetTable[playerId].positionPrice - match.price) * match.volume * self.unit
            margin += (self.assetTable[playerId].positionPrice - match.price) * match.volume * self.unit
            positionVolume = self.assetTable[playerId].positionVolume - match.volume
            positionPrice = self.assetTable[playerId].positionPrice
            isLong = self.assetTable[playerId].isLong
            self.assetTable[playerId] = Asset(total, margin, positionVolume, positionPrice, isLong)
        else:
            total = self.assetTable[playerId].total - (match.price * match.volume * self.unit) * self.feeRate
            margin = self.assetTable[playerId].margin - (match.price * match.volume * self.unit) * self.feeRate
            total -= (self.assetTable[playerId].positionPrice - match.price) * match.volume * self.unit
            margin -= (self.assetTable[playerId].positionPrice - match.price) * match.volume * self.unit
            positionVolume = self.assetTable[playerId].positionVolume - match.volume
            positionPrice = self.assetTable[playerId].positionPrice
            isLong = self.assetTable[playerId].isLong
            self.assetTable[playerId] = Asset(total, margin, positionVolume, positionPrice, isLong)



            

    
    

