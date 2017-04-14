from .statFMB import db
from .models import (Country, Municipality, Municipality_alias,
                     Shift, Gate, Vehicle_type, Vehicle_type_alias)
import csv
from collections import defaultdict

#create the Database and db tables
def create_tables():
    db.create_all()
    insert_countries()
    insert_municipalities_and_alias()
    insert_shifts()
    insert_gates()
    insert_vehicle_types()
    #insert_vehicle_types_and_alias()

    db.session.commit()
    return

#insert

def insert_vehicle_types():
   db.session.add(Vehicle_type("Moto"))
   db.session.add(Vehicle_type("Ligeiro"))
   db.session.add(Vehicle_type("Ligeiro XL"))
   db.session.add(Vehicle_type("Caravana"))
   db.session.add(Vehicle_type("Autocarro"))

'''
def insert_vehicle_types_and_alias():
    read_list = []
    with open('static/resources/vt_alias.csv', 'rt',
              encoding = "ISO-8859-1") as vehicle_type_csv:
        reader = csv.reader(vehicle_type_csv, delimiter = ',')
        for row in reader:
            read_list.append(row)

    vehicle_type_dict = defaultdict(list)
    for entry in read_list:
        vehicle_type = entry[0]
        vehicle_type_alias = entry[1]
        vehicle_type_dict[vehicle_type].append(Vehicle_type_alias)

    vehicle_type_obj_list = []
    vehicle_type_alias_obj_list = []
    for vehicle_type, alias_list in vehicle_type_dict.items():
        vehicle_type_obj = Vehicle_type(vehicle_type)
        vehicle_type_obj_list.append(vehicle_type_obj)
        for alias in alias_list:
            alias_obj = Vehicle_type_alias(alias,vehicle_type_obj)
            vehicle_type_alias_obj_list.append(alias_obj)

    db.session.add_all(vehicle_type_obj_list)
    db.session.add_all(vehicle_type_alias_obj_list)

'''

def insert_countries():
    country_list = []
    with open('static/resources/country_list.csv','rt',
              encoding ="ISO-8859-1") as country_csv:
        reader = csv.reader(country_csv)
        for row in reader:
            country_list.append(row[0])

    country_list.sort()

    country_obj_list = []
    for country in country_list:
        country_obj = Country(country)
        country_obj_list.append(country_obj)

    db.session.add_all(country_obj_list)

    return


def insert_municipalities_and_alias():

    read_list = []
    #read table from file
    with open('static/resources/municipality_list.csv', 'rt',
              encoding = "ISO-8859-1") as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in reader:
            read_list.append(row)

    municipalities_dict = defaultdict(list)
    for entry in read_list:
        municipality = entry[3]
        parish = entry[5]
        municipalities_dict[municipality].append(parish)

    municipality_obj_list = []
    parish_obj_list = []
    for municipality, parish_list in municipalities_dict.items():
        municipality_obj = Municipality(municipality)
        municipality_obj_list.append(municipality_obj)
        for parish in parish_list:
            parish_obj = Municipality_alias(parish,municipality_obj)
            parish_obj_list.append(parish_obj)

    db.session.add_all(municipality_obj_list)
    db.session.add_all(parish_obj_list)

    return


def insert_shifts():
   db.session.add(Shift("Completo"))
   db.session.add(Shift("Meio"))


def insert_gates():
   db.session.add(Gate("Ameias"))
   db.session.add(Gate("Serpa"))
   db.session.add(Gate("Rainha"))


def insert_country_alias():
    pass

