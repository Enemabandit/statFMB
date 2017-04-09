from .statFMB import app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from collections import Counter, OrderedDict


db = SQLAlchemy(app)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    vehicles = db.Column(db.Integer)
    pawns = db.Column(db.Integer)
    bicicles = db.Column(db.Integer)
    gate_id = db.Column(db.Integer, db.ForeignKey('gates.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'))

    entrance = db.relationship("Entrance", backref="report", lazy="dynamic")

class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.Integer, primary_key = True)
    duration = db.Column(db.String(20), nullable=False)

    report = db.relationship("Report", backref="shift", lazy="dynamic")

#TODO: set @classmethods
class Entrance(db.Model):
    __tablename__ = 'entrances'
    id = db.Column(db.Integer, primary_key=True)
    n_persons = db.Column(db.Integer)

    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

    ### Constructor for Entrances objects
    def __init__(self,id,date,n_persons,entrance_type_id,gate_id,
                 country_id,municipality_id):
        self.id = id
        self.date = date
        self.n_persons = n_persons
        self.entrance_type_id = entrance_type_id
        self.gate_id = gate_id
        self.country = country
        self.municipality_id = municipality_id

    #initializes the seached_list with all entrances filtered by the user input
    def create_searched_list(lower_date, upper_date, gate):
        if  int(gate) == 4:
            Entrances.searched_list = (Entrances.query
                                       .join(Gates)
                                       .join(Countries)
                                       .join(Municipalities)
                                       .join(Entrance_types)
                                       .filter(Entrances.date >= lower_date)
                                       .filter(Entrances.date <= upper_date)
                                       .all())
        else:
            Entrances.searched_list = (Entrances.query
                                       .join(Gates)
                                       .join(Countries)
                                       .join(Municipalities)
                                       .join(Entrance_types)
                                       .filter(Entrances.date >= lower_date)
                                       .filter(Entrances.date <= upper_date)
                                       .filter(Entrances.gate_id == int(gate))
                                       .all())

    ###GET FUNCTIONS
    #returns a dictionary ordered by top gate with the related gate entrances
    #NOTE:get_top_x() returns the number of persons for each x
    #TODO:think about a solution to show get_top_x() for persons and vehicles
    #TODO:limit size of get_top_x() returns
    def get_top_gates():
        top_gates = {"Ameias": 0, "Serpa": 0, "Rainha": 0}
        for entrance in Entrances.searched_list:
            top_gates[gate_to_string(entrance.gate_id)] += entrance.n_persons
        return sort_dict(top_gates)

    def get_top_countries():
        top_countries = Counter()
        for entrance in Entrances.searched_list:
            current_country = entrance.country.country
            top_countries[current_country] += entrance.n_persons
        return top_countries.most_common(5)

    def get_top_municipalities():
        top_municipalities = Counter()
        for entrance in Entrances.searched_list:
            if entrance.country_id == 1:
                current_m = entrance.municipality.municipality
                top_municipalities[current_m] += entrance.n_persons
        return top_municipalities.most_common(5)

    ##returns a OrderedDict as explained below
    #
    #  period_list = ["yyyy-mm-dd": [entrance_type_id: n_vehicles,
    #                                entrance_type_id: n_vehicles,
    #                                ...]
    #                 "yyyy-mm-dd": [entrance_type_id: n_vehicles,
    #                                ...]
    #                 ...]
    #
    #  ids[1..8] = entrance types; [9] = passengers ; [10] = vehicles
    #
    #TODO:default show results by day, implement period option
    #TODO:implement pagination
    def get_period_list():
        period_entry = Counter()
        period_list = Counter()

        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id not in (1,2):
                add_entrance = Counter()
                add_entrance[entrance.entrance_type_id] = 1
                #add the number os passengers
                add_entrance[9] = entrance.n_persons
                #udd the sum of vehicles
                add_entrance[10]= 1
            else:
                add_entrance = Counter()
                add_entrance[entrance.entrance_type_id] = entrance.n_persons

            #update period_list
            if period_list[entrance.date] != 0:
                period_list[entrance.date] += add_entrance
            else:
                period_list[entrance.date] = add_entrance

        #sort list
        sorted_list = OrderedDict(sorted(period_list.items(),
                                         key=lambda t: t[0],
                                         reverse = True))
        Entrances.period_list = sorted_list
        return sorted_list

    def get_period_list_totals():
        totals = Counter()
        for period in Entrances.period_list:
            if totals != 0:
                totals += Entrances.period_list[period]
            else:
                totals = Entrances.period_list[period]
        print (totals)
        return totals


    #TODO: bicicles counting as vehicles, solve this
    def get_sum_vehicles():
        sum_vehicles = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id != 1:
                sum_vehicles += 1
        return sum_vehicles

    #TODO: bicicles counting as vehicles,solve this
    def get_sum_passengers():
        sum_passengers = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id != 1:
                sum_passengers += entrance.n_persons
        return sum_passengers

    #TODO: think about where to put biciles
    def get_sum_pedestrians():
        sum_pedestrians = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id == 1:
                sum_pedestrians += entrance.n_persons
        return sum_pedestrians

    ###

class Vehicle_type(db.Model):
    __tablename__ = 'vehicle_types'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(20), nullable=False)
    entrance = db.relationship("Entrance", backref="vehicle_type",
                               lazy="dynamic")


class Gate(db.Model):
    __tablename__ = 'gates'
    id = db.Column(db.Integer, primary_key=True)
    gate = db.Column(db.String(20), nullable=False)
    report = db.relationship("Report", backref="gate", lazy="dynamic")


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    report = db.relationship("Report", backref="country", lazy="dynamic")
    alias = db.relationship("Country_alias", backref="country", lazy="dynamic")

class Country_alias(db.Model):
    __tablename__ = 'country_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    municipality = db.Column(db.String(50), nullable=False)
    report = db.relationship("Report", backref="municipality", lazy="dynamic")
    alias = db.relationship("Municipality_alias", backref="municipality",
                            lazy="dynamic")


class Municipality_alias(db.Model):
    __tablename__ = 'municipality_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

###END OF DB.MODELS

class Period:
    #date_range
    #gate
    #total_vehicles
    #total_persons = n_passengers + n_pawns
    #n_passangers
    #vehicle_list
    #n_bicicles
    #n_pawns

    pass


#returns a dictionary sorted by value, from an unsorted dictionary
#returns none if argument type != dictionary
def sort_dict(d):
    if type(d) == dict:
        sorted_d = {}
        for key, value in sorted(d.items(),
                                 key = lambda t: t[1],
                                 reverse = True):
            sorted_d[key] = value
        return sorted_d
    else:
        return

#db.create_all()
