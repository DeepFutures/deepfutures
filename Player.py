
# coding: utf-8

# In[26]:


from Action import *
from Asset import *
from random import *
from NeuralNetworks import *

class Player(object):
    def __init__(self, playerId):
        self.id = playerId
        self.nn = None
        self.action = None
        self.actionId = None
        self.asset = Asset(100000.0, 100000.0, 0, 0.0, 0)
        
    def nnPrediction(self, user):

        predictions = user.nnClassifier.predict(
            input_fn=lambda:eval_input_fn(user.cur_x, None, batch_size=30),
            checkpoint_path = user.nnClassifier.latest_checkpoint())
        move = None
        for predict in predictions:
            move = predict['class_ids'][0]
        self.actionId = int(move)
        self.action = self.translateAction(self.actionId)
        
        return self.actionId
    
    def mctsPrediction(self, priceVector, nn):
        move = randint(0,12)
        self.actionId = move
        self.action = self.translateAction(move)
    
    def submitAction(self, transaction):
        transaction.submissions.append([self.id, self.action])
        transaction.assetTable[self.id] =  self.asset
        return
    
    def upgradeAsset(self, transaction):
        self.asset = transaction.assetTable[self.id]
        return
        
    def getNNPrediction(self, data):
        pass
    
    def translateAction(self, move):
        action = None
        if move is 0:
            action = Action(1, 0, 0)
        elif move is 1:
            action = Action(0, 0, 0)
        elif move is 2:
            action = Action(0, 0, 1)
        elif move is 3:
            action = Action(0, 0, 2)
        elif move is 4:
            action = Action(0, 0, 3)
        elif move is 5:
            action = Action(0, 0, 4)
        elif move is 6:
            action = Action(0, 0, 5) 
        elif move is 7:
            action = Action(0, 1, 0)
        elif move is 8:
            action = Action(0, 1, 1)
        elif move is 9:
            action = Action(0, 1, 2)
        elif move is 10:
            action = Action(0, 1, 3)
        elif move is 11:
            action = Action(0, 1, 4)
        elif move is 12:
            action = Action(0, 1, 5)          
        return action

