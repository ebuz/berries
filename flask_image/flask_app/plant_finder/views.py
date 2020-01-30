from plant_finder import app, plant_modeler
from flask_googlemaps import Map
from flask import render_template, request

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def map():
    plant_options = plant_modeler.plant_options.keys()
    selected_plants = []
    markers = []
    if request.method == 'POST':
        selected_plants = request.form.getlist('plants')
        results = plant_modeler.predict_plant_locations([plant_modeler.plant_options[p] for p in selected_plants])
        for plant in selected_plants:
            results.sort_values(by=f'{plant_modeler.plant_options[plant]}_svm_score', ascending = False)
            top_ten = results[:10]
            markers.extend(list(zip(top_ten.latitude, top_ten.longitude)))
    mymap = Map(
        identifier="view-side",
        lat=42.387265,
        lng=-72.038140,
        fit_markers_to_bounds=True if len(markers) > 0 else False,
        markers=markers
    )
    return render_template('map.html',
            plant_options=plant_options, selected_plants=selected_plants,
            mymap=mymap, plant_data=None)
