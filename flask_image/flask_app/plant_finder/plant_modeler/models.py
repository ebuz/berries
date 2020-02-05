from plant_finder.plant_modeler.data import plant_options, plant_data, landcovers, mass_openspace_stats
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import pickle
import os.path

features = ['ppt', 'hardiness', 'tmin', 'tmax', 'latitude', 'longitude'] + ['histo_' + l for l in landcovers]


def pipeline_fit(species_data, nu=.2):
    X_train, X_test, y_train, y_test = train_test_split(species_data, np.ones(len(species_data)), test_size=0.2)
    n_features = X_train.shape[1]
    # scale the numeric features (the categorical landtype features are already encoded)
    column_trans = ColumnTransformer(
        [('scaled', StandardScaler(), [0, 1, 2, 3, 4, 5])],
        remainder='passthrough')
    # pipeline taking transformer and classifier, declare nu and set max_iter as otherwise some species do not fit
    clf = Pipeline(steps=[('preprocessor', column_trans),
                          ('classifier', svm.OneClassSVM(nu=nu, max_iter=10**7))])
    # Setup search grid
    search_params = {'classifier__kernel': ('linear', 'sigmoid', 'rbf'),
                     'classifier__gamma': np.linspace(1 / (n_features * X_train.var()), .5, num=10)
                     }
    grid_search = GridSearchCV(clf, search_params, 'accuracy', n_jobs=-2)
    grid_search.fit(X_train, y_train)
    # return best fit, predictions on test and distance from hyperplane
    return grid_search, grid_search.predict(X_test), grid_search.decision_function(X_test)


def gridsearch_fit(nu=.2):
    #results to save and return
    fits_dict = {}
    prediction_dict = {}
    distance_dict = {}
    #split grid search by species
    for plant, symbol in plant_options.items():
        print(f'{symbol}:{plant}')
        species_data = plant_data[plant_data.accepted_symbol == symbol]
        X = species_data[features]
        # fit to species
        cvfit, test_predict, test_dist = pipeline_fit(X.values, nu)
        fits_dict[symbol] = cvfit
        # calculate accuracy on test set
        prediction_dict[symbol] = (test_predict == 1).mean()
        # calculate average distance from hyperplane of test set
        distance_dict[symbol] = test_dist.mean()
    return fits_dict, prediction_dict, distance_dict


def park_metrics(fits, symbol, metric='predict'):
    X = mass_openspace_stats[[f + '_mean' for f in features[:4]] + features[4:]]
    if metric == 'predict':
        return fits[symbol].predict(X.values)
    elif metric == 'decision':
        return fits[symbol].decision_function(X.values)
    return None


park_predictions = pd.DataFrame(columns=('plant', 'ogc_fid', 'site_name',
                                         'latitude', 'longitude', 'prediction', 'distance', 'nu'))
# fitted model cache
fitted_models_by_nu = {}

if os.path.isfile('model_cache.pickle'):
    with open('model_cache.pickle', 'rb') as infile:
        fitted_models_by_nu = pickle.load(infile)
else:
    nu_search_space = np.linspace(0.2, 0.25, num=5)
    for nu in nu_search_space:
        fits, _, _ = gridsearch_fit(nu)
        # save fits by nu
        fitted_models_by_nu[nu] = fits
    with open('model_cache.pickle', 'wb') as outfile:
        pickle.dump(fitted_models_by_nu, outfile, pickle.HIGHEST_PROTOCOL)

if os.path.isfile('park_cache.pickle'):
    with open('park_cache.pickle', 'rb') as infile:
        park_predictions = pickle.load(infile)
else:
    for nu, fits in fitted_models_by_nu.items():
        for c, s in plant_options.items():
            park_results = mass_openspace_stats[['ogc_fid', 'site_name', 'latitude', 'longitude']].assign(
                prediction=(park_metrics(fits, s, 'predict') == 1),
                distance=park_metrics(fits, s, 'decision'),
                plant=s, nu=nu)
            park_predictions = pd.concat([park_predictions, park_results], ignore_index=True, sort=False)
    park_predictions = park_predictions[park_predictions.prediction == True].reset_index()
    with open('park_cache.pickle', 'wb') as outfile:
        pickle.dump(park_predictions, outfile, pickle.HIGHEST_PROTOCOL)

# returning models at a specific nu to avoid breaking view code
fitted_models = fitted_models_by_nu[.2]
