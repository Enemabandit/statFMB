from .statFMB import db, gate_to_string
from collections import Counter, OrderedDict

class Entrances(db.Model):
    __tablename__ = 'entrances'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    n_persons = db.Column(db.Integer)

    #ForeignKeys and relationships
    entrance_type_id = db.Column(db.Integer,db.ForeignKey('entrance_types.id'))
    entrance_type = db.relationship("Entrance_types")
    gate_id = db.Column(db.Integer,db.ForeignKey('gates.id'))
    gate = db.relationship("Gates")
    country_id = db.Column(db.Integer,db.ForeignKey('countries.id'))
    country = db.relationship("Countries")
    municipality_id = db.Column(db.Integer,db.ForeignKey('municipalities.id'))
    municipality = db.relationship("Municipalities")

    #contains the entrances list filtered by date and gate
    #TODO:initialize searched list on methods when it is not initialized
    searched_list = []

    #contains the entrances in period groups
    period_list = OrderedDict()

    ### Constructor for Entrances objects
    def __init__(self,id,date,
                 entrance_type_id,
                 gate_id,
                 n_persons = 0,
                 country_id = 1,
                 municipality_id = 999):
        self.id = id
        self.date = date
        self.n_persons = n_persons
        self.entrance_type_id = entrance_type_id
        self.gate_id = gate_id
        self.country = country
        self.municipality_id = municipality_id

    def __repr__():
        pass
    def __str__():
        pass

    #initializes the seached_list with all entrances filtered by the user input
    @classmethod
    def create_searched_list(cls,lower_date, upper_date, gate):
        if  int(gate) == 4:
            Entrances.searched_list = (cls.query
                                       .join(Gates)
                                       .join(Countries)
                                       .join(Municipalities)
                                       .join(Entrance_types)
                                       .filter(Entrances.date >= lower_date)
                                       .filter(Entrances.date <= upper_date)
                                       .all())
        else:
            Entrances.searched_list = (cls.query
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
    @classmethod
    def get_top_gates(cls):
        top_gates = {"Ameias": 0, "Serpa": 0, "Rainha": 0}
        for entrance in cls.searched_list:
            top_gates[gate_to_string(entrance.gate_id)] += entrance.n_persons
        return sort_dict(top_gates)

    @classmethod
    def get_top_countries(cls):
        top_countries = Counter()
        for entrance in cls.searched_list:
            current_country = entrance.country.country
            top_countries[current_country] += entrance.n_persons
        return top_countries.most_common(5)

    @classmethod
    def get_top_municipalities(cls):
        top_municipalities = Counter()
        for entrance in cls.searched_list:
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
    #TODO:think about turning Counter of Counters in instances of Entrances
    @classmethod
    def get_period_list(cls):
        period_entry = Counter()
        period_list = Counter()

        for entrance in cls.searched_list:
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
        cls.period_list = sorted_list
        return sorted_list

    @classmethod
    def get_period_list_totals(cls):
        totals = Counter()
        for period in cls.period_list:
            if totals != 0:
                totals += cls.period_list[period]
            else:
                totals = cls.period_list[period]
        print (totals)
        return totals


    #TODO: bicicles counting as vehicles, solve this
    @classmethod
    def get_sum_vehicles(cls):
        sum_vehicles = 0
        for entrance in cls.searched_list:
            if entrance.entrance_type_id != 1:
                sum_vehicles += 1
        return sum_vehicles

    #TODO: bicicles counting as vehicles,solve this
    @classmethod
    def get_sum_passengers(cls):
        sum_passengers = 0
        for entrance in cls.searched_list:
            if entrance.entrance_type_id != 1:
                sum_passengers += entrance.n_persons
        return sum_passengers

    #TODO: think about where to put biciles
    @classmethod
    def get_sum_pedestrians(cls):
        sum_pedestrians = 0
        for entrance in cls.searched_list:
            if entrance.entrance_type_id == 1:
                sum_pedestrians += entrance.n_persons
        return sum_pedestrians

    ###


class Entrance_types(db.Model):
    __tablename__ = 'entrance_types'
    id = db.Column(db.Integer, primary_key=True)
    entrance_type = db.Column(db.String(20))


class Gates(db.Model):
    __tablename__ = 'gates'
    id = db.Column(db.Integer, primary_key=True)
    gate = db.Column(db.String(20))


class Countries(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50))


class Municipalities(db.Model):
    __tablename__ = 'municipalities'
    id = db.Column(db.Integer, primary_key=True)
    municipality = db.Column(db.String(50))

###END OF DB.MODELS

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
        return None
