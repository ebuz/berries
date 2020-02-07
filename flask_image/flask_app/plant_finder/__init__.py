from flask import Flask
from flask_googlemaps import GoogleMaps
import os
import sys

app = Flask(__name__, template_folder="./templates")

GoogleMaps(app, key=os.environ['GOOGLE_MAPS_API_KEY'])

try:
    from plant_finder import views
except Exception as e:
    sys.stderr.write(f'failed to import views: {e}')
    sys.stderr.flush()
    raise e
