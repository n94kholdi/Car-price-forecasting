import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
import numpy as np


cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='cars')

cursor = cnx.cursor()

##### DELETE DUPLICATE ROWS FROM TABLE :

create_cmd = 'CREATE TABLE new_truecar_info (name varchar(40), Exterior_Color varchar(40), Style varchar(40), Interior_Color varchar(40), MPG varchar(40), Engine varchar(40), Transmission varchar(40), Drive_Type varchar(40), Fuel_Type varchar(40), Mileage INT, Options_Level varchar(40), Accident_Check_ INT, Usage_ varchar(40), Title_ varchar(40), Number_of_Owners_ INT, price INT);'

insert_cmd = ' INSERT INTO new_truecar_info (SELECT DISTINCT name, Exterior_Color, Style, Interior_Color, MPG, Engine, Transmission, Drive_Type, Fuel_Type, Mileage, Options_Level, Accident_Check_, Usage_, Title_, Number_of_Owners_, price FROM truecar_info);'

cursor.execute(create_cmd)
cursor.execute(insert_cmd)

cnx.commit()
cnx.close()

