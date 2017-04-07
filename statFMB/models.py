from .statFMB import db, gate_to_string

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
                                       .filter(Entrances.date >= lower_date)
                                       .filter(Entrances.date <= upper_date)
                                       .all())
        else:
            Entrances.searched_list = (Entrances.query
                                       .filter(Entrances.date >= lower_date)
                                       .filter(Entrances.date <= upper_date)
                                       .filter(Entrances.gate_id == int(gate))
                                       .all())

    #returns a dictionary ordered by top gate with the related gate entrances
    def get_top_gates():
        top_gates = {"Ameias": 0, "Serpa": 0, "Rainha": 0}
        for entrance in Entrances.searched_list:
            top_gates[gate_to_string(entrance.gate_id)] += 1

        sorted_top_gates = {}
        for key, value in sorted(top_gates.items(),
                                 key = lambda t: t[1],
                                 reverse = True):
            sorted_top_gates[key] = value
        return sorted_top_gates

    def get_sum_vehicles():
        sum_vehicles = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id != 1:
                sum_vehicles += 1
        return sum_vehicles

    def get_sum_passengers():
        sum_passengers = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id != 1:
                sum_passengers += entrance.n_persons
        return sum_passengers

    def get_sum_pedestrians():
        sum_pedestrians = 0
        for entrance in Entrances.searched_list:
            if entrance.entrance_type_id == 1:
                sum_pedestrians += entrance.n_persons
        return sum_pedestrians



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

