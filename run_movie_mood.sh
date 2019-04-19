#!/bin/bash

echo "setting up environment..."

DIRECTORY=$(cd `dirname $0` && pwd)

source ~/.profile
workon py3cv4

echo "running movie mood script..."

python movie_mood.py --input "http://192.168.0.30:8080/?action=stream;dummy=param.mjpg" --crop "45 325 230 125" --light "Lounge Ceiling Light,Hallway Ceiling Light"
