from .statFMB import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from datetime import date

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,index = True, nullable=False)
    vehicles = db.Column(db.Integer)
    pawns = db.Column(db.Integer)
    bicicles = db.Column(db.Integer)
    gate_id = db.Column(db.Integer, db.ForeignKey('gates.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id'))

    entrance = db.relationship("Entrance", backref="report", lazy="dynamic")

    def __repr__(self):
        return '<Report {} - {} - {}'.format(self.id,self.date ,self.gate)

    #TODO: this logic is not working!!!!!!!!!!!!!!!!!!!!!!
    #      cls.date == input_date not working
    #      Report.date is no acepting the date in the constructor
    @classmethod
    def is_eligible(cls,input_date,input_shift):

        print(type(input_date))
        print(type(cls.date))
        query = cls.query.filter(cls.date == input_date).all()

        print("query len: {}".format(len(query)))

        #query always gets at least 1, wich is the on we are importing
        print(input_shift.shift)
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


class Entrance(db.Model):
    __tablename__ = 'entrances'
    id = db.Column(db.Integer, primary_key=True)
    passengers = db.Column(db.Integer)

    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'))
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

    """
    def __init__(self,n_persons,report,vehicle_type,country,municipality):
        self.n_persons = n_persons
        self.report = report
        self.vehicle_type = vehicle_type
        self.country = country
        self.municipality = municipality
    """

    def __repr__(self):
        return '<Entrance {}'.format(self.id)


class Vehicle_type(db.Model):
    __tablename__ = 'vehicle_types'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(20), nullable=False)
    entrance = db.relationship("Entrance", backref="vehicle_type",
                               lazy="dynamic")

    def __init__(self,vehicle_type):
        self.vehicle_type = vehicle_type

    @classmethod
    def get_vehicle_type(cls,v):
        return cls.query.filter(cls.vehicle_type == v).one()


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


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance", backref="country", lazy="dynamic")
    alias = db.relationship("Country_alias", backref="country", lazy="dynamic")

    def __init__(self,country):
        self.country = country

    #TODO:when c == "" validate ocordingly
    @classmethod
    def get_country(cls,c):
        if c == "":
            return cls.query.filter(cls.country == "Portugal").one()
        else:
            return cls.query.filter(cls.country == c).one()


class Country_alias(db.Model):
    __tablename__ = 'country_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))


class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    municipality = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance", backref="municipality", lazy="dynamic")
    alias = db.relationship("Municipality_alias", backref="municipality",
                            lazy="dynamic")

    def __init__(self,municipality):
        self.municipality = municipality

    #TODO:when m == "" validate ocordingly
    @classmethod
    def get_municipality(cls,m):
        if m == "":
            return cls.query.filter(cls.municipality == "Lisboa").one()
        else:
            return cls.query.filter(cls.municipality == m).one()


class Municipality_alias(db.Model):
    __tablename__ = 'municipality_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey('municipalities.id'))

    def __init__(self,alias,municipality):
        self.alias = alias
        self.municipality = municipality


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

