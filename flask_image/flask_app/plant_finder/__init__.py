from flask import Flask
from flask_googlemaps import GoogleMaps
import os

app = Flask(__name__, template_folder="./templates")

GoogleMaps(app, key=os.environ['GOOGLE_MAPS_API_KEY'])

from plant_finder import views
