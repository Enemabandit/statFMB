import getpass
import re

from statFMB.views import app, socketio, create_tables, user_datastore, db

#NOTE: change the comments in order change hosts
def main():
    socketio.run(app)
    #socketio.run(app, host='0.0.0.0', port='80')

def create_db():
    print('A inicializar tabelas!')
    create_tables()
    create_admin_user()
    print('Base de dados criada')

def create_admin_user():
    print('Criar conta de Administrador')
    role = 'Administrador'
    create_user(role)
    print('Utilizador Criado!')


def create_user(role = None):
    email = input('  email: ')
    while not re.match(r'[^@]+@[^@]+\.[^@]+',email) or len(email) > 80:
        print('Email invalido!')
        email = input('  email: ')

    password = getpass.getpass('  password: ')
    while len(password) > 80:
        print('Password demasiado longa! (max.80)')
        password = getpass.getpass('  password: ')

    name = input('  nome: ')
    while len(name) > 100:
        print('Nome demasiado longo! (max.100)')
        name = input('  nome: ')

    phone = input('  telefone: ')
    while len(phone) != 9 or not phone.isdigit():
        print('Numero de telefone invalido!')
        phone = input('  telefone: ')

    alias = input('  alias: ')
    while len(alias) > 3 or len(alias) == 0:
        print('Alias errado!')
        alias = input('  alias: ')

    if role == None:
        role = input('  role (Administrador, Portageiro, Visualizador):')
        while role not in ['Administrador', 'Portageiro', 'Visualizador']:
            print('Role invalida!')
            role = input('  role (Administrador, Portageiro, Visualizador):')

    user_datastore.create_user(email = email,
                               password = password,
                               name = name,
                               phone = phone,
                               alias = alias,
    )
    user_datastore.add_role_to_user(email,role)
    db.session.commit()

if __name__ == "__main__":
    socketio.run(app)
    #socketio.run(app, host='0.0.0.0', port='80')
