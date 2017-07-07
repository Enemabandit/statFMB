from flask import Flask, render_template, request, redirect, request, json
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from json import dumps


app=Flask(__name__)
##TODO: create instance for config (SECURITY)
### this was added to solve a deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#change database name(URL) here
app.config['SQLALCHEMY_DATABASE_URI']='mysql://statFMB:statFMB@localhost/test1'
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

#models.py imports db, needs to be imported after db creation
from .models import *
from .charts import *
from .upload import update_database, save_corrections

###Website structure

@app.route('/',methods=['GET','POST'])
def index():
    try:
        if request.method == 'POST':
            lower_date = request.form['lower_date']
            upper_date = request.form['upper_date']
            if lower_date > upper_date:
                date_error = True
                return render_template("statistics.html",
                                       date_warning = True,
                                       lower_date = date(2001,1,1),
                                       upper_date = date.today())

            gate = request.form['gate']
            period_str = request.form['period']
            search = Search(lower_date, upper_date, gate, period_str)

            if search.period_list:
                sums = search.get_sums()
                tops = search.get_tops()

                period_list = []
                if period_str != "Totais":
                    period_list = search.period_list

                totals = search.get_totals()

                return render_template("statistics.html",
                                       date_warning = False,
                                       search_is_valid = True,
                                       upper_date = upper_date,
                                       lower_date = lower_date,
                                       gate = gate,
                                       period_str = period_str,
                                       tops = tops,
                                       sums = sums,
                                       period_list = period_list,
                                       totals = totals,)

        ###default route(/)
        #TODO: set lower_date to inauguration date
        lower_date = date(2010,1,1)
        upper_date = date.today()

        #NOTE: to create table uncomment this on first install
        #TODO: rework this, rly ugly!!
        #from .db_create import create_tables
        #create_tables()

        return render_template("statistics.html",
                               date_warning = False,
                               is_search = False,
                               upper_date = upper_date,
                               lower_date = lower_date)

    except Exception as e:
        return(str(e))


@app.route('/charts',methods=['GET','POST'])
def charts():
    try:
        if request.method == 'POST':
            lower_date = request.form['lower_date']
            upper_date = request.form['upper_date']
            if lower_date > upper_date:
                date_error = True
                return render_template("statistics.html",
                                       date_warning = True,
                                       lower_date = date(2001,1,1),
                                       upper_date = date.today())

            gate = request.form['gate']
            period_str = request.form['period']
            search = Search(lower_date, upper_date, gate, period_str)

            print(Search_json_encoder().encode(search))

            return render_template("charts.html",
                                   lower_date = lower_date,
                                   upper_date = upper_date,
                                   gate = gate,
                                   period_str = period_str,
                                   search = json.dumps(search.to_dict()),
            )

        ###default route(/)
        #TODO: set lower_date to inauguration date
        lower_date = date(2010,1,1)
        upper_date = date.today()

        return render_template("charts.html",
                               lower_date = lower_date,
                               upper_date = upper_date,
        )
    except Exception as e:
        return(str(e))


#TODO: page to search for one single report
@app.route('/reports',methods=['GET','POST'])
def reports():
    return redirect("/")


@app.route('/upload',methods=['GET','POST'])
def upload():
    try:
        if request.method == 'POST' and 'file[]' in request.files:
            uploaded_files = request.files.getlist("file[]")
            upload_results, failed_uploads = update_database(uploaded_files)

            vt_list = Vehicle_type.get_vehicle_types_list()
            c_list = Country.get_countries_list()
            m_list = Municipality.get_municipalities_list()

            return render_template("upload.html",
                                   upload_results = upload_results,
                                   failed_uploads = failed_uploads,
                                   vt_list = vt_list,
                                   c_list = c_list,
                                   m_list = m_list,
            )

        return render_template("uploadFiles.html")
    except Exception as e:
        return(str(e))


#TODO: create a way to save failed entrances and forget button
@app.route('/upload/finalize',methods=['GET','POST'])
def upload_finalize():
    try:
        if request.method == 'POST':
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

    except Exception as e:
        return(str(e))

if __name__ == "__main__":
    app.run()
