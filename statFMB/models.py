from collections import OrderedDict, defaultdict, Counter
from json import JSONEncoder
from datetime import date, datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .statFMB import db, RoleMixin, UserMixin, SQLAlchemyUserDatastore

##Report related models
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,index = True, nullable=False)

    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())

    vehicles = db.Column(db.Integer)

    pawns = db.Column(db.Integer)
    bicicles = db.Column(db.Integer)

    gate_id = db.Column(db.Integer, db.ForeignKey('gates.id'))
    entrances = db.relationship("Entrance",
                               backref=db.backref("report"),
                               lazy="dynamic")

    def __repr__(self):
        return '<Report {} - {} - {}>'.format(self.id,
                                             self.date ,
                                              self.gate.gate)

    @classmethod
    def get_report(cls,date,start_time,end_time,gate):
        report = cls.query.filter(cls.date == date,
                                  cls.start_time == start_time,
                                  cls.end_time == end_time,
                                  cls.gate == gate,).one()
        return report

    @classmethod
    def get_report_by_id(cls,report_id):
        return cls.query.filter(cls.id == report_id).one()

    @classmethod
    def get_report_list(cls,lower_date, upper_date, gate):
        report_query = cls.query.filter(cls.date >= lower_date,
                                       cls.date <= upper_date)
        if gate != "Todas":
            gate_obj = Gate.get_gate(gate)
            report_query = report_query.filter(cls.gate == gate_obj)

        return report_query.all()

    @classmethod
    def get_db_action(cls,input_date,input_gate,input_start_time,
                       input_end_time):

        report_list = cls.query.filter(cls.date == input_date,
                                       cls.gate == input_gate).all()

        #query always gets at least 1, wich is the on we are uploading
        count = 0
        if len(report_list) > 1:
            for report in report_list:
                if (report.start_time == input_start_time
                    and report.end_time == input_end_time):
                    count = count +1
                    if count > 1:
                        return "replace"
                elif (report.start_time >= input_end_time
                      or report.end_time <= input_start_time):
                    return "valid"
                else:
                    return "invalid"
        else:
            return "valid"


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
    vehicle_type_id = db.Column(db.Integer,
                                db.ForeignKey('vehicle_types.id'))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    municipality_id = db.Column(db.Integer,
                                db.ForeignKey('municipalities.id'))

    def __repr__(self):
        return '<Entrance {}>'.format(self.id)

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
            return cls.query.filter(cls.vehicle_type == v).one()

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


class Vehicle_type_alias(db.Model):
    __tablename__ = "vehicle_type_alias"
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(20), nullable = False)
    vehicle_type_id = db.Column(db.Integer,
                                db.ForeignKey("vehicle_types.id"))

    def __init__(self, alias, vehicle_type):
        self.alias = alias
        self.vehicle_type = vehicle_type

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_alias_list(cls):
        alias_obj_list = cls.get_all()
        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)
        return alias_list

    @classmethod
    def get_dict(cls):
        alias_obj_list = cls.get_all()
        alias_dict = {}
        for alias in alias_obj_list:
            if alias.vehicle_type.vehicle_type in alias_dict:
                alias_dict[alias.vehicle_type.vehicle_type].append(alias.alias)
            else:
                alias_dict[alias.vehicle_type.vehicle_type] = [alias.alias]
        return alias_dict


class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance", backref="country",
                               lazy="dynamic")
    alias = db.relationship("Country_alias", backref="country",
                            lazy="dynamic")

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


class Country_alias(db.Model):
    __tablename__ = 'country_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(50), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_alias_list(cls):
        alias_obj_list = cls.get_all()
        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)
        return alias_list

    @classmethod
    def get_dict(cls):
        alias_obj_list = cls.get_all()
        alias_dict = {}
        for alias in alias_obj_list:
            if alias.country.country in alias_dict:
                alias_dict[alias.country.country].append(alias.alias)
            else:
                alias_dict[alias.country.country] = [alias.alias]
        return alias_dict


class Municipality(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    municipality = db.Column(db.String(50), nullable=False)
    entrance = db.relationship("Entrance",
                               backref="municipality", lazy="dynamic")
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


class Municipality_alias(db.Model):
    __tablename__ = 'municipality_alias'
    id = db.Column(db.Integer, primary_key=True)
    alias = db.Column(db.String(100), nullable=False)
    municipality_id = db.Column(db.Integer,
                                db.ForeignKey('municipalities.id'))

    def __init__(self,alias,municipality):
        self.alias = alias
        self.municipality = municipality

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_alias_list(cls):
        alias_obj_list = cls.get_all()
        alias_list = []
        for alias in alias_obj_list:
            alias_list.append(alias.alias)
        return alias_list

    @classmethod
    def get_dict(cls):
        alias_obj_list = cls.get_all()
        alias_dict = {}
        for alias in alias_obj_list:
            if alias.municipality.municipality in alias_dict:
                alias_dict[alias.municipality.municipality].append(alias.alias)
            else:
                alias_dict[alias.municipality.municipality] = [alias.alias]
        return alias_dict



#Logging models
class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer(), primary_key=True)
    time = db.Column(db.DateTime())
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, description, user, time = datetime.now()):
        self.time = time
        self.description = description
        self.user_id = user.id

    @classmethod
    def get_logs_raw(cls,user = None,
                     lower_time= datetime.min, upper_time = datetime.now()):
        if user == None:
            logs_query = cls.query.filter(cls.time >= lower_time,
                                          cls.time <= upper_time)
        else:
            logs_query = cls.query.filter(cls.user_id == user.id,
                                          cls.time >= lower_time,
                                          cls.time <= upper_time)
        return logs_query.all()

    @classmethod
    def get_logs(cls, user = None,
                 lower_time = datetime.min, upper_time = datetime.now()):
        logs_list_raw = cls.get_logs_raw(user = user,
                                         lower_time = lower_time,
                                         upper_time = upper_time)
        logs_list = []
        for log in logs_list_raw:
            logs_list.append(log.to_dict())

        if logs_list == []:
            return None
        else:
            logs_list = sorted(logs_list, key = lambda t: t['time'],
                               reverse = True)
            return logs_list


    def to_dict(self):
        return {"time": self.time,
                "description": self.description,
                "user": User.get_user_by_id(self.user_id).name}


    def __repr__(self):
        user = User.get_user_by_id(self.user_id)
        return '<Log: {}-{}-{}>'.format(self.time,user,self.description)


#Authentication models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    @classmethod
    def get_roles():
        return cls.query.all()


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    name = db.Column(db.String(100))
    phone = db.Column(db.Integer)
    alias = db.Column(db.String(3), unique=True)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    logs = db.relationship('Log',
                           backref=db.backref("logs"), lazy="dynamic")

    @classmethod
    def get_user_list(cls):
        return cls.query.all()

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.filter(cls.id == user_id).one()

    @classmethod
    def is_available(self,email = "",alias = ""):
        user_list = User.get_user_list()
        for user in user_list:
            if email == user.email or alias == user.alias:
                return False
        return True

    @classmethod
    def get_unavailable_description(self,email = "",alias = ""):
        user_list = User.get_user_list()
        description = ""
        for user in user_list:
            if user.email == email:
                description += "email->{}; ".format(email)
            if user.alias == alias:
                description += "Abreviatura->{} ".format(alias)
        return description

    #returns true if email is unchanged or available in db
    def is_email_eligible_for_editing(self, email):
        if ((self.email != email and User.is_available(email = email))
            or self.email == email):
            return True
        else:
            return False

    #returns true if alias is unchanged or available in db
    def is_alias_eligible_for_editing(self, alias):
        if ((self.alias != alias and User.is_available(alias = alias))
            or self.alias == alias):
            return True
        else:
            return False

    def is_eligible_for_editing(self,email = "",alias = ""):
        if ((self.is_email_eligible_for_editing(email) or email == "")
            and (self.is_alias_eligible_for_editing(alias) or alias == "")):
            return True
        else:
            return False

    def get_ineligible_description(self,email = "",alias = ""):
        description = ""
        if email != "" and not self.is_email_eligible_for_editing(email):
            description += ("email: {}, ".format(email))
        if alias != "" and not self.is_alias_eligible_for_editing(alias):
            description += ("abreviatura: {}, ".format(alias))
        description += "já existe na base de dados"
        return description


    def to_dict(self):
        return {'role': self.roles[0],
                'email': self.email,
                'state': self.active,
                'name': self.name,
                'phone': self.phone,
                'alias': self.alias,
        }

    def get_role(self):
        return self.roles[0]

    def __repr__(self):
        return '<User: {}>'.format(self.email)


###END OF DB.MODELS

class Search():

    def __init__(self,lower_date, upper_date, gate, period_str):
        self.report_list = Report.get_report_list(lower_date,
                                                  upper_date,
                                                  gate)
        self.period_list = []
        self.period_str = period_str

        if self.report_list:
            self.set_period_list()

    def set_period_list(self):
        #split reports per period and create its instances
        selection = {
            'Totais': self.set_totals,
            'Diario': self.set_daily,
            'Semanal': self.set_weekly,
            'Mensal': self.set_monthly,
            'Anual': self.set_annual,
        }
        selection[self.period_str] ()

    def set_totals(self):
        self.period_list.append(Period(self.report_list))
        print("Total period: {}".format(self.period_list))

    def set_daily(self):
        agregated_reports = defaultdict(list)
        for report in self.report_list:
            agregated_reports[report.date.isoformat()].append(report)

        ordered_reports = OrderedDict(sorted(agregated_reports.items(),
                                             key = lambda t: t[0],
                                             reverse = True))
        for entry in ordered_reports:
            new_period = Period(ordered_reports[entry],self.period_str)
            self.period_list.append(new_period)

        print("Number of periods found: {}".format(len(self.period_list)))

    def set_weekly(self):
        agregated_reports = defaultdict(list)
        for report in self.report_list:
            year = report.date.year
            week = report.date.isocalendar()[1]
            dict_key = "{} {}".format(year, week)
            agregated_reports[dict_key].append(report)

        ordered_reports = OrderedDict(sorted(agregated_reports.items(),
                                             key = lambda t: t[1][0].date,
                                             reverse = True))

        for entry in ordered_reports:
            new_period = Period(ordered_reports[entry],self.period_str)
            self.period_list.append(new_period)

        print("Number of periods found: {}".format(len(self.period_list)))

    def set_monthly(self):
        agregated_reports = defaultdict(list)

        for report in self.report_list:
            year = report.date.year
            month = report.date.month
            dict_key = "{} {}".format(year, month)
            agregated_reports[dict_key].append(report)

        ordered_reports = OrderedDict(sorted(agregated_reports.items(),
                                             key = lambda t: t[1][0].date,
                                             reverse = True))

        for entry in ordered_reports:
            new_period = Period(ordered_reports[entry], self.period_str)
            self.period_list.append(new_period)

        print("Number of periods found: {}".format(len(self.period_list)))

    def set_annual(self):
        agregated_reports = defaultdict(list)

        for report in self.report_list:
            print (report)

        for report in self.report_list:
            agregated_reports[report.date.year].append(report)

        ordered_reports = OrderedDict(sorted(agregated_reports.items(),
                                             key = lambda t: t[1][0].date,
                                             reverse = True))

        for entry in ordered_reports:
            new_period = Period(ordered_reports[entry], self.period_str)
            self.period_list.append(new_period)

        print("Number of periods found: {}".format(len(self.period_list)))

    #TODO: set functins have some redundancy, review
    def get_agregated_report(self,period):
        pass

    #returns a tuple with (sum_vehicles, sum_passengers, sum_pedestrians)
    #TODO: use namedtuple
    def get_sums(self):
        sum_vehicles = 0
        sum_passengers = 0
        sum_pedestrians = 0

        for period in self.period_list:
            sum_vehicles += period.vehicles
            sum_passengers += period.passengers
            sum_pedestrians += period.pawns

        return {"vehicles": sum_vehicles,
                "passengers": sum_passengers,
                "pedestrians": sum_pedestrians}


    def get_tops(self):
        top_gates = Counter()
        top_countries = Counter()
        top_municipalities = Counter()

        for report in self.report_list:
            top_gates[report.gate.gate] += report.pawns + report.bicicles
            for entrance in report.entrances:
                top_countries[entrance.country.country] += entrance.passengers
                top_gates[report.gate.gate] += entrance.passengers
                if entrance.country.country == "Portugal":
                    top_municipalities[entrance.municipality.municipality] += (
                        entrance.passengers)

        return {"gates": dict(top_gates.most_common()),
                "countries": dict(top_countries.most_common()),
                "municipalities": dict(top_municipalities.most_common())}

    def get_totals(self):
        return Period(self.report_list)

    def to_dict(self):
        tops = self.get_tops()
        period_list = []
        for period in self.period_list:
            period_list.append(period.to_dict())

        return {
            "period_list": period_list,
            "tops": tops,
        }


class Period():
    vehicles = 0
    pawns = 0
    bicicles = 0
    passengers = 0
    persons = 0

    def __init__(self,report_list,period_str = None):
        if report_list:
            sorted_report_list = sorted(report_list,
                                         key = lambda x: x.date,
                                         reverse = True)

            self.end_date = sorted_report_list[0].date

            if len(sorted_report_list) == 1:
                self.start_date = sorted_report_list[0].date
            else:
                self.start_date = sorted_report_list[-1].date

            self.set_designation(period_str)

            self.entrances = []
            for report in report_list:
                self + report

            self.set_vehicles()


    def __repr__(self):
        return '<Period {} - {}>'.format(self.start_date, self.end_date)

    #adds a report to the period
    def __add__(self, report):
        self.vehicles += report.vehicles
        self.pawns += report.pawns
        self.bicicles += report.bicicles
        self.persons += report.pawns
        for entrance in report.entrances.all():
            if entrance.passengers:
                self.passengers += entrance.passengers
                self.persons += entrance.passengers
            self.entrances.append(entrance)

    def set_designation(self,period_str):
        if period_str == "Totais":
            self.designation = "T"

        elif period_str == "Diario" or period_str == "Diário":
            self.designation = "D: {}".format(
                self.start_date.strftime("%d-%m-%Y"))

        elif period_str == "Semanal":
            self.designation = "A: {} S: {}".format(
                self.start_date.isocalendar()[0],
                self.start_date.isocalendar()[1])

        elif period_str == "Mensal":
            self.designation = "A: {} M: {}".format(
                self.start_date.year, self.start_date.month)

        elif period_str == "Anual":
            self.designation = "A: {}".format(self.start_date.year)

        else:
            self.designation = self.__repr__()

    def set_vehicles(self):
        self.lightduty = 0
        self.lightdutyXL = 0
        self.caravans = 0
        self.busses = 0
        self.bikes = 0

        for entrance in self.entrances:
            if entrance.vehicle_type.vehicle_type == "Moto":
                self.bikes += 1
            elif entrance.vehicle_type.vehicle_type == "Ligeiro":
                self.lightduty += 1
            elif entrance.vehicle_type.vehicle_type == "Ligeiro XL":
                self.lightdutyXL += 1
            elif entrance.vehicle_type.vehicle_type == "Caravana":
                self.caravans += 1
            elif entrance.vehicle_type.vehicle_type == "Autocarro":
                self.busses += 1

    def to_dict(self):
        return {
            "designation": self.designation,
            "persons": self.persons,
            "pawns": self.pawns,
            "bicicles": self.bicicles,
            "passengers": self.passengers,
            "vehicles": self.vehicles,
            "bikes": self.bikes,
            "lightduty": self.lightduty,
            "lightdutyXL": self.lightdutyXL,
            "caravans": self.caravans,
            "busses": self.busses,
        }

