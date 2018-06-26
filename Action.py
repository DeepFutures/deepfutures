
# coding: utf-8

# In[3]:


class Action(object):
    def __init__(self, isPass, isLong, bias):
        self.isPass = isPass
        self.isLong = isLong
        self.bias = bias

