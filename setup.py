from setuptools import setup

setup(
    name='statFMB',
    version='0.1',
    author='Pedro Coelho',
    url='https://github.com/maia-dev/statFMB',
    description='A portal to Fundação Mata do Buçaco',
    license='GPL3',
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
        'weasyprint',
    ],
)
