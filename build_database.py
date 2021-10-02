import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
import numpy as np


cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='cars')

cursor = cnx.cursor()
all_res = []
count = 0

for p in range(301,334):

    ##########################
    ### read each webpage: ###
    print('page : %d' % p)
    list_req = requests.get('https://www.truecar.com/used-cars-for-sale/listings/ford/?page=%i&sort[]=best_match' % p)
    list_soup = BeautifulSoup(list_req.text, 'html.parser')

    ser = list_soup.find_all('a', attrs = {'class' : 'card card-1 card-shadow card-shadow-hover vehicle-card _1qd1muk'})
    for s in ser:
        
        ###########################
        ### read each car_info: ###


        car_url = "https://www.truecar.com/" + re.search(r'href="(.*)" style="color', str(s))[1]

        car_req = requests.get(car_url)
        car_soup = BeautifulSoup(car_req.text, 'html.parser')

        features = ['name']

        name = car_soup.find('div', attrs = {'class' : "text-truncate heading-3 margin-right-2 margin-right-sm-3"})
        engine = car_soup.find_all('h4', attrs = {'class' : "heading-5"})
        info = car_soup.find_all('div', attrs = {'class' : "_1l9na3c align-self-center col"})
        price = car_soup.find('div', attrs = {'class' : "label-block-text"})
        
        ##############################
        ### read all feature tags: ###

        for e in engine:
            features = features + [e.text]
        features = features + ['price']
        
        if len(features) == 18:
            del features[11]
            del features[-2]
        else:
            print('new car : False\n')
            continue
        
        base_features = ['name', 'Exterior Color', 'Style', 'Interior Color', 'MPG', 'Engine', 'Transmission', 'Drive Type', 'Fuel Type', 'Mileage', 'Options Level', 'Accident Check ', 'Usage ', 'Title ', 'Number of Owners ', 'price']

        if features != base_features:
            print('new car : False\n')
            continue
        else:
            print('new car : True\n')
            features = base_features

        ###############################
        ####### Build database: #######


        cr_command = "CREATE TABLE truecar_info ("
        ins_command = "INSERT INTO truecar_info VALUES ("

        for f in features:

            cr_command += re.sub(r'\s', '_', f) + (' INT, ' if f == 'price' or f == 'Mileage' or f == 'Number of Owners ' or f == 'Accident Check ' else ' varchar(40), ')
            ins_command += ("\'%i\'," if f == 'price' or f == 'Mileage' or f == 'Number of Owners ' or f == 'Accident Check ' else "\'%s\',")
 
        ins_command = ins_command[:len(ins_command)-1] + ');'
        cr_command = cr_command[:len(cr_command)-2] + ');'

        if count == 0:
        #    cursor.execute('DROP TABLE truecar_info;')
            cursor.execute(cr_command)

        ###########################################
        ### Add all feature values to database: ###

        err = 0
        feature_vals = (name.text,)

        for (f, i) in zip(features[1:len(features)-5], info):
            val = re.sub(f, '', i.text)
            try:
                val = int(''.join(re.findall(r"\d*", val))) if f == 'Mileage' else val
            except ValueError:
                err = 1
                break
            feature_vals += (val,)
        if err == 1:
            continue

        err = 0
        remain_fea = car_soup.find_all('div', attrs = {'class' : "padding-1"})

        for (f, r) in zip(features[-5:-1], remain_fea):
            val = re.sub(f, '', r.text)
            try:
                val = int(''.join(re.findall(r"\d*", val))) if f == 'Number of Owners ' or f == 'Accident Check ' else val
            except ValueError:
                err = 1
                break
            feature_vals += (val,)
        if err == 1:
            continue

        feature_vals += (int(''.join(re.findall(r"\d*", price.text[1:]))),)
        
        try:
            cursor.execute(ins_command % feature_vals)
        except:
            print('type error!!')
            continue
        cnx.commit()
        count += 1

        #if count > 5:
        #    cnx.close()
        #    exit(0)

        #for (e, i) in zip(engine, info):
        #    print("%s  :  %s" % (e.text, re.sub(e.text, '', i.text)))
        
cnx.close()
print('Count of cars: %i' % count)


##### DELETE DUPLICATE ROWS FROM TABLE :

## CREATE TABLE new_truecar_info (name varchar(40), Exterior_Color varchar(40), Style varchar(40), Interior_Color varchar(40), MPG varchar(40), Engine varchar(40), Transmission varchar(40), Drive_Type varchar(40), Fuel_Type varchar(40), Mileage INT, Options_Level varchar(40), Accident_Check_ INT, Usage_ varchar(40), Title_ varchar(40), Number_of_Owners_ INT, price INT);

## INSERT INTO new_truecar_info (SELECT DISTINCT name, Exterior_Color, Style, Interior_Color, MPG, Engine, Transmission, Drive_Type, Fuel_Type, Mileage, Options_Level, Accident_Check_, Usage_, Title_, Number_of_Owners_, price FROM truecar_info);
