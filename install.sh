#!/bin/bash
pip3 install -r requirements.txt
export FLASK_APP=v2rayClient.py
flask run
