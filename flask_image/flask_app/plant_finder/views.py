from plant_finder import app, plant_modeler
from flask_googlemaps import Map
from flask import render_template, request

season_key = {'Spring':'🌱', 'Summer':'🌞', 'Fall':'🍂', 'Winter':'❄️'}
def harvest_strings(l):
    if l[0] == l[1]:
        return season_key[l[0]]
    return ' ~ '.join(season_key[i] for i in l)

harvest_strings_dict = {sym: harvest_strings(sea[1:]) for sym, sea in plant_modeler.plant_characteristics.set_index('accepted_symbol').T.to_dict('list').items()}
wiki_slugs = {sym: plant.replace(' ', '_') for plant, sym in plant_modeler.plant_options.items()}

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index', methods = ['POST', 'GET'])
def map():
    selected_plants = []
    markers = []
    if request.method == 'POST' and len(request.form.getlist('plants')) > 0:
        selected_plants = request.form.getlist('plants')
        results = plant_modeler.predict_plant_locations(selected_plants)
        for plant in selected_plants:
            results.sort_values(by=f'{plant}_svm_score', ascending = False)
            top_ten = results[:10]
            markers.extend(list(zip(top_ten.latitude, top_ten.longitude)))
    mymap = Map(
        zoom=10,
        style='height:100%;width:100%;margin:0;',
        identifier="view-side",
        lat=42.387265,
        lng=-72.038140,
        fit_markers_to_bounds=True if len(markers) > 0 else False,
        markers=markers
    )
    return render_template('map.html',
                           plant_options=plant_modeler.plant_options,
                           harvest_strings_dict=harvest_strings_dict,
                           selected_plants=selected_plants, mymap=mymap,
                           wiki_slugs=wiki_slugs)
