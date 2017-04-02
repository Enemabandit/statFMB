from flask_sqlalchemy import SQLAlchemy
from statFMB import app

#app = Flask(__name__)
### this was added to solve a deprecation warning
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://statFMB:statFMB@localhost/test'
 
db = SQLAlchemy(app)

class Entrances(db.Model):
    __tablename__ = 'entrances'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    n_persons = db.Column(db.Integer)

    entrance_type_id = db.Column(db.Integer,db.ForeignKey('entrance_types.id'))
    entrance_type = db.relationship("Entrance_types")

    gate_id = db.Column(db.Integer,db.ForeignKey('gates.id'))
    gate = db.relationship("Gates")
    country_id = db.Column(db.Integer,db.ForeignKey('countries.id'))
    country = db.relationship("Countries")
    municipality_id = db.Column(db.Integer,db.ForeignKey('municipalities.id'))
    municipality = db.relationship("Municipalities")

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
