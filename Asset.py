
# coding: utf-8

# In[1]:


class Asset(object):
    def __init__(self, total, margin, positionVolume, positionPrice, isLong):
        self.total = total
        self.margin = margin
        self.positionVolume = positionVolume
        self.positionPrice = positionPrice
        self.isLong = isLong

