from plant_finder.plant_modeler.data import plant_options, plant_data, landcovers
import numpy as np
from sklearn import svm
from sklearn.model_selection import GridSearchCV
import pickle
import os.path

features = ['ppt', 'hardiness', 'tmin', 'tmax', 'latitude', 'longitude'] + ['histo_' + l for l in landcovers]

if os.path.isfile('model_cache.pickle'):
    with open('model_cache.pickle', 'rb') as infile:
        fitting_dict = pickle.load(infile)
else:
    fitting_dict = {}
    for plant, symbol in plant_options.items():
        print(f'{symbol}:{plant}')
        species_data = plant_data.loc[plant_data.accepted_symbol == symbol]
        X = species_data[features]
        n_features = len(features)
        search_params = {'kernel': ('linear', 'sigmoid', 'rbf'),
                         'gamma': np.linspace(1 / (n_features * X.values.var()), 1/n_features, num=10),
                         'nu': [1/(1+len(species_data)) ]
                         }
        ocsvm = svm.OneClassSVM()
        clf = GridSearchCV(ocsvm, search_params, 'accuracy')
        clf.fit(X.values, np.ones(len(X)))
        fitting_dict[symbol] = clf
    with open('model_cache.pickle', 'wb') as outfile:
        pickle.dump(fitting_dict, outfile, pickle.HIGHEST_PROTOCOL)

fitted_models = fitting_dict
