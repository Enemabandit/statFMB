import os
from flask import Flask, render_template, request, redirect, request, json, \
    send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
    RoleMixin, login_required, current_user, roles_required, roles_accepted, \
    logout_user
from flask_security.utils import encrypt_password, verify_password
from datetime import date, datetime
from json import dumps
from flask_socketio import SocketIO, emit
from flask_weasyprint import HTML, render_pdf

#TODO: IMPORTANT!!! reorganize the import system
#TODO: setup SSL
#TODO: websockets to log user disconnection
#TODO: websockets might bring some security vulns (look into it)
#TODO: create a way to save failed entrances and forget button
#TODO: progress bar when uploading files(sockets)
#TODO: config from objects
#TODO: redo how save button in finalizeUploads work when there is only file
#      and it errors

app = Flask('statFMB')
app.config.from_pyfile('config.cfg')
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

db = SQLAlchemy(app)

#models.py imports db, needs to be imported after db creation
from statFMB.models import *
from statFMB.db_create import create_tables
from statFMB.upload import update_database, save_corrections
from statFMB.utils import Alert
from statFMB.files import  delete_file, copy_to_validated_folder, get_file_path

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
socketio = SocketIO(app)

# Create users to test with
# @app.before_first_request
# def create_user():
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
#    user_datastore.add_role_to_user('visualizador@fmb.pt', 'Visualizador')##

#    user_datastore.create_user(email='portageiro@fmb.pt',
#                               password='1234',
#                               name= 'Porti Portikus',
#                               phone= 939393933,
#                               alias= 'POR')
#    user_datastore.add_role_to_user('portageiro@fmb.pt', 'Portageiro')
#    db.session.commit()

#Create debug user
#@app.before_first_request
#def create_debug_user():
#    user_datastore.create_user(email='debug@fmb.pt',
#                               password='1234',
#                               name= 'Debugus Maximus',
#                               phone= 666666666,
#                               alias= 'DEB')
#    user_datastore.add_role_to_user('debug@fmb.pt', 'Administrador')
#    db.session.commit()

#VIEWS
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect("/userLogin")
    else:
        return render_template("index.html",
                               current_user= current_user.to_dict())


@app.route('/userLogin')
@login_required
def userLogin():
    log = Log(description = "Entrou", user = current_user)
    db.session.add(log)
    db.session.commit()
    return redirect("/")


@app.route('/userLogout')
@login_required
def userLogout():
    log = Log(description = "Saiu", user = current_user)
    db.session.add(log)
    db.session.commit()
    logout_user()
    return redirect('/')


@app.route('/personalData', methods=['GET','POST'])
@login_required
def personalData():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            if current_user.roles[0].name == "Administrador":
                alias = request.form['alias'].upper()
            else:
                alias = current_user.alias
            print("-> Modifying user: {}".format(current_user.email))

            if current_user.is_eligible_for_editing(email = email,
                                                    alias = alias):
                current_user.email = email
                current_user.alias = alias
                current_user.name = name
                current_user.phone = phone

                description = "Dados pessoais editados"
                print(description)
                alert = Alert(category = "success",
                              title = "Sucesso",
                              description = description,
                )
                log = Log(description = description, user = current_user)
                db.session.add(log)
                db.session.commit()
            else:
                description = current_user.get_ineligible_description(email,
                                                                      alias)
                print("-> Error, {}".format(description))
                alert = Alert(category = "danger",
                              title = "Erro",
                              description = description)

            return render_template("personalData.html",
                                   current_user = current_user.to_dict(),
                                   alert_data = alert,
                                   user = current_user,

            )
        else:
            alert = Alert(category = "none")

        return render_template("personalData.html",
                               current_user = current_user.to_dict(),
                               user = current_user,
                               alert_data = alert.to_dict(),
        )
    except Exception as e:
        print (str(e))
        return render_template("personalData.html",
                               current_user = current_user.to_dict(),
                               user = current_user,
                               alert_data = Alert(),
        )


@app.route('/changePassword', methods=['GET','POST'])
@login_required
def changePassword():
    try:
        if request.method == 'POST':
            old_password = request.form['old_password']
            new_password = encrypt_password(request.form['new_password'])

            if verify_password(old_password,current_user.password):
                current_user.password = new_password
                description = ("Password alterada")
                print(description)
                alert = Alert(category = "success",
                              title = "Sucesso",
                              description = description)
                log = Log(description = description, user = current_user)
                db.session.add(log)
                db.session.commit()
            else:
                alert = Alert(category = "danger",
                              title = "Erro",
                              description = "Password antiga incorreta.")

            return render_template("changePassword.html",
                                   current_user = current_user.to_dict(),
                                   alert_data = alert,
            )


        return render_template("changePassword.html",
                               current_user = current_user.to_dict(),
                               user = current_user,
        )
    except Exception as e:
        print (str(e))
        return render_template("personalData.html",
                               current_user = current_user.to_dict(),
                               user = current_user,
                               alert_data = Alert(),
        )


@app.route('/under_construction')
@login_required
def underConstruction():
    return render_template("underConstruction.html",
                               current_user = current_user.to_dict())


@app.route('/chat')
@login_required
def chat():
    return render_template("chat.html",
                           current_user = current_user.to_dict())


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

            if User.is_available(email,alias):
                user_datastore.create_user(email = email,
                                           password = password,
                                           name = name,
                                           phone = phone,
                                           alias= alias,
                )
                user_datastore.add_role_to_user(email, role)

                description = "Utilizador {} adicionado".format(email)
                print(description)
                alert = Alert(category = "success",
                              title = "Sucesso",
                              description = description)
                log = Log(description = description,
                          user = current_user)
                db.session.add(log)
                db.session.commit()
            else:
                print("-> Error, unavailable data for database")
                alert = Alert (category = "danger",
                               title = "Erro",
                               description = "Utilizador com: {}já existe.".
                               format(User.get_unavailable_description(email,
                                                                       alias)))

        else:
            alert = Alert(category = "none")

        return render_template("addUser.html",
                               current_user = current_user.to_dict(),
                               alert_data = alert.to_dict(),
        )
    except Exception as e:
        print (str(e))
        return render_template("addUser.html",
                               current_user = current_user.to_dict(),
                               alert_data = Alert(),
        )


@app.route('/pendingPdf', methods=['GET','POST'])
@roles_required('Administrador')
def pendingPdf():
    report_list = Report.get_unvalidated_reports()
    printable_reports = []
    for report in report_list:
        printable_reports.append(report.to_dict())

    html = render_template('pendingPdf.html',
                           report_list = printable_reports,
                           date = date.today(),
    )

    filename = "Receitas Pendentes {}.pdf".format(
        date.today().strftime("%d/%m/%Y"))

    return render_pdf(HTML(string=html),
                      #NOTE: comment this to open the pdf in a new tab
                      download_filename = filename,
    )


@app.route('/editUser', methods=['GET','POST'])
@roles_required('Administrador')
def editUser():
    try:
        if request.method == 'POST':
            editing = request.form["editing"]
            email_to_edit = request.form["email_to_edit"]
            user_to_edit = user_datastore.get_user(email_to_edit)

            #this only comes true when the POST request comes from editUser.html
            #NOTE: this may generate parameter tampering vulnaberabilities,
            #      should be fine since it requires admin previleges to access
            #      this function
            if editing == "True":
                print("-> Editing user {}.".format(user_to_edit.name))
                name = request.form["name"]
                email = request.form["email"]
                alias = request.form["alias"].upper()
                phone = request.form["phone"]
                role = request.form["role"]
                password = request.form["password"]

                if user_to_edit.is_eligible_for_editing(email = email,
                                                        alias = alias):
                    user_to_edit.name = name
                    user_to_edit.email = email
                    user_to_edit.alias = alias
                    user_to_edit.phone = phone
                    if password != "":
                        user_to_edit.password = password

                    user_datastore.remove_role_from_user(user_to_edit,
                                                         user_to_edit.get_role()
                    )
                    user_datastore.add_role_to_user(user_to_edit,role)

                    description = ("Utilizador {} editado".
                                   format(user_to_edit.email))
                    print(description)
                    alert = Alert(category = "success",
                                  title = "Sucesso",
                                  description = description)
                    log = Log(description = description,
                              user = current_user)
                    db.session.add(log)
                    db.session.commit()
                    return render_template("listUsers.html",
                                           current_user =current_user.to_dict(),
                                           alert_data = alert,
                                           user_list = User.get_user_list(),
                    )
                else:
                    description = user_to_edit.get_ineligible_description(email,
                                                                          alias)
                    print("-> Error, {}".format(description))
                    alert = Alert(category = "danger",
                                  title = "Erro",
                                  description = description)

            else:
                alert = Alert(category = "none")
            return render_template("editUser.html",
                                   current_user =current_user.to_dict(),
                                   user = user_to_edit.to_dict(),
                                   alert_data = alert,
            )
        else:
            return redirect('/')

    except Exception as e:
        print (str(e))
        return render_template("listUsers.html",
                               current_user = current_user.to_dict(),
                               user_list = User.get_user_list(),
                               alert_data = Alert(),
        )


@app.route('/listUsers')
@roles_required('Administrador')
def listUsers():
    try:
        user_list = User.get_user_list()
        return render_template("listUsers.html",
                               user_list = user_list,
                               current_user = current_user.to_dict(),
        )
    except Exception as e:
        return (str(e))


@app.route('/toggleUserActivation', methods=['GET','POST'])
@roles_required('Administrador')
def toggleUserActivation():
    try:
        if request.method == 'POST':
            user_email = request.form['toggle']
            user = user_datastore.get_user(user_email)

            if user.active:
                description = "Utilizador {} desativado".format(user.email)
            else:
                description = "Utilizador {} ativado".format(user.email)
            print(description)

            user_datastore.toggle_active(user)
            log = Log(description = description, user = current_user)
            db.session.add(log)
            db.session.commit()

            return redirect('listUsers')
    except Exception as e:
        return (str(e))


@app.route('/logs', methods=['GET','POST'])
@roles_required('Administrador')
def logs():
    try:
        user_list = User.get_user_list()
        lower_date = date(2016,1,1)
        upper_date = date.today()
        logs_list = None

        if request.method == 'POST':
            lower_date = request.form['lower_date']
            upper_date = request.form['upper_date']
            lower_time = datetime.strptime(lower_date,"%Y-%m-%d")
            upper_time = datetime.strptime((upper_date + "-23-59-59"),
                                           "%Y-%m-%d-%H-%M-%S")
            user_email = request.form['email']
            if lower_date > upper_date:
                lower_date = date(2016,1,1)
                upper_date = date.today()
                alert = Alert(category = "error",
                              title = "Erro",
                              description = ("Data de inicio tem de"
                                             + " ser anterior à data de fim")
                )
            else:
                if user_email != "Todos":
                    user = user_datastore.get_user(user_email)
                    logs_list = Log.get_logs(user = user,
                                             lower_time = lower_time,
                                             upper_time = upper_time)
                else:
                    logs_list = Log.get_logs(lower_time = lower_time,
                                             upper_time = upper_time)

                if logs_list == None:
                    alert = Alert(category = "warning",
                                  title = "",
                                  description = "Nenhum registo encontrado.")
                else:
                    alert = Alert(category = "none")
        else:
            alert = Alert(category = "none")

        return render_template("logs.html",
                               user_list = user_list,
                               lower_date = lower_date,
                               upper_date = upper_date,
                               logs_list = logs_list,
                               current_user = current_user.to_dict(),
                               alert_data = alert,
        )
    except Exception as e:
        return (str(e))


@app.route('/validateReport', methods=['GET','POST'])
@roles_required('Administrador')
def validateReport():
    try:
        if request.method == 'POST':
            report_id = request.form['report_id']
            report = Report.get_report_by_id(report_id)
            copy_to_validated_folder(report.get_filename())
            report.validated = True

            print("=> Report {} validated".format(report))
            description = "receita {} validada.".format(report)
            log = Log(description = "Validou receita {}".format(report),
                      user = current_user)
            alert = Alert(category = "success",
                          title = "Sucesso",
                          description = description)
            db.session.add(log)
            db.session.commit()
        else:
            alert = Alert("none")

        report_list = Report.get_unvalidated_reports()
        printable_reports = []
        for report in report_list:
            printable_reports.append(report.to_dict())

        return render_template("validateReports.html",
                               current_user = current_user.to_dict(),
                               report_list = printable_reports,
                               alert_data = alert,
        )
    except Exception as e:
        return (str(e))


@app.route('/downloadReport', methods=['GET','POST'])
@roles_required('Administrador')
def downloadReport():
    try:
        if request.method == 'POST':
            report_id = request.form['report_id']
            report = Report.get_report_by_id(report_id)
            validated = report.is_validated()

            full_path = get_file_path(report.get_filename(),validated)
            filename = full_path.split(os.sep)[-1]

            print("=> Report {} downloaded".format(report))
            description = "Descarregou {}.".format(report)
            log = Log(description = "descarregou {}".format(report),
                      user = current_user)
            db.session.add(log)
            db.session.commit()

        return send_file(filename_or_fp = full_path,
                         as_attachment=True,
                         attachment_filename=filename)

    except Exception as e:
        return (str(e))


@app.route('/deleteReport', methods=['GET','POST'])
@roles_required('Administrador')
def deleteReport():
    try:
        if request.method == 'POST':
            report_id = request.form['report_id']
            report = Report.get_report_by_id(report_id)
            validated = report.is_validated()
            date = report.date

            entrances = Entrance.get_entrances_of_report(report)
            for entrance in entrances:
                db.session.delete(entrance)
            db.session.delete(report)

            filename = report.get_filename()
            delete_file(filename = filename,validated = validated)

            print("=> report {} eliminated.".format(report))
            description = "receita {} Eliminada.".format(report)
            log = Log(description = "Eliminou receita {}".format(report),
                      user = current_user)
            alert = Alert(category = "success",
                          title = "Sucesso",
                          description = description)
            db.session.add(log)
            db.session.commit()

            if validated == True:
                template = "listReports.html"
                report_list = Report.get_report_list(date,date)
                printable_reports = []
                for report in report_list:
                    printable_reports.append(report.to_dict())
            else:
                template = "validateReports.html"
                report_list = Report.get_unvalidated_reports()
                printable_reports = []
                for report in report_list:
                    printable_reports.append(report.to_dict())

            return render_template(template,
                                   current_user = current_user.to_dict(),
                                   date = date,
                                   report_list = printable_reports,
                                   alert_data = alert,
            )

    except Exception as e:
        return (str(e))


@app.route('/listReports', methods=['GET','POST'])
@roles_required('Administrador')
def listReports():
    try:
        if request.method == 'POST':
            date = request.form['date']
            report_list = Report.get_report_list(date,date)
            printable_reports = []
            for report in report_list:
                printable_reports.append(report.to_dict())

            if printable_reports == []:
                alert = Alert(category = "warning",
                              title = "Atenção",
                              description= "nenhuma receita validada para esta data")
            else:
                alert = Alert(category = "none")
        else:
            printable_reports = []
            alert = Alert(category = "none")

        return render_template("listReports.html",
                               current_user = current_user.to_dict(),
                               report_list = printable_reports,
                               alert_data = alert,
        )
    except Exception as e:
        return (str(e))


@app.route('/validateReports', methods=['GET'])
@roles_required('Administrador')
def validateReports():
    try:
        report_list = Report.get_unvalidated_reports()
        printable_reports = []
        for report in report_list:
            printable_reports.append(report.to_dict())

        if printable_reports == []:
            alert = Alert(category = "warning",
                          title = "Atenção",
                          description = "nenhuma receita pendente")
        else:
            alert = Alert(category = "none")

        return render_template("validateReports.html",
                               current_user = current_user.to_dict(),
                               report_list = printable_reports,
                               alert_data = alert,
        )
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
                                       current_user = current_user.to_dict(),
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
                                       current_user = current_user.to_dict(),
                )

        ###default route(/)
        lower_date = date(2016,1,1)
        upper_date = date.today()
        return render_template("statistics.html",
                               date_warning = False,
                               is_search = False,
                               upper_date = upper_date,
                               lower_date = lower_date,
                               current_user = current_user.to_dict(),
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
                                       current_user = current_user.to_dict(),
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
                                   current_user = current_user.to_dict(),
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
                               current_user = current_user.to_dict(),
        )
    except Exception as e:
        return(str(e))


@app.route('/upload',methods=['GET','POST'])
@roles_accepted('Administrador','Portageiro')
def upload():
    try:
        if request.method == 'POST' and 'files' in request.files:
            uploaded_files = request.files.getlist("files")
            if current_user.get_role() == "Administrador":
                user_email = request.form['email']
                user = user_datastore.get_user(user_email)
                print(user)
            else:
                user = current_user
            upload_results, failed_uploads = update_database(uploaded_files,
                                                             user)

            vt_list = Vehicle_type.get_vehicle_types_list()
            c_list = sorted(Country.get_countries_list())
            m_list = sorted(Municipality.get_municipalities_list())


            return render_template("upload.html",
                                   upload_results = upload_results,
                                   failed_uploads = failed_uploads,
                                   vt_list = vt_list,
                                   c_list = c_list,
                                   m_list = m_list,
            )

        return render_template("uploadFiles.html",
                               current_user = current_user.to_dict(),
                               user_list = User.get_users_by_role("Portageiro"),
        )
    except Exception as e:
        return(str(e))


@app.route('/schedule',methods=['GET','POST'])
@roles_accepted('Administrador','Portageiro')
def schedule():
    return render_template("schedule.html",
                           current_user = current_user.to_dict(),
                           user_list = User.get_users_by_role("Portageiro"),
    )


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


##SOCKEIO interface
@socketio.on('chat')
def chat_event(json):
    socketio.emit('chat-response',json)


@socketio.on('chat-login')
def chat_login(json):
    socketio.emit('login-response',json)


@socketio.on('chat-logout')
def chat_logout(json):
    socketio.emit('logout-response', json)
