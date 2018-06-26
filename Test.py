
# coding: utf-8

# In[1]:


from User import *
from NeuralNetworks import *


# In[2]:


user1 = User()


# In[3]:


user1.getSituation('2017-09-02')


# In[4]:


print user1.priceVector


# In[5]:


print user1.situation


# In[6]:


user1.simulate()


# In[7]:


user1.displayActions()


# In[8]:


user1.displayTotalAsset()


# In[9]:


user1.displayPrices()


# In[10]:


user1.displayMatchings()


# In[11]:


(train_feature, train_label), (test_feature, test_label) = load_data()


# In[12]:


train_x = {}


# In[13]:


train_y = {}


# In[14]:


test_x = {}


# In[15]:


test_y = {}


# In[16]:


train_data = {}


# In[17]:


train_data['total'] = []
train_data['margin'] = []
train_data['positionVolume'] = []
train_data['positionPrice'] = []
train_data['isLong'] = []
train_data['actionId'] = []

for i in range(0, len(user1.result.priceVector)):
    train_data['total'].append(user1.result.assetVector[i].total)
    train_data['margin'].append(user1.result.assetVector[i].margin)
    train_data['positionVolume'].append(user1.result.assetVector[i].positionVolume)
    train_data['positionPrice'].append(user1.result.assetVector[i].positionPrice)
    train_data['isLong'].append(user1.result.assetVector[i].isLong)
    train_data['{:d}'.format(i)] = user1.priceVectorTable[i]
    train_data['actionId'].append(user1.result.actionIdVector[i])



# In[18]:


print len(train_data.keys())


# In[19]:


df_data = pd.DataFrame(data=train_data)


# In[20]:


print len(df_data.keys())


# In[21]:


print df_data.keys()


# In[22]:


df_y = df_data.pop('actionId')


# In[23]:


print len(df_data.keys())


# In[24]:


print df_y


# In[25]:


df_x = df_data


# In[26]:


print df_x.keys()


# In[27]:


print train_label.keys()


# In[28]:


print df_y.keys()


# In[29]:


print train_feature.keys()


# In[30]:


my_feature_columns = []
for key in df_x.keys():
    my_feature_columns.append(tf.feature_column.numeric_column(key=key))


# In[31]:


print len(my_feature_columns)


# In[177]:


classifier = tf.estimator.DNNClassifier(
       feature_columns=my_feature_columns,
       hidden_units=[10, 10, 10],
       n_classes=13,
       model_dir = 'nnModels67',
       optimizer='Adagrad',
       activation_fn=tf.nn.relu,
       dropout=None,
       loss_reduction=tf.losses.Reduction.SUM)


# In[178]:


classifier.train(
        input_fn=lambda:train_input_fn(df_x, df_y, 30),
        steps=1000)


# In[176]:


eval_result = classifier.evaluate(
    input_fn=lambda:eval_input_fn(df_x, df_y, 30))

print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))


# In[181]:


predictions = classifier.predict(
    input_fn=lambda:eval_input_fn(df_x, None,batch_size=50))


# In[182]:


for pred_dict, expec in zip(predictions, df_y):
    template = ('\nPrediction is "{}" ({:.1f}%), expected "{}"')

    class_id = pred_dict['class_ids'][0]
    probability = pred_dict['probabilities'][class_id]
    print(template.format(class_id, 100 * probability, expec))
    if class_id != expec:
        print "wrong prediction"

