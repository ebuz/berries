from plant_finder.plant_modeler.data import plant_options, plant_data, landcovers, mass_openspace_stats
import numpy as np
import pandas as pd
from joblib import parallel_backend
from sklearn import svm
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import pickle
import os.path

features = ['ppt', 'hardiness', 'tmin', 'tmax', 'latitude', 'longitude'] + ['histo_' + l for l in landcovers]


def pipeline_cvfit(species_data, nu=.2, model='svm'):
    # do a split to gather testing data
    X_train, X_test, y_train, y_test = train_test_split(species_data, np.ones(len(species_data)), test_size=0.2)
    n_features = X_train.shape[1]
    # scale the numeric features (the categorical landtype features should already be one-hot encoded)
    column_trans = ColumnTransformer(
        [('scaled', StandardScaler(), [0, 1, 2, 3, 4, 5])],
        remainder='passthrough')
    if model == 'svm':
        # set nu value and put cap on iteration to avoid fitting forever
        classifier = svm.OneClassSVM(nu=nu, shrinking=True, max_iter=10**7)
        # set up grid search
        search_params = [
            {'classifier__kernel': ['linear']
             },
            {'classifier__kernel': ['poly'],
             'classifier__gamma': np.linspace(1 / (n_features * X_train.var()), .5, num=10),
             'classifier__degree': [2, 3, 4],
             },
            {'classifier__kernel': ['rbf'],
             'classifier__gamma': np.linspace(1 / (n_features * X_train.var()), .5, num=10),
             }
        ]
    elif model == 'isolationforest':
        # set contamination to nu value and set random_state for reproducible results
        classifier = IsolationForest(contamination=nu, random_state=10)
        search_params = {'classifier__n_estimators': list(range(100, 400, 30)),
                         'classifier__max_samples': list(range(100, 200, 10)),
                         'classifier__max_features': [5, 10, 15],
                         'classifier__bootstrap': [True, False]}
    elif model == 'localoutlierfactor':
        # set contamination to nu value and set novelty to true to allow predictions on unseen data
        classifier = LocalOutlierFactor(contamination=nu, novelty=True)
        search_params = [
            {'classifier__n_neighbors': list(range(10, 40, 5)),
             'classifier__algorithm': ['ball_tree', 'kd_tree'],
             'classifier__leaf_size': list(range(15, 60, 5)),
             'classifier__p': [1, 2]},
            {'classifier__n_neighbors': list(range(10, 40, 5)),
             'classifier__algorithm': ['brute'],
             'classifier__p': [1, 2]},
        ]
    else:
        raise Exception
    clf = Pipeline(steps=[('preprocessor', column_trans),
                          ('classifier', classifier)])
    with parallel_backend('threading', n_jobs=-2):
        grid_search = GridSearchCV(clf, search_params, 'recall')
        grid_search.fit(X_train, y_train)
    # return best fit, predictions on test and distance from hyperplane
    return grid_search, grid_search.predict(X_test), grid_search.decision_function(X_test)


def gridsearch_fit(nu=.2, model='svm'):
    #results to save and return
    fits_dict = {}
    prediction_dict = {}
    distance_dict = {}
    #split grid search by species
    for plant, symbol in plant_options.items():
        print(f'{symbol}:{plant}:{model}:{nu}')
        species_data = plant_data[plant_data.accepted_symbol == symbol]
        X = species_data[features]
        # fit to species
        cvfit, test_predict, test_dist = pipeline_cvfit(X.values, nu, model)
        fits_dict[symbol] = cvfit
        # calculate accuracy on test set
        prediction_dict[symbol] = (test_predict == 1).mean()
        # calculate average distance from hyperplane of test set
        distance_dict[symbol] = test_dist.mean()
    return fits_dict, prediction_dict, distance_dict


def park_metrics(fits, symbol, metric='predict'):
    X = mass_openspace_stats[[f + '_mean' for f in features[:4]] + features[4:]]
    result = None
    with parallel_backend('threading', n_jobs=-2):
        if metric == 'predict':
            result = fits[symbol].predict(X.values)
        elif metric == 'decision':
            result = fits[symbol].decision_function(X.values)
    return result


nu_search_space = list(np.linspace(0.1, 0.25, num=5))
model_types = ['isolationforest']
fitted_models = {}

for model in model_types:
    if os.path.isfile(f'{model}_model_cache.pickle'):
        with open(f'{model}_model_cache.pickle', 'rb') as infile:
            fitted_models[model] = pickle.load(infile)
    else:
        test_results_by_nu = {}
        for nu in nu_search_space:
            fits, test_predictions, _ = gridsearch_fit(nu,  model=model)
            # save fits by nu
            fitted_models[model][nu] = fits
            test_results_by_nu[nu] = test_predictions
        with open(f'{model}_model_cache.pickle', 'wb') as outfile:
            pickle.dump(fitted_models[model], outfile, pickle.HIGHEST_PROTOCOL)
        with open(f'{model}_test_results.pickle', 'wb') as outfile:
            pickle.dump(test_results_by_nu, outfile, pickle.HIGHEST_PROTOCOL)

model_park_predictions = {}

for model in model_types:
    if os.path.isfile(f'{model}_park_cache.pickle'):
        with open(f'{model}_park_cache.pickle', 'rb') as infile:
            model_park_predictions[model] = pickle.load(infile)
    else:
        park_predictions = pd.DataFrame(columns=('ogc_fid', 'site_name',
                                                 'latitude', 'longitude', 'prediction', 'distance',
                                                 'plant', 'nu', 'model'))
        for nu, fits in fitted_models[model].items():
            for c, s in plant_options.items():
                p_r = mass_openspace_stats[['ogc_fid', 'site_name', 'latitude', 'longitude']].assign(
                    prediction=(park_metrics(fits, s, 'predict') == 1),
                    distance=park_metrics(fits, s, 'decision'),
                    plant=s, nu=nu, model=model)
                park_predictions = pd.concat([park_predictions, p_r], ignore_index=True, sort=False)
        # park_predictions = park_predictions[park_predictions.prediction == True]
        model_park_predictions[model] = park_predictions
        with open(f'{model}_park_cache.pickle', 'wb') as outfile:
            pickle.dump(park_predictions, outfile, pickle.HIGHEST_PROTOCOL)

# select model to use for frontend
park_predictions = model_park_predictions['isolationforest']
park_predictions = park_predictions[park_predictions.nu == 0.1].reset_index()
