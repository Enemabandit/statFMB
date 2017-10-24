from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='statFMB',
    version='0.1',
    author='Pedro Coelho',
    author_email='maia.coelho.dev@gmail.com',
    url='https://github.com/maia-dev/statFMB',
    description='A portal to Fundação Mata do Buçaco',
    long_description=readme(),
    license='GPLv3+',
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
        'flask-weasyprint',
        'weasyprint',
        'bcrypt',
    ],
    entry_points={
        'console_scripts': ['statFMB=statFMB.run:main'],
    }
)
