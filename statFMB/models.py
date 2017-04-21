from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .statFMB import db
from .modules.utils import is_typo

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,index = True, nullable=False)
    vehicles = db.Column(db.Integer)
    pawns = db.Column(db.Integer)
    bicicles = db.Column(db.Integer)
    gate_id = db.Column(db.Integer, db.ForeignKey('gates.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'))

    entrance = db.relationship("Entrance",
                               backref=db.backref("report"),
                               lazy="dynamic")

    def __repr__(self):
        return '<Report {} - {} - {}'.format(self.id,self.date ,self.gate)

    #TODO: this overrides the last report, if more than one (rework)
    @classmethod
    def get_report(cls,date,gate):
        report = cls.query.filter(cls.date == date,
                                 cls.gate == gate,
                                 ).first()
        return report

    @classmethod
    def get_report_by_id(cls,report_id):
        return cls.query.filter(cls.id == report_id).one()

    @classmethod
    def is_eligible(cls,input_date,input_shift,input_gate):

        query = cls.query.filter(cls.date == input_date,
                                 cls.gate == input_gate).all()
        #query always gets at least 1, wich is the on we are uploading
        if len(query) > 1:
            if len(query) < 3 and input_shift.shift == "Meio":
                    return True
            else:
                return False
        else:
            return True


    #creates the search_list with all the entrances from de date range
    @classmethod
    def create_search_list(cls,lower_date, upper_date, selected_gate):
        cls.s_query = (cls.query
                       .join(Entrance)
                       .join(Gate)
                       .join(Vehicle_type)
                       .join(Country)
                       .join(Municipality)
                       .add_columns(cls.date,
                                    cls.vehicles,
                                    cls.pawns,
                                    cls.vehicles,
                                    Gate.gate,
                                    Entrance.passengers,
                                    Vehicle_type.vehicle_type,
                                    Country.country,
                                    Municipality.municipality)
                       .filter(cls.date >= lower_date)
                       .filter(cls.date <= upper_date)
        )
        if selected_gate != "Todas":
            cls.s_query = cls.s_query.filter(Gate.gate == selected_gate)

        cls.search_list = cls.s_query.all()

        return


class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.Integer, primary_key = True)
    shift = db.Column(db.String(20), nullable=False)

    report = db.relationship("Report", backref="shift", lazy="dynamic")

    def __init__(self, shift):
        self.shift = shift

    @classmethod
    def get_shift(cls,s):
        return cls.query.filter(cls.shift == s).one()


class Gate(db.Model):
    __tablename__ = 'gates'
    id = db.Column(db.Integer, primary_key=True)
    gate = db.Column(db.String(20), nullable=False)
    report = db.relationship("Report", backref="gate", lazy="dynamic")

    def __init__(self, gate):
        self.gate = gate

    @classmethod
    def get_gate(cls,g):
        return cls.query.filter(cls.gate == g).one()


##Entrance related models
class Entrance(db.Model):
    __tablename__ = 'entrances'
    id = db.Column(db.Integer, primary_key=True)
    passengers = db.Column(db.Integer)

    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

    def __repr__(self):
        return '<Entrance {}'.format(self.id)

    @classmethod
    def get_entrances_of_report(cls,report):
        return cls.query.filter(cls.report == report).all()


class Vehicle_type(db.Model):
    __tablename__ = 'vehicle_types'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(20), nullable=False)

    entrance = db.relationship("Entrance", backref="vehicle_type",
                               lazy="dynamic")
    alias = db.relationship("Vehicle_type_alias", backref="vehicle_type",
                               lazy="dynamic")

    def __init__(self,vehicle_type):
        self.vehicle_type = vehicle_type

    @classmethod
    def get_vehicle_type(cls,v):
        clean_str = cls.clean_str(v)
        if clean_str != "invalid":
            return cls.query.filter(cls.vehicle_type == clean_str).one()
        else:
            return None

    #returns the contents of table vehicle_types
    @classmethod
    def get_vehicle_types(cls):
        return cls.query.all()

    #returns a list of all Vehicle_type.vehicle_type strings
    @classmethod
    def get_vehicle_types_list(cls):
        query = cls.get_vehicle_types()
        vehicle_type_list = []
        for vt in query:
            vehicle_type_list.append(vt.vehicle_type)
        return vehicle_type_list


    #TODO: this is replicated in Country and Municipality (rework)
    #returns the string cleaned for vehicle_type or "invalid" when not found
    @classmethod
    def clean_str(cls,word):
        vehicle_type_obj_list = cls.query.all()

        vehicle_type_list = []
        for vt in vehicle_type_obj_list:
            vehicle_type_list.append(vt.vehicle_type)

        if word in vehicle_type_list:
            return word
        else:
            for vehicle_type in vehicle_type_list:
                if is_typo(word,vehicle_type):
                    return vehicle_type
                else:
                    if Vehicle_type_alias.is_alias(word,vehicle_type):
                        return vehicle_type
            else:
                return "invalid"


class Vehicle_type_alias(db.Model):
    __tablename__ = "vehicle_type_alias"
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(20), nullable = False)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey("vehicle_types.id"))

    def __init__(self, alias, vehicle_type):
        self.alias = alias
        self.vehicle_type = vehicle_type

    #TODO: this is replicated on all alias classes (rework)
    @classmethod
    def is_alias(cls, word, vehicle_type):
        alias_obj_list = cls.query.filter(
            cls.vehicle_type
            == Vehicle_type.get_vehicle_type(vehicle_type)).all()

        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)

        if alias_list:
            if word not in alias_list:
                for alias in alias_list:
                    if is_typo(word,alias):
                        return True
                else:
                    return False
            else:
                return True
        else:
            return False


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance", backref="country", lazy="dynamic")
    alias = db.relationship("Country_alias", backref="country", lazy="dynamic")

    def __init__(self,country):
        self.country = country

    @classmethod
    def get_country(cls,c):
        return cls.query.filter(cls.country == c).one()

    @classmethod
    def get_countries_list(cls):
        query = cls.query.all()
        country_list = []
        for country in query:
            country_list.append(country.country)
        return country_list

    #TODO: this is replicated on Municipality and Vehicle_type (rework)
    #returns the string cleaned for country or "invalid" when not found
    @classmethod
    def clean_str(cls,word):
        country_obj_list = cls.query.all()

        country_list = []
        for c in country_obj_list:
            country_list.append(c.country)

        if word in country_list:
            return word
        else:
            for country in country_list:
                if is_typo(word,country):
                    return country
                else:
                    if Country_alias.is_alias(word,country):
                        return country
            else:
                return "invalid"


#TODO: not considering E.U.América as alias for some reason
#      needs further testing
class Country_alias(db.Model):
    __tablename__ = 'country_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

    #TODO: this is replicated on all alias classes (rework)
    @classmethod
    def is_alias(cls, word, country):
        alias_obj_list = cls.query.filter(
            cls.country == Country.get_country(country)).all()

        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)

        if alias_list:
            if word not in alias_list:
                for alias in alias_list:
                    if is_typo(word,alias):
                        return True
                else:
                    return False
            else:
                return True
        else:
            return False


class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    municipality = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance", backref="municipality", lazy="dynamic")
    alias = db.relationship("Municipality_alias", backref="municipality",
                            lazy="dynamic")

    def __init__(self,municipality):
        self.municipality = municipality

    @classmethod
    def get_municipality(cls,m):
        return cls.query.filter(cls.municipality == m).one()

    @classmethod
    def get_municipalities_list(cls):
        query = cls.query.all()
        municipalities_list = []
        for municipality in query:
            municipalities_list.append(municipality.municipality)
        return municipalities_list

    #TODO: this is replicated on Country and Vehicle_type (rework)
    #returns the string cleaned for municipality or "invalid" when not found
    @classmethod
    def clean_str(cls,word):
        municipality_obj_list = cls.query.all()

        municipality_list = []
        for m in municipality_obj_list:
            municipality_list.append(m.municipality)

        if word in municipality_list:
            return word
        else:
            for municipality in municipality_list:
                if is_typo(word,municipality):
                    return municipality
                else:
                    if Municipality_alias.is_alias(word,municipality):
                        return municipality
            else:
                return "invalid"


class Municipality_alias(db.Model):
    __tablename__ = 'municipality_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(100), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

    def __init__(self,alias,municipality):
        self.alias = alias
        self.municipality = municipality


    #TODO: this is replicated on all alias classes (rework)
    @classmethod
    def is_alias(cls, word, municipality):
        alias_obj_list = cls.query.filter(
            cls.municipality
            == Municipality.get_municipality(municipality)).all()

        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)

        if alias_list:
            if word not in alias_list:
                for alias in alias_list:
                    if is_typo(word,alias):
                        return True
                else:
                    return False
            else:
                return True
        else:
            return False


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

