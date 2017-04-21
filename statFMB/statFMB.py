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
from .upload import update_database, save_corrections

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

    if request.method == 'POST' and 'file[]' in request.files:
        uploaded_files = request.files.getlist("file[]")
        upload_results = update_database(uploaded_files)

        vt_list = Vehicle_type.get_vehicle_types_list()
        c_list = Country.get_countries_list()
        m_list = Municipality.get_municipalities_list()

        return render_template("upload.html",
                               upload_results = upload_results,
                               vt_list = vt_list,
                               c_list = c_list,
                               m_list = m_list,
        )

    else:
        #TODO:handle file error warning
        print("!!err uploading file")
        render_template("upload.html")

    return redirect("/")

#TODO: create a way to save failed entrances and forget button
#TODO: rethink how the form posts the data see(JSON)
@app.route('/upload/finalize',methods=['GET','POST'])
def upload_finalize():

    if request.method == 'POST':
        #the form gives a number of lists with the data needed
        #get entrance values
        vt_list = request.form.getlist("vt")
        c_list = request.form.getlist("c")
        m_list = request.form.getlist("m")
        p_list = request.form.getlist("p")
        #get report list and number of entrances from each
        r_list = request.form.getlist("reports")
        ne_list = request.form.getlist("num_entrances")
        #get the failed values to insert in alias tables
        vt_failed_list = request.form.getlist("vt_failed")
        c_failed_list = request.form.getlist("c_failed")
        m_failed_list = request.form.getlist("m_failed")

        corrections_made = {}
        #places the current index being read
        index_bound = 0
        #iterates the lists to create a dict containing the data
        for i, report_id in enumerate(r_list):
            entrance = {}
            entrances_list = []
            for j in range(int(ne_list[i])):
                vehicle_type = vt_list[j + index_bound]
                vehicle_type_failed = vt_failed_list[j + index_bound]
                country = c_list[j + index_bound]
                country_failed = c_failed_list[j + index_bound]
                municipality = m_list[j + index_bound]
                municipality_failed = m_failed_list[j + index_bound]
                passengers = p_list[j+ index_bound]
                #TODO: this should be a subclass of Entrance
                entrance = {"vehicle_type" : vehicle_type,
                            "vehicle_type_failed" : vehicle_type_failed,
                            "country" : country,
                            "country_failed" : country_failed,
                            "municipality" : municipality,
                            "municipality_failed" : municipality_failed,
                            "passengers" : passengers
                }
                entrances_list.append(entrance)

            index_bound += int(ne_list[i])
            corrections_made[report_id] = entrances_list
        save_corrections(corrections_made)

    return redirect('/')

if __name__ == "__main__":
    app.run()
