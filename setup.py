from setuptools import setup

setup(
    name='statFMB',
    packages=['statFMB'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-security',
        'flask-sqlalchemy',
        'openpyxl',
        'xlrd',
        'eventlet',
        'flask-socketio',
    ],
)
