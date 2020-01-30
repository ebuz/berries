.PHONY: get_data_sources

get_data_sources:
	mkdir -p ./data/gis_data
	curl ftp://prism.nacse.org/normals_800m/tmax/PRISM_tmax_30yr_normal_800mM2_annual_bil.zip -o ./data/gis_data/annual_tmax.zip
	curl ftp://prism.nacse.org/normals_800m/tmin/PRISM_tmin_30yr_normal_800mM2_annual_bil.zip -o ./data/gis_data/annual_tmin.zip
	curl ftp://prism.nacse.org/normals_800m/ppt/PRISM_ppt_30yr_normal_800mM2_annual_bil.zip -o ./data/gis_data/annual_ppt.zip
	curl http://prism.nacse.org/projects/public/phm/phm_us_grid.zip -o ./data/gis_data/phm_us_grid.zip
	curl https://s3-us-west-2.amazonaws.com/mrlc/NLCD_2016_Land_Cover_L48_20190424.zip -o ./data/gis_data/landcover.zip
	curl https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_nation_5m.zip -o ./data/gis_data/us_border.zip
	curl http://download.massgis.digital.mass.gov/shapefiles/state/openspace.zip -o ./data/gis_data/mass_openspace.zip
