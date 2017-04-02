DEBUG = True

SQLALCHEMY_DATABASE_URI = 'mysql://statFMB:statFMB@localhost/test'

### this was added to solve a deprecation warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'DontTellAnyone'
