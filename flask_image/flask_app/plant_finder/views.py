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
def main_map():
    selected_plants = []
    markers = []
    no_results = False
    if request.method == 'POST' and len(request.form.getlist('plants')) > 0:
        selected_plants = request.form.getlist('plants')
        print(f'got plant requests {selected_plants}')
        for plant in selected_plants:
            print(f'finding park predictions for {plant}')
            park_predictions = plant_modeler.models.park_predictions[plant_modeler.models.park_predictions.plant == plant]
            park_predictions = park_predictions[park_predictions.nu == 0.2]
            park_predictions = park_predictions.sort_values(by='distance', ascending=False)
            top_ten = park_predictions[:10]
            print(f'{top_ten}')
            markers.extend(list(zip(top_ten.latitude, top_ten.longitude)))
        if len(markers) < 1:
            no_results = True
    mymap = Map(
        zoom=10,
        style='height:100%;width:100%;margin:0;',
        identifier="view-side",
        lat=42.387265,
        lng=-71.538140,
        fit_markers_to_bounds=True if len(markers) > 0 else False,
        markers=markers
    )
    return render_template('map.html',
                           plant_options=plant_modeler.plant_options,
                           harvest_strings_dict=harvest_strings_dict,
                           selected_plants=selected_plants,
                           no_results=no_results, mymap=mymap, wiki_slugs=wiki_slugs)
