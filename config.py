DEBUG = True

SECRET_KEY = 'DontTellAnyone'

SQLALCHEMY_DATABASE_URI = 'mysql://statFMB:statFMB@localhost/test'

### this was added to solve a deprecation warning
SQLALCHEMY_TRACK_MODIFICATIONS = False
