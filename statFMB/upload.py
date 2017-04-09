from openpyxl import load_workbook, worksheet
from datetime import date
from .statFMB import db
from .models import Entrances

#TODO: don't let files be uploaded more than once
#TODO: error handling
def update_database(new_file):
    print("inserting:", new_file.filename, "in database.")

    wb = load_workbook(new_file, read_only = True)
    statSheet = wb.get_sheet_by_name("Estatística")
    regSheet = wb.get_sheet_by_name("Folha de Registo")

    iso_date = format_date(regSheet['C6'].value)
    gate = regSheet['A4'].value.rsplit(' ',1)[-1].capitalize()
    if gate not in ["Ameias","Serpa","Rainha"]:
        #TODO: error views
        print("could not find gate!")

    #get list of payed entrances
    payer_upper_bound="Dados visitantes veículos pagantes"
    payer_lower_bound="Dados visitantes veículos não pagantes (hóspedes, reuniões, outros)"
    payer_interval = find_row_interval(statSheet,payer_upper_bound,
                                       payer_lower_bound)

    payed_entraces = create_entrance_list(statSheet,payer_interval)

    print (payer_interval)
    print (len(payed_entraces))
    for entry in payed_entraces:
        print(entry)
    return

#returns a list of entrances
def create_entrance_list(sheet,interval):
    entrance_list = []

    for row in sheet.iter_rows(min_row=interval[0]+2,
                               max_row=interval[1]-1,
                               max_col=19):
        if row[0].value:
            entrance_type = row[0].value
            if row[6].value: n_persons = row[6].value
            else: n_persons = 0

            if row[12].value: country = row[12].value
            else: country = ""

            if row[18].value: municipality = row[18].value
            else: municipality = ""

            entrance_list.append([entrance_type,n_persons,
                                  country,municipality])

    return entrance_list

#returns the row interval between lower_delimiter and upper_delimiter
def find_row_interval(sheet,lower_delimiter, upper_delimiter):
    lower_bound = 0
    upper_bound = 0

    for row in sheet.iter_rows(max_col=1):
        for cell in row:
            if cell.value == lower_delimiter:
                lower_bound = cell.row
            if cell.value == upper_delimiter:
                upper_bound = cell.row

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
