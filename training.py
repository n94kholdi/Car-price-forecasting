import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='cars')

cursor = cnx.cursor()

################################
### Read data from database: ###

read_cmd = 'SELECT * FROM new_truecar_info;'
cursor.execute(read_cmd)

x_data = []
y_data = []

for (name, Exterior_Color, Style, Interior_Color, MPG, Engine, Transmission, Drive_Type, Fuel_Type, Mileage, Options_Level, Accident_Check_, Usage_, Title_, Number_of_Owners_, price) in cursor:
    x_data.append((name, Exterior_Color, Style, Interior_Color, MPG, Engine, Transmission, Drive_Type, Fuel_Type, int(Mileage), Options_Level, int(Accident_Check_), Usage_, Title_, int(Number_of_Owners_)))
    y_data.append(int(price))

tags = [('name', 'S40'), ('Exterior_Color', 'S40'), ('Style', 'S40'), ('Interior_Color', 'S40'), ('MPG', 'S40'), ('Engine', 'S40'), ('Transmission', 'S40'), ('Drive_Type', 'S40'), ('Fuel_Type', 'S40'), ('Mileage', int), ('Options_Level', 'S40'), ('Accident_Check_', int), ('Usage_', 'S40'), ('Title_', 'S40'), ('Number_of_Owners_', int)]

x_data = np.array(x_data, dtype=tags)
y_data = np.array(y_data)


##################################################
### Preprocess data and encode string features: ###

x_data_prepro = []

for feature in tags:
    if feature[1] == 'S40':
        le = preprocessing.LabelEncoder()
        le.fit(list(x_data[feature[0]]))

        #print('%s : %a' % (feature[0], le.transform(list(x_data[feature[0]]))))
        x_data_prepro.append(le.transform(list(x_data[feature[0]])))
    else:
        #print('%s : %a' % (feature[0], x_data[feature[0]]))
        x_data_prepro.append(x_data[feature[0]])

x_data_prepro = np.array(x_data_prepro)
x_data_prepro = x_data_prepro.T

#####################################
######### shuffle Dataset ###########

indices = np.arange(len(y_data))
np.random.shuffle(indices)

x_data_prepro = x_data_prepro[indices]
y_data = y_data[indices]

##############################################
######### Split train and test set ###########

x_train = x_data_prepro[0:4000]
y_train = y_data[0:4000]

x_test = x_data_prepro[4000:]
y_test = y_data[4000:]

#######################################################
################## Compute loss : #####################

def compute_loss(model_name):
    pred_train = []
    for i in range(0, len(x_train)):
        pred_train.append(reg.predict([x_train[i]])[0])

    pred_test = []
    for i in range(0, len(x_test)):
        pred_test.append(reg.predict([x_test[i]])[0])

    import math
    print('MAE loss of train set for (%s Regression) : %f' % (model_name, math.sqrt(mean_squared_error(y_train, pred_train))))
    print('MAE loss of test set for (%s Regression) : %f\n' % (model_name, math.sqrt(mean_squared_error(y_test, pred_test))))


#############################################################
####### Train model for different reggression models ########

print()

reg = linear_model.BayesianRidge()
reg.fit(x_train, y_train)
compute_loss('Bayesian')

reg = linear_model.LassoLars(alpha=.1)
reg.fit(x_train, y_train)
compute_loss('lasso')

reg = linear_model.Ridge(alpha=.5)
reg.fit(x_train, y_train)
compute_loss('Ridge')

reg = linear_model.RidgeCV(alphas=np.logspace(-6, 6, 13))
reg.fit(x_train, y_train)
compute_loss('RidgeCV')

#######################################
############# samples #################

print('sample 5 :' )
print(reg.predict([x_test[5]])[0])
print(y_test[5])

print('\nsample 10 :' )
print(reg.predict([x_test[10]])[0])
print(y_test[10])

cnx.close()
