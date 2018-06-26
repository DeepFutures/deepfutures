
# coding: utf-8

# In[1]:


class Match(object):
    def __init__(self, price, volume, isLong, step):
        self.price = price
        self.volume = volume
        self.isLong = isLong
        self.step = step

