from flask import Flask, render_template, request, redirect, request, json
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
    RoleMixin, login_required, current_user, roles_required, roles_accepted, \
    logout_user
from flask_security.utils import encrypt_password
from datetime import date
from json import dumps

#TODO: setup SSL
#TODO: create instance for config (SECURITY)
#TODO: create a way to save failed entrances and forget button
#TODO: progress bar when uploading files
#TODO: some users don't change the hours in the report when working half days,
#      this needs to be reworked in order to get the needed data.
#TODO: !!IMPORTANT!!! alias are being created twice for diferent countries
#      and Municipalities (when prompted for correction in the same page twice),
#      this causes bug on finalizing upload! !*!*!*!*!*!*!*!
#TODO: Exceptions are not working properly, NEEDS REVIEW and test with debug off

app=Flask(__name__)
### this was added to solve a deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='mysql://statFMB:statFMB@localhost/test2'
app.config['SECRET_KEY'] = 'DontTellAnyone'
app.config['DEBUG'] = True

#security config
app.config['SECURITY_PASSWORD_SALT']='HMAC'

db = SQLAlchemy(app)

#models.py imports db, needs to be imported after db creation
from .models import *
from .db_create import create_tables
from .upload import update_database, save_corrections

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
#@app.before_first_request
#def create_user():
#    create_tables()
#    user_datastore.create_user(email='Administrador@fmb.pt',
#                               password='1234',
#                               name='Admin Adminus',
#                               phone= 919191911,
#                               alias= 'BOS')
#    user_datastore.add_role_to_user('Administrador@fmb.pt', 'Administrador')
#    user_datastore.create_user(email='visualizador@fmb.pt',
#                               password='1234',
#                               name='Viewer Vizualizus',
#                               phone= 929292922,
#                               alias= 'VIZ')
#    user_datastore.add_role_to_user('visualizador@fmb.pt', 'Visualizador')#
#
#    user_datastore.create_user(email='portageiro@fmb.pt',
#                               password='1234',
#                               name= 'Porti Portikus',
#                               phone= 939393933,
#                               alias= 'POR')
#    user_datastore.add_role_to_user('portageiro@fmb.pt', 'Portageiro')
#    db.session.commit()


@app.route('/')
@login_required
def index():
    return render_template("layout.html",
                               user_info = current_user.user_info())


@app.route('/logout')
@login_required
def logout():
    logout_user()


@app.route('/addUser', methods=['GET','POST'])
@roles_required('Administrador')
def addUser():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            alias = request.form['alias'].upper()
            password = encrypt_password(request.form['password'])
            phone = request.form['phone']
            role = request.form['role']

            print("-> Adding user: {}".format(name))
            print("-> Email: {}".format(email))
            print("-> Role: {}".format(role))

            user_datastore.create_user(email = email,
                                       password = password,
                                       name = name,
                                       phone = phone,
                                       alias= alias,
            )
            user_datastore.add_role_to_user(email, role)
            db.session.commit()
            print("-> User added with success!")
            return render_template("addUser.html",
                                   user_info = current_user.user_info(),
                                   warning = "success",
                                   user_added = name,

            )

        return render_template("addUser.html",
                               user_info = current_user.user_info(),
        )
    except Exception as e:
        print (str(e))
        return render_template("addUser.html",
                               user_info = current_user.user_info(),
                               warning = "error",
        )


@app.route('/listUsers')
@roles_required('Administrador')
def listUsers():
    try:
        user_list = User.get_user_list()
        return render_template("listUsers.html",
                               user_list = user_list,
                               user_info = current_user.user_info(),
        )
    except Exception as e:
        return (str(e))


@app.route('/toggleUserActivation', methods=['GET','POST'])
@roles_required('Administrador')
def toggleUserActivation():
    try:
        if request.method == 'POST':
            user = request.form['toggle']
            print("-> user {} activation toggled.")
            user_datastore.toggle_active(user_datastore.get_user(user))
            db.session.commit()

            return redirect('listUsers')
    except Exception as e:
        return (str(e))

@app.route('/stats',methods=['GET','POST'])
@roles_accepted('Administrador','Visualizador')
def stats():
    try:
        if request.method == 'POST':
            lower_date = request.form['lower_date']
            upper_date = request.form['upper_date']
            if lower_date > upper_date:
                date_error = True
                return render_template("statistics.html",
                                       date_warning = True,
                                       lower_date = date(2016,1,1),
                                       upper_date = date.today(),
                                       user_info = current_user.user_info(),
                )

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
                                       totals = totals,
                                       user_info = current_user.user_info(),
                )

        ###default route(/)
        lower_date = date(2016,1,1)
        upper_date = date.today()

        return render_template("statistics.html",
                               date_warning = False,
                               is_search = False,
                               upper_date = upper_date,
                               lower_date = lower_date,
                               user_info = current_user.user_info(),
        )

    except Exception as e:
        return(str(e))


@app.route('/charts',methods=['GET','POST'])
@roles_accepted('Administrador','Visualizador')
def charts():
    try:
        if request.method == 'POST':
            lower_date = request.form['lower_date']
            upper_date = request.form['upper_date']
            if lower_date > upper_date:
                date_error = True
                return render_template("statistics.html",
                                       date_warning = True,
                                       lower_date = date(2016,1,1),
                                       upper_date = date.today(),
                                       user_info = current_user.user_info(),
                )

            gate = request.form['gate']
            period_str = request.form['period']
            search = Search(lower_date, upper_date, gate, period_str)

            return render_template("charts.html",
                                   lower_date = lower_date,
                                   upper_date = upper_date,
                                   gate = gate,
                                   period_str = period_str,
                                   search_made = True,
                                   search = json.dumps(search.to_dict()),
                                   user_info = current_user.user_info(),
            )

        ###default route(/)
        lower_date = date(2016,1,1)
        upper_date = date.today()
        search = {}

        return render_template("charts.html",
                               lower_date = lower_date,
                               upper_date = upper_date,
                               search_made = False,
                               search = json.dumps(search),
                               user_info = current_user.user_info(),
        )
    except Exception as e:
        return(str(e))


@app.route('/upload',methods=['GET','POST'])
@roles_accepted('Administrador','Portageiro')
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

        return render_template("uploadFiles.html",
                               user_info = current_user.user_info(),
        )
    except Exception as e:
        return(str(e))


@app.route('/upload/finalize',methods=['GET','POST'])
@roles_accepted('Administrador','Portageiro')
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
        return redirect('/upload')

    except Exception as e:
        return(str(e))


@app.route('/under_construction')
def underConstruction():
    return render_template("underConstruction.html",
                               user_info = current_user.user_info())


if __name__ == "__main__":
    app.run()
