from openpyxl import load_workbook, worksheet
from datetime import date
from .statFMB import (db, Report, Entrance, Shift, Gate,
                      Vehicle_type, Country, Municipality)

#TODO: error views for upload, read sheets, date, gate, shift, report
##

#returns a Dict with results from the update, indexed by file
def update_database(new_files):

    upload_results = {}
    for new_file in new_files:

        report, entrance_obj_list, error_list = upload_file(new_file)
        upload_results[new_file.filename] = [report,
                                             entrance_obj_list,
                                             error_list]

    return upload_results

def upload_file(new_file):
    print("inserting: {} in database.".format(new_file.filename))

    ##load uploaded file and sheets
    wb = load_workbook(new_file, read_only = True, data_only = True)
    statSheet = wb.get_sheet_by_name("Estatística")
    regSheet = wb.get_sheet_by_name("Folha de Registo")

    ##date
    date = format_date(regSheet['C6'].value)
    print("==> date: {}".format(date))

    ##gate
    gate_str = regSheet['A4'].value.rsplit(' ',1)[-1].capitalize()
    if gate_str not in ["Ameias","Serpa","Rainha"]:
        #TODO: error views
        print("==>could not find gate!")
    gate = Gate.get_gate(gate_str)

    ##shift
    shift_str = get_shift(regSheet)
    print ("==> Shift: " + shift_str)
    shift = Shift.get_shift(shift_str)

    ##total_vehicles
    total_vehicles = get_total_vehicles(regSheet)
    print ("==> Vehicles: " + str(total_vehicles))

    #pawns
    pawns = get_pawns(statSheet)
    print ("==> Pawns: " + str(pawns))

    #bicicles
    bicicles = get_bicicles(statSheet)
    print ("==> Bicicles: " + str(bicicles))

    report = Report(date = date,
                    vehicles = total_vehicles,
                    pawns = pawns,
                    bicicles = bicicles,
                    gate = gate,
                    shift = shift
    )
    print("==> Report Created!")

    print("==> Instanciating entrances!")
    #entrances
    entrance_obj_list, error_list = get_entrance_list(statSheet,report)
    print ("==> Entrances registered: {}".format(len(entrance_obj_list)))
    print ("==> Errors found: {}".format(len(error_list)))

    #passengers
    passengers = 0
    for entrance in entrance_obj_list:
        passengers += entrance.passengers

    print ("All instances Created, updating database!")
    if Report.is_eligible(date,shift):
        db.session.add(report)
        for entrance in entrance_obj_list:
            db.session.add(entrance)
        db.session.commit()
        print("database updated for: {}".format(new_file.filename))
    else:
        #TODO: implement override
        print("Override not implemented")

    return report, entrance_obj_list, error_list


def get_shift(sheet):

    start = sheet['R5'].value
    end = sheet['V5'].value

    shift = "Meio" if end - start < 8 else "Completo"

    return shift


def get_total_vehicles(sheet):
    result = 0
    for row in sheet.iter_rows(min_col = 20,
                               max_col = 20,
                               min_row = 11,
                               max_row = 18,):
        for cell in row:
            if cell.value:
                result += cell.value
    return result


def get_pawns(sheet):
    col_number = 1
    col_leter = 'A'
    lower_bound = "N.º entradas a pé"
    interval = find_row_interval(sheet,
                                 col_number,
                                 lower_delimiter = lower_bound)

    pawn_list = str_to_int_list(sheet[col_leter + str(interval[0]+1) :
                                      col_leter + str(interval[1])])

    return sum(pawn_list)


def get_bicicles(sheet):
    col_number = 9
    col_leter = 'I'
    lower_bound = "N.º entradas de bicicleta"
    interval = find_row_interval(sheet,
                                 col_number,
                                 lower_delimiter = lower_bound)

    bicicle_list = str_to_int_list(sheet[col_leter + str(interval[0]+1) :
                                         col_leter + str(interval[1])])
    return sum(bicicle_list)


#returns a tuple (entrance_obj_list, error_list)
def get_entrance_list(sheet,report):
    #get list of payed entrances
    col_number = 1
    upper_bound = "Dados visitantes veículos pagantes"
    lower_bound = "Dados visitantes veículos não pagantes " + \
                  "(hóspedes, reuniões, outros)"
    interval = find_row_interval(sheet, col_number,
                                 upper_bound, lower_bound)
    entrance_obj_list = []
    error_list = []

    for row in sheet.iter_rows(min_row=interval[0]+2,
                               max_row=interval[1]-1,
                               max_col=19):
        if row[0].value:
            vehicle_type = Vehicle_type.clean_str(row[0].value.capitalize())

            if row[6].value: passengers = row[6].value
            else: passengers = 0

            #TODO: VALIDATE
            if row[12].value: country = row[12].value.capitalize()
            else: country = ""

            #TODO: VALIDATE
            if row[18].value: municipality = row[18].value.capitalize()
            else: municipality = ""

            #test if everything is valid
            if vehicle_type != "invalid" and country != "" and municipality != "":
                entrance = Entrance(passengers = passengers,
                                    report = report,
                                    vehicle_type = Vehicle_type(vehicle_type),
                                    country = Country(country),
                                    municipality = Municipality(municipality),
                )

                entrance_obj_list.append(entrance)
            else:
                error_list.append([vehicle_type,passengers,country,municipality])
    return entrance_obj_list, error_list


#returns the row interval between lower_delimiter and upper_delimiter
def find_row_interval(sheet, column = 1,
                      lower_delimiter = None, upper_delimiter = None):
    upper_bound = 0
    lower_bound = 0

    for row in sheet.iter_rows(min_col = column-1,max_col = column):
        for cell in row:
            if lower_delimiter:
                if cell.value == lower_delimiter:
                    lower_bound = cell.row
            else:
                upper_delimiter = 0

            if upper_delimiter:
                if cell.value == upper_delimiter:
                    upper_bound = cell.row
            else:
                upper_delimiter = sheet.max_row

    return (lower_bound,upper_bound)


#expects a string "dd-mm-yyyy" or "dd/mm/yyyy" and formats to iso
def format_date(d):
    if len(d.split('/')) == 3:
        d_list = d.split('/')
    elif len(d.split('-') == 3):
        d_list = d.split('-')
    else:
        #return error
        print("error spliting date")

    try:
        formated_date = date(int(d_list[2]),int(d_list[1]),int(d_list[0]))
    except ValueError:
        #TODO:error views
        print("could not find date!")

    return formated_date


def str_to_int_number(n):
    n_str = ''.join(c for c in n if c.isdigit())
    return int(n_str)


def str_to_int_list(l):
    new_list = []
    for element in l:
        if element[0].value != None:
            new_list.append(str_to_int_number(str(element[0].value)))
    return new_list
