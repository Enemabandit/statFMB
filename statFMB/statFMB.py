from flask import Flask, render_template, request, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app=Flask(__name__)
##TODO: create instance for config (SECURITY)
### this was added to solve a deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://statFMB:statFMB@localhost/test1'
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

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
        period = request.form['period']

        Report.create_search_list(lower_date, upper_date,gate)

        print(Report.search_list)

        #sum_vehicles = Entrances.get_sum_vehicles()
        #sum_passengers = Entrances.get_sum_passengers()
        #sum_pedestrians = Entrances.get_sum_pedestrians()

        #top_gates = Entrances.get_top_gates()
        #top_countries = Entrances.get_top_countries()
        #top_municipalities = Entrances.get_top_municipalities()

        #period_list = Entrances.get_period_list()
        #period_list_totals = Entrances.get_period_list_totals()

        return render_template("index.html",
                               date_warning = False,
                               upper_date = upper_date,
                               lower_date = lower_date,
                               gate = gate,
         #                      sum_vehicles = sum_vehicles,
         #                      sum_passengers = sum_passengers,
         #                      sum_pedestrians = sum_pedestrians,
         #                      top_gates = top_gates,
         #                      top_countries = top_countries,
         #                      top_municipalities = top_municipalities,
         #                      period_list = period_list,
         #                      period_list_totals = period_list_totals,
        )

    ###default route(/)
    #TODO: set lower_date to inauguration date
    lower_date = date(2010,1,1)
    upper_date = date.today()

    #NOTE: to create table uncomment this on first install
    #TODO: rework this, rly ugly!!
    #from .db_create import create_tables
    #create_tables()


    return render_template("index.html",
                           date_warning = False,
                           upper_date = upper_date,
                           lower_date = lower_date)


@app.route('/charts',methods=['GET','POST'])
def charts():
    return redirect("/")


#TODO: handle error when user doesn't select file
@app.route('/upload',methods=['GET','POST'])
def upload():
    from .upload import update_database

    if request.method == 'POST' and 'file[]' in request.files:
        uploaded_files = request.files.getlist("file[]")
        upload_results = update_database(uploaded_files)

        for result in upload_results:
            print (result)
            for l in upload_results[result]:
                print (l)

    else:
        #TODO:handle file error warning
        print("!!err uploading file")
        render_template("upload.html")

    return render_template("upload.html")
