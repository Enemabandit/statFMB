from flask import Flask, render_template, request, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app=Flask(__name__)
##TODO: create instance for config (SECURITY)
### this was added to solve a deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://statFMB:statFMB@localhost/test'
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['DEBUG'] = True

db = SQLAlchemy(app)
session = db.session.connection()

def gate_to_string(gate):
    return{
        1:"Ameias",
        2:"Serpa",
        3:"Rainha",
        4:"Todas",
    }.get(int(gate))

#models.py imports db, needs to be imported after db creation
from .models import *

###Website structure
@app.route('/',methods=['GET','POST'])
def index():

    if request.method == 'POST':
        lower_date = request.form['lower_date']
        upper_date = request.form['upper_date']

        #check date range and renders the warning if invalid
        if lower_date > upper_date:
            date_error = True
            return render_template("index.html",
                                   date_warning = True,
                                   lower_date = date(2001,1,1),
                                   upper_date = date.today())


        gate = request.form['gate']
        #TODO:filter by period of time
        #period = request.form['period']

        Entrances.create_searched_list(lower_date, upper_date,gate)

        sum_vehicles = Entrances.get_sum_vehicles()
        sum_passengers = Entrances.get_sum_passengers()
        sum_pedestrians = Entrances.get_sum_pedestrians()

        top_gates = Entrances.get_top_gates()
        top_countries = Entrances.get_top_countries()
        top_municipalities = Entrances.get_top_municipalities()

        period_list = Entrances.get_period_list()
        period_list_totals = Entrances.get_period_list_totals()

        return render_template("index.html",
                               date_warning = False,
                               upper_date = upper_date,
                               lower_date = lower_date,
                               gate = gate_to_string(gate),
                               sum_vehicles = sum_vehicles,
                               sum_passengers = sum_passengers,
                               sum_pedestrians = sum_pedestrians,
                               top_gates = top_gates,
                               top_countries = top_countries,
                               top_municipalities = top_municipalities,
                               period_list = period_list,
                               period_list_totals = period_list_totals,
        )

    ###default route(/)
    #TODO: set lower_date to inauguration date
    lower_date = date(2010,1,1)
    upper_date = date.today()
    return render_template("index.html",
                           date_warning = False,
                           upper_date = upper_date,
                           lower_date = lower_date)


@app.route('/charts',methods=['GET','POST'])
def charts():
    return redirect("/")


#TODO: don't let files be uploaded more than once
@app.route('/upload',methods=['GET','POST'])
def upload():
    from .upload import update_database

    if request.method == 'POST' and 'file[]' in request.files:
        uploaded_files = request.files.getlist("file[]")

        #TODO: validate files
        for current_file in uploaded_files:
            update_database(current_file)
    else:
        #TODO:handle file error warning
        print("!!err uploading file")

    return redirect("/")
