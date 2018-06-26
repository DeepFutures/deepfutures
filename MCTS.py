
# coding: utf-8

# In[1]:


# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 2.7.
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in 
# the UCTPlayGame() function at the bottom of the code.
# 
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
from User import *
from Player import *
from Transaction import *
import random

class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic 
        zero-sum game, although they can be enhanced and made quicker, for example by using a 
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """
    def __init__(self, user):
            self.playerJustMoved = 2 # At the root pretend the player just moved is player 2 - player 1 has the first move
            self.rootState = user
            self.user = user
            self.userTemp = User()
            priceVector = user.priceVector
            self.userTemp.priceVector = priceVector
            cur_x = user.cur_x
            self.userTemp.cur_x = cur_x
            
            self.player1 = Player(1)
            tempPlayer1 = Player(1)
            self.tempPlayer1 = tempPlayer1
            
            self.player2 = Player(2)
            tempPlayer2 = Player(2)
            self.tempPlayer2 = tempPlayer2
            
            self.transaction = Transaction(self.user.priceVector[len(self.user.priceVector) - 1])
            tempTransaction = Transaction(self.user.priceVector[len(self.user.priceVector) - 1])
            self.tempTransaction = tempTransaction
    
    def upgradeTrainFeatures(self, asset, step):
        self.user.cur_x['total'].at[0] = asset.total
        self.user.cur_x['margin'].at[0] = asset.margin
        self.user.cur_x['positionVolume'].at[0] = asset.positionVolume
        self.user.cur_x['positionPrice'].at[0] = asset.positionPrice
        self.user.cur_x['isLong'].at[0] = asset.isLong
        self.user.cur_x['reward'].at[0] = 0.03 * (step + 1)
        for i in range(0, len(self.user.priceVector)):
            self.user.cur_x['{:d}'.format(i)].at[0] = self.user.priceVector[i]
    
    def Clone(self):
        """ Create a deep clone of this game state.
        """
        tempUser = User()
        tempUser.cur_x = self.rootState.cur_x
        tempUser.priceVector = self.rootState.priceVector
        newState = GameState(tempUser) 
        st = newState
        st.playerJustMoved = self.playerJustMoved
        return st

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        if self.playerJustMoved == 2:
            self.playerJustMoved = 3 - self.playerJustMoved
            self.player1.actionId = move
            self.player1.action = self.player1.translateAction(self.player1.actionId)
            self.player1.submitAction(self.transaction)
        else:
            self.playerJustMoved = 3 - self.playerJustMoved
            self.player2.actionId = move
            self.player2.action = self.player2.translateAction(self.player2.actionId)
            self.player2.submitAction(self.transaction)
            self.transaction.match()
            self.player1.upgradeAsset(self.transaction)
            self.player2.upgradeAsset(self.transaction)
            asset = self.player2.asset
            self.user.upgradePriceVector(self.transaction.price)
            self.upgradeTrainFeatures(asset, self.transaction.curStep)
            del self.transaction.submissions[:]
            self.transaction.matchTable.clear()
            self.transaction.assetTable.clear()
            self.transaction.curStep += 1
     
    def DoMoveTemp(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        if self.playerJustMoved == 2:
            self.playerJustMoved = 3 - self.playerJustMoved
            self.tempPlayer1.actionId = move
            self.tempPlayer1.action = self.tempPlayer1.translateAction(self.tempPlayer1.actionId)
            self.tempPlayer1.submitAction(self.tempTransaction)
        else:
            self.playerJustMoved = 3 - self.playerJustMoved
            self.tempPlayer2.actionId = move
            self.tempPlayer2.action = self.tempPlayer2.translateAction(self.tempPlayer2.actionId)
            self.tempPlayer2.submitAction(self.tempTransaction)
            self.tempTransaction.match()
            self.tempPlayer1.upgradeAsset(self.tempTransaction)
            self.tempPlayer2.upgradeAsset(self.tempTransaction)
            asset = self.tempPlayer2.asset
            self.userTemp.upgradePriceVector(self.tempTransaction.price)
            self.upgradeTrainFeatures(asset, self.tempTransaction.curStep)
            del self.tempTransaction.submissions[:]
            self.tempTransaction.matchTable.clear()
            self.tempTransaction.assetTable.clear()
            self.tempTransaction.curStep += 1


    

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        return range(0, 13)
    
    def GetResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """        
        
        if self.transaction.curStep == 30 or self.player1.asset.margin <= 0 or self.player2.asset.margin <= 0:
            if self.player1.asset.total > self.player2.asset.total:
                if playerjm == 1: 
                    if self.playerJustMoved == playerjm:
                        return 1.0
                    else:
                        return 0.0
            elif self.player1.asset.total < self.player2.asset.total:
                if playerjm == 1: 
                    if self.playerJustMoved == playerjm:
                        return 0.0
                    else:
                        return 1.0
            else:
                return 0.0
        else:
            return None
        
    def GetTempResult(self, playerjm):
        """ Get the game result from the viewpoint of playerjm. 
        """        
        
        if self.tempTransaction.curStep == 30 or self.tempPlayer1.asset.margin <= 0 or self.tempPlayer2.asset.margin <= 0:
            if self.tempPlayer1.asset.total > self.tempPlayer2.asset.total:
                if playerjm == 1: 
                    if self.playerJustMoved == playerjm:
                        return 1.0
                    else:
                        return 0.0
            elif self.tempPlayer1.asset.total < self.tempPlayer2.asset.total:
                if playerjm == 1: 
                    if self.playerJustMoved == playerjm:
                        return 0.0
                    else:
                        return 1.0
            else:
                return 0.0
        else:
            return None
        

    def __repr__(self):
        """ Don't need this - but good style.
        """
        s = "Situation:" + str(self.user.priceVector) + " JustPlayed:" + str(self.playerJustMoved)
        return s
        pass



class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()
        

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMoveTemp(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)            
            m = random.choice(node.untriedMoves) 
            state.DoMoveTemp(m)
            node = node.AddChild(m,state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != [] and state.GetTempResult(node.playerJustMoved) == None: # while state is non-terminal
            state.DoMoveTemp(random.choice(state.GetMoves()))
        
        result = state.GetTempResult(node.playerJustMoved)
        
        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(result) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    #if (verbose): print rootnode.TreeToString(0)
    #else: print rootnode.ChildrenToString()

    move = sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
    
    return move
    
                
def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number 
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO
    
    user1 = User()
    user1.getSituation('2017-09-02')    
    state = GameState(user1)
    move = UCT(rootstate = state, itermax = 13, verbose = False)

            
                          
            



