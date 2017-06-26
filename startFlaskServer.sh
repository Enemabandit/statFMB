#!/bin/bash

. venv/bin/activate
export FLASK_APP=statFMB
export FLASK_DEBUG=1

flask run
