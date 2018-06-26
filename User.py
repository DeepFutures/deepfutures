
# coding: utf-8

# In[6]:


import quandl
from Result import *
from Transaction import *
from Player import *
from random import *
from copy import *
import math
import pandas as pd
import tensorflow as tf


# In[7]:


class User(object):
    def __init__(self):
        self.situation = None
        self.priceVector = None
        self.result = None
        self.cur_x = None
        self.train_data = None
        self.train_x = None
        self.cur_y = None
        self.train_y = None
        self.nnClassifier = None
        self.date = None
    
    def getSituation(self, date):
        self.date = date
        situation = quandl.get("LBMA/GOLD.1", authtoken="LgQLvtBPEoVmev6J58_f", end_date = date, rows = 30, returns = "numpy")
        self.situation = situation
        self.extractPriceVector()
        self.initializeNN()
        return
    
    def extractPriceVector(self):
        if self.situation is None:
            return -1
        else:
            priceVector = []
            for i in range(0,len(self.situation)):
                priceVector.append(self.situation[i][1])
            self.priceVector = priceVector
            return
        
    def upgradePriceVector(self, newPrice):
        for i in range(0, 29):
            self.priceVector[i] = self.priceVector[i + 1]
        self.priceVector[29] = newPrice
    
    def simulate(self):
        if self.priceVector is None:
            return -1
        else:
            self.result = Result()
            transaction = Transaction(self.priceVector[len(self.priceVector) - 1])
            player1 = Player(1)
            player2 = Player(2)
            for i in range(0, 30):
                player1.mctsPrediction(self.priceVector, 1)
                player2.nnPrediction(self)
                player1.submitAction(transaction)
                player2.submitAction(transaction)
                transaction.match()
 
                player1.upgradeAsset(transaction)
                player2.upgradeAsset(transaction)
                self.upgradePriceVector(transaction.price)
                
                self.result.priceVector.append(transaction.price)
                self.result.actionsVector.append(player1.action)
                self.result.actionIdVector.append(player1.actionId)
                asset = player1.asset
                self.result.assetVector.append(asset)
                
                self.upgradeTrainFeatures(asset, transaction.curStep)
                self.upgradeTrainLabels(player1.actionId, transaction.curStep)

                if 1 in transaction.matchTable:
                    self.result.transactionsVector.append(transaction.matchTable[1])
                del transaction.submissions[:]
                transaction.matchTable.clear()
                transaction.assetTable.clear()
                transaction.curStep += 1
                if player1.asset.margin < -20000.0 or player2.asset.margin < -20000.0:
                    break
            self.convertTrainDataFrame()
        return
    
    def displayActions(self):
        for i in range(0, len(self.result.actionsVector)):
            if self.result.actionsVector[i].isPass is 1:
                print "Pass"
            elif self.result.actionsVector[i].isLong is 0:
                print "Sell out 1 hand",
                if self.result.actionsVector[i].bias is 0:
                    print "at previous price -2%"
                elif self.result.actionsVector[i].bias is 1:
                    print "at previous price -1%"
                elif self.result.actionsVector[i].bias is 2:
                    print "at previous price -0.5%"
                elif self.result.actionsVector[i].bias is 3:
                    print "at previous price +0.5%"
                elif self.result.actionsVector[i].bias is 4:
                    print "at previous price +1%"
                elif self.result.actionsVector[i].bias is 5:
                    print "at previous price +2%"
            else:
                print "Buy in 1 hand",
                if self.result.actionsVector[i].bias is 0:
                    print "at previous price -2%"
                elif self.result.actionsVector[i].bias is 1:
                    print "at previous price -1%"
                elif self.result.actionsVector[i].bias is 2:
                    print "at previous price -0.5%"
                elif self.result.actionsVector[i].bias is 3:
                    print "at previous price +0.5%"
                elif self.result.actionsVector[i].bias is 4:
                    print "at previous price +1%"
                elif self.result.actionsVector[i].bias is 5:
                    print "at previous price +2%"
    
    def displayMatchings(self):
        print "Days with a match:"
        for i in range(0, len(self.result.transactionsVector)):
            print "Day",
            print self.result.transactionsVector[i].step
        
    def displayPrices(self):
        for i in range(0, len(self.result.priceVector)):
            print self.result.priceVector[i]
            
    def displayTotalAsset(self):
        for i in range(0, len(self.result.assetVector)):
            print self.result.assetVector[i].total
            
    def upgradeTrainFeatures(self, asset, step):
        self.cur_x['total'].at[0] = asset.total
        self.cur_x['margin'].at[0] = asset.margin
        self.cur_x['positionVolume'].at[0] = asset.positionVolume
        self.cur_x['positionPrice'].at[0] = asset.positionPrice
        self.cur_x['isLong'].at[0] = asset.isLong
        self.cur_x['reward'].at[0] = 0.03 * (step + 1)
        for i in range(0, len(self.priceVector)):
            self.cur_x['{:d}'.format(i)].at[0] = self.priceVector[i]
 
        for key in self.cur_x.keys():
            self.train_data[key].append(self.cur_x[key].at[0])
            
            
    def upgradeTrainLabels(self, actionId, step):
        self.cur_y[0] = actionId
        self.train_data['actionId'].append(actionId)
        
    def convertTrainDataFrame(self):
        length = len(self.train_data['reward'])
        for i in range(0, length):
            self.train_data['reward'][length - 1 - i] = 1.0 - i * (1.0 / length)
        df = pd.DataFrame(data=self.train_data)
        self.train_y = df.pop('actionId')
        self.train_x = df
    
    def initializeNN(self):
        cur_data = {}
        cur_data['total'] = []
        cur_data['margin'] = []
        cur_data['positionVolume'] = []
        cur_data['positionPrice'] = []
        cur_data['isLong'] = []
        for i in range(0,30):
            cur_data['{:d}'.format(i)] = []
        cur_data['reward'] = []
        cur_data['actionId'] = []

        
        cur_data['total'].append(100000.0)
        cur_data['margin'].append(100000.0)
        cur_data['positionVolume'].append(0)
        cur_data['positionPrice'].append(0.0)
        cur_data['isLong'].append(0)
        cur_data['reward'].append(0.03)
        for i in range(0,30):
            cur_data['{:d}'.format(i)].append(self.priceVector[i])
        cur_data['actionId'].append(0)

        cur_data = pd.DataFrame(data=cur_data)
        self.cur_y = cur_data.pop('actionId')
        self.cur_x = cur_data
        
        self.train_data = {}
        self.train_data['total'] = []
        self.train_data['margin'] = []
        self.train_data['positionVolume'] = []
        self.train_data['positionPrice'] = []
        self.train_data['isLong'] = []
        self.train_data['reward'] = []
        for i in range(0,30):
            self.train_data['{:d}'.format(i)] = []
        self.train_data['actionId'] = []
            
        my_feature_columns = []
        for key in self.cur_x.keys():
            my_feature_columns.append(tf.feature_column.numeric_column(key=key))
        self.nnClassifier = tf.estimator.DNNClassifier(
        feature_columns=my_feature_columns,
        hidden_units=[1664, 832,416, 208, 104, 52, 26],
        n_classes=13,
        optimizer=tf.train.GradientDescentOptimizer(
        learning_rate=0.00000005),
        model_dir = 'nnModels',
        loss_reduction=tf.losses.Reduction.SUM)
        
    def trainNN(self):
        accuracy = 0
        while accuracy < 0.5:
            train = self.nnClassifier.train(
                input_fn=lambda:train_input_fn(self.train_x, self.train_y, 1),
                steps=1000)
            eval_result = self.nnClassifier.evaluate(
                input_fn=lambda:eval_input_fn(self.train_x, self.train_y, 30))
            accuracy = eval_result['accuracy']
    
         

