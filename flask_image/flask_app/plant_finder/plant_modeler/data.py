from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import OneHotEncoder
import os

engine = create_engine(f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOST"]}:5432/plants')

landcover_mapping = {'11': 'water', '12': 'perennial ice/snow', '21': 'developed open', '22': 'developed low intensity',
                     '23': 'developed med intensity', '24': 'developed high intensity', '31': 'barren land',
                     '41': 'deciduous forest', '42': 'evergreen forest', '43': 'mixed forest', '51': 'dwarf scrub',
                     '52': 'shrub/scrub', '71': 'grassland', '72': 'sedge', '73': 'lichens', '74': 'moss',
                     '81': 'pasture', '82': 'cropland', '90': 'woody wetlands', '95': 'emergent herbaceous wetlands'}


plant_data = gpd.GeoDataFrame.from_postgis("select accepted_symbol, scientific_name, latitude, longitude, location, "
                                           "landcover, tmin, tmax, ppt, hardiness from ediblestats "
                                           "where tmax is not NULL;",
                                           con=engine, geom_col='location')

fruiting_plants = pd.read_sql_query("select accepted_symbol, scientific_name, common_name "
                                    "from fruiting_plants where common_name is not NULL;",
                                    con=engine)

plant_characteristics = pd.read_sql_query("select distinct accepted_symbol, bloom_period, fruit_period_begin, "
                                          "fruit_period_end from plant_characteristics;",
                                          con=engine)

mass_observed_edibles = pd.read_sql_query("select accepted_symbol from mass_observed_edibles;",
                                          con=engine)

#subset data to fruiting plants
plant_data = plant_data[plant_data.accepted_symbol.isin(fruiting_plants.accepted_symbol)]

# cast landcover to int -> str and remove unknown value
plant_data.landcover = plant_data.landcover.astype('int32').astype('str')
plant_data = plant_data[plant_data.landcover != '0']

# tabulate count data and subset species with few observations
# subset to ensure 20 points per (expected) feature
plant_counts = plant_data[['accepted_symbol', 'tmax']].groupby(['accepted_symbol']).agg(['count'])
frequency_subset = plant_counts[plant_counts.tmax['count'] > 22*20].index
plant_data = plant_data[plant_data.accepted_symbol.isin(frequency_subset)]

# subset fruit lists to available data
fruiting_plants = fruiting_plants[fruiting_plants.accepted_symbol.isin(plant_data.accepted_symbol)]
plant_characteristics = plant_characteristics[plant_characteristics.accepted_symbol.isin(fruiting_plants.accepted_symbol)]

# load parks data
mass_openspace_stats = gpd.GeoDataFrame.from_postgis("select *, ST_X(ST_Centroid(geom)) as longitude, "
                                                     "ST_Y(ST_Centroid(geom)) as latitude from mass_openspace_stats;",
                                                     con=engine, geom_col='geom')

# re-encode parkland to one-hot encoding
# grab parkland types
park_landcovers = [ty[6:] for ty in filter(lambda x: 'histo' in x, list(mass_openspace_stats))]
landcovers = sorted(list(set(park_landcovers + list(plant_data.landcover.unique()))))

# normalized park encoding of landcover
# parks are missing '12' type landcover
mass_openspace_stats.insert(mass_openspace_stats.columns.get_loc('histo_11'), 'histo_12', 0)
row_norms = np.linalg.norm(mass_openspace_stats[['histo_' + l for l in landcovers]], axis = 1)
normalized_rows = mass_openspace_stats[['histo_' + l for l in landcovers]].values / row_norms[:,None]
mass_openspace_stats[['histo_' + l for l in landcovers]] = normalized_rows

# hot encode plant data and set columns to match mass park data
landcover_encoder = OneHotEncoder(handle_unknown='error')
landcover_encoder.fit(np.array(landcovers, str).reshape(-1, 1))
landcover_encoded = landcover_encoder.transform(plant_data.landcover.values.reshape(-1, 1))
lc_pd = pd.DataFrame(data = landcover_encoded.todense(), columns = ['histo_' + l for l in landcovers])
plant_data = pd.concat([plant_data.reset_index(drop=True), lc_pd], axis=1)

# build species option list for front end
plant_options = dict(zip(fruiting_plants.common_name, fruiting_plants.accepted_symbol))
