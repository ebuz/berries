from plant_finder.plant_modeler.data import plant_options, plant_data, plant_characteristics, mass_openspace_stats, landcovers
from plant_finder.plant_modeler.models import fitted_models, features

def predict_plant_locations(plants = ['VACO']):
    for symbol in plants:
        if f'{symbol}_svm_score' not in mass_openspace_stats:
            X = mass_openspace_stats[[f + '_mean' for f in features[:4]] + features[4:]]
            mass_openspace_stats[f'{symbol}_svm_score'] = fitted_models[symbol].decision_function(X.values)
    return mass_openspace_stats


