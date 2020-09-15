import sys, os, yaml
import argparse
import pandas as pd
from sklearn import preprocessing


def load_yaml(path_to_file):
  stream = open(path_to_file, 'r')
  yaml_doc = yaml.load(stream, Loader=yaml.BaseLoader)
  return yaml_doc

def find_or_create_parent(yaml_doc, search_string):
  yaml_component = yaml_doc
  for path_component in search_string.split(".")[:-1]:
    if path_component in yaml_component:
      if type(yaml_component[path_component]) is dict:
        yaml_component = yaml_component[path_component]
      else:
        sys.exit("Error: Component {0} of {1} exists but is not an object".format(
          path_component, search_string
        ))
    else:
      yaml_component[path_component] = dict()
      yaml_component = yaml_component[path_component]
  return yaml_component


def current_value(yaml_doc, seach_string):
  parent = find_or_create_parent(yaml_doc, search_string)
  if search_string.split(".")[-1] in parent:
    return parent[search_string.split(".")[-1]]
  else:
    return None


def set_value(yaml_doc, search_string, value):
  parent = find_or_create_parent(yaml_doc, search_string)
  parent[search_string.split(".")[-1]] = value


def dump(yaml_doc):
  return yaml.dump(yaml_doc, default_flow_style=False, allow_unicode=True, encoding="utf-8")


def change_year(path_to_file, search_string, path_out, year):
  yaml_doc = load_yaml(path_to_file)
  set_value(yaml_doc, search_string, str(year))
  output_file = open(path_out, "wb")
  output_file.write(dump(yaml_doc=yaml_doc))


def load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2015):

    # selecting spreadsheet
    filename = os.path.join(
        os.path.expanduser("~"), path_to_data, '2019-04-04_Agorameter_v8.1.xlsx')

    data = pd.read_excel(filename, sheet_name=str(year), header=6)
    data.drop(labels=['Year','Month','Day','Hour'], axis=1, inplace=True)
    data.set_index("Date/Time", inplace=True)

    # taking into account exports for generation
    load = data["Consumption"]
    exportsaldo = data["Exportsaldo"]
    demand_eff = load+exportsaldo
    p_spot_agora = data["Day-Ahead Spot"]
    em_factor_agora = data["Emission factor g/kWh"]

    if year < 2015:
        gen_technologies=['Biomass', 'Hydro', 'Wind', 'PV', 'Nuclear', 'Lignite', 'Hard Coal', 'Natural Gas', 'Pump', 'Others']
    else:
        gen_technologies=['Biomass', 'Hydro', 'Wind onshore', 'PV', 'Nuclear', 'Lignite', 'Hard Coal', 'Natural Gas', 'Pump', 'Others']

    generation = data[gen_technologies]

    return load, generation, p_spot_agora, em_factor_agora


def plt_jdl(input):
    series = input.sort_values(ascending=False)
    series = series.reset_index()
    plt_jdl = series.iloc[:, 1]

    return plt_jdl


def normalize_timeseries(input):
    x = input.reshape(-1, 1)
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    x_norm = pd.DataFrame(x_scaled)

    return x_norm

def calculate_PV_sites(region, invert=True, separation=1000, name='NoRegion', convert2epsg=True):
    # Choose Region
    ecPV = gl.ExclusionCalculator(region, srs=3035, pixelSize=100, limitOne=False)

    # Apply selected exclusion criteria
    ecPV.excludePrior(pr.settlement_proximity, value=None)
    ecPV.excludePrior(pr.settlement_urban_proximity, value=None)
    ecPV.excludePrior(pr.industrial_proximity, value=None)

    # Placement Algorithm
    ecPV.distributeItems(separation=separation, invert=invert, outputSRS=4326)

    # Extract and convert site coords of turbines
    site_coords = pd.DataFrame(ecPV.itemCoords)
    site_coords.columns = ['latitude', 'longitude']
    site_coords_gdf = geom.create_geo_df(site_coords, wkt_column=None, lon_column="longitude",
                                         lat_column='latitude')

    # Convert2epsg for plotting purposes
    if convert2epsg == True:
        trsf = site_coords_gdf["geometry"]
        site_coords_gdf_epsg3857 = trsf.to_crs(epsg=3857)

        # Save coords in EPSG3587 to hard disk
        site_coords_gdf_epsg3857.to_file("site_coordsPV_epsg3857_" + name + ".geojson", driver='GeoJSON')
        site_coords_gdf.to_file("site_coordsPV_WGS84_" + name + ".geojson", driver='GeoJSON')
    elif convert2epsg == False:
        site_coords_gdf.to_file("site_coordsPV_WGS84_" + name + ".geojson", driver='GeoJSON')

    # Calculate Power per Site in MW
    p_mean = 300000 / len(site_coords)  # Total possible PV-Power in MW divided by site count

    # Write turbines to power plants df
    res_df_PV = pd.DataFrame(columns=["energy_source_level_1", "energy_source_level_2", "technology",
                                      "electrical_capacity", "lon", "lat", "data_source"])

    res_df_PV["lon"] = site_coords["latitude"]
    res_df_PV["lat"] = site_coords["longitude"]
    res_df_PV["energy_source_level_1"] = 'Renewable energy'
    res_df_PV["energy_source_level_2"] = 'Solar'
    res_df_PV["technology"] = 'Photovoltaics'
    res_df_PV["electrical_capacity"] = p_mean
    res_df_PV["data_source"] = 'GLAES'

    return res_df_PV, ecPV

def calculate_wind_sites(region, invert=False, separation=700, name='NoRegion', convert2epsg=False, asArea=False):
    # Choose Region
    ecWind = gl.ExclusionCalculator(region, srs=3035, pixelSize=100, limitOne=False)

    # Define Exclusion Criteria
    selExlWind = {
        "access_distance": (5000, None),
        # "agriculture_proximity": (None, 50 ),
        # "agriculture_arable_proximity": (None, 50 ),
        # "agriculture_pasture_proximity": (None, 50 ),
        # "agriculture_permanent_crop_proximity": (None, 50 ),
        # "agriculture_heterogeneous_proximity": (None, 50 ),
        "airfield_proximity": (None, 1760),  # Diss WB
        "airport_proximity": (None, 5000),  # Diss WB
        "connection_distance": (10000, None),
        # "dni_threshold": (None, 3.0 ),
        "elevation_threshold": (1500, None),
        # "ghi_threshold": (None, 3.0 ),
        "industrial_proximity": (None, 250),  # Diss Wingenbach / UBA 2013
        "lake_proximity": (None, 0),
        "mining_proximity": (None, 100),
        "ocean_proximity": (None, 10),
        "power_line_proximity": (None, 120),  # Diss WB
        "protected_biosphere_proximity": (None, 5),  # UBA 2013
        "protected_bird_proximity": (None, 200),  # UBA 2013
        "protected_habitat_proximity": (None, 5),  # UBA 2013
        "protected_landscape_proximity": (None, 5),  # UBA 2013
        "protected_natural_monument_proximity": (None, 200),  # UBA 2013
        "protected_park_proximity": (None, 5),  # UBA 2013
        "protected_reserve_proximity": (None, 200),  # UBA 2013
        "protected_wilderness_proximity": (None, 200),  # UBA 2013
        "camping_proximity": (None, 900),  # UBA 2013)
        # "touristic_proximity": (None, 800),
        # "leisure_proximity": (None, 1000),
        "railway_proximity": (None, 250),  # Diss WB
        "river_proximity": (None, 5),  # Abweichung vom standardwert (200)
        "roads_proximity": (None, 80),  # Diss WB
        "roads_main_proximity": (None, 80),  # Diss WB
        "roads_secondary_proximity": (None, 80),  # Diss WB
        # "sand_proximity": (None, 5 ),
        "settlement_proximity": (None, 600),  # Diss WB
        "settlement_urban_proximity": (None, 1000),
        "slope_threshold": (10, None),
        # "slope_north_facing_threshold": (3, None ),
        "wetland_proximity": (None, 5),  # Diss WB / UBA 2013
        "waterbody_proximity": (None, 5),  # Diss WB / UBA 2013
        "windspeed_100m_threshold": (None, 4.5),
        "windspeed_50m_threshold": (None, 4.5),
        "woodland_proximity": (None, 0),  # Abweichung vom standardwert (300) / Diss WB
        "woodland_coniferous_proximity": (None, 0),  # Abweichung vom standardwert (300)
        "woodland_deciduous_proximity": (None, 0),  # Abweichung vom standardwert (300)
        "woodland_mixed_proximity": (None, 0)  # Abweichung vom standardwert (300)
    }

    # Apply selected exclusion criteria
    # for key in selExlWind:
    #     ecWind.excludePrior(pr[key], value=ecWind.typicalExclusions[key])

    for key in selExlWind.keys():
        ecWind.excludePrior(key, value=selExlWind[key])

    # Placement Algorithm
    ecWind.distributeItems(separation=separation, outputSRS=4326, asArea=asArea)

    # Extract and convert site coords of turbines
    site_coords = pd.DataFrame(ecWind.itemCoords)
    site_coords.columns = ['latitude', 'longitude']
    site_coords_gdf = geom.create_geo_df(site_coords, wkt_column=None, lon_column="longitude",
                                         lat_column='latitude')

    # Convert2epsg for plotting purposes
    if convert2epsg == True:
        trsf = site_coords_gdf["geometry"]
        site_coords_gdf_epsg3857 = trsf.to_crs(epsg=3857)

        # Save coords in EPSG3587 to hard disk
        site_coords_gdf_epsg3857.to_file("site_coordsWind_epsg3857_" + name + ".geojson", driver='GeoJSON')
        site_coords_gdf.to_file("site_coordsWind_WGS84_" + name + ".geojson", driver='GeoJSON')

    elif convert2epsg == False:
        site_coords_gdf.to_file("site_coordsWind_WGS84_" + name + ".geojson", driver='GeoJSON')

    # Write turbines to power plants df
    res_df_Wind = pd.DataFrame(columns=["energy_source_level_1", "energy_source_level_2", "technology",
                                        "electrical_capacity", "lon", "lat", "data_source"])

    res_df_Wind["lon"] = site_coords["latitude"]
    res_df_Wind["lat"] = site_coords["longitude"]
    res_df_Wind["energy_source_level_1"] = 'Renewable energy'
    res_df_Wind["energy_source_level_2"] = 'Wind'
    res_df_Wind["technology"] = 'Onshore'
    res_df_Wind["electrical_capacity"] = 3.5
    res_df_Wind["data_source"] = 'GLAES'

    return res_df_Wind, ecWind


def get_hp_shares():
    # Diese Funktion macht vermutlich überhaupt keinen Sinn
    qdem, age_structure = spatial.disagg_households_heatload_DB(how='bottom-up', weight_by_income=True)
    share_hp = pd.DataFrame(index=age_structure.index, columns=['share_hp35', 'share_hp55','share_hp75'])

    for idx in share_hp.index:
        share_hp.loc[idx]['share_hp35'] = age_structure.loc[idx]['F_>2000'] / age_structure.loc[idx].sum()
        share_hp.loc[idx]['share_hp55'] = (age_structure.loc[idx]['E_1996-2000'] +
                                           age_structure.loc[idx]['D_1986-1995']) / age_structure.loc[idx].sum()
        share_hp.loc[idx]['share_hp75'] = age_structure.loc[idx]['A_<1948'] / age_structure.loc[idx].sum()

    return share_hp


def load_and_compare_charging_of_fleets():
    # Read files, cut off initial charging and normalize between 0 and 1
    p500 = pd.read_csv('P_500ev.csv', index_col='Unnamed: 0')
    p500.iloc[0:48] = p500.iloc[48:96].values
    p500_immediate = normalize_timeseries(p500['immediate'].values)
    p500_balanced = normalize_timeseries(p500['balanced'].values)

    p1000 = pd.read_csv('P_1000ev.csv', index_col='Unnamed: 0')
    p1000.iloc[0:48] = p1000.iloc[48:96].values
    p1000_immediate = normalize_timeseries(p1000['immediate'].values)
    p1000_balanced = normalize_timeseries(p1000['balanced'].values)

    p2500 = pd.read_csv('P_2500ev.csv', index_col='Unnamed: 0')
    p2500.iloc[0:48] = p2500.iloc[48:96].values
    p2500_immediate = normalize_timeseries(p2500['immediate'].values)
    p2500_balanced = normalize_timeseries(p2500['balanced'].values)

    p5000 = pd.read_csv('P_5000ev.csv', index_col='Unnamed: 0')
    p5000.iloc[0:48] = p5000.iloc[48:96].values
    p5000_immediate = normalize_timeseries(p5000['immediate'].values)
    p5000_balanced = normalize_timeseries(p5000['balanced'].values)

    # Concatenate all series to study differences depending on profile count
    immediate_norm = pd.concat([p500_immediate, p1000_immediate, p2500_immediate, p5000_immediate], axis=1)
    immediate_norm.columns = ['500', '1000', '2500', '5000']

    balanced_norm = pd.concat([p500_balanced, p1000_balanced, p2500_balanced, p5000_balanced], axis=1)
    balanced_norm.columns = ['500', '1000', '2500', '5000']

    return immediate_norm, balanced_norm


def normalize_timeseries(input):
    x = input.reshape(-1,1)
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    x_norm = pd.DataFrame(x_scaled)

    return x_norm


def return_sum_power(path):
    a = pd.read_csv(path)
    a.set_index('Unnamed: 0', drop=True, inplace=True)
    a.drop(a.index[0:3], inplace=True)
    for bla in a.columns:
        a[bla] = a[bla].astype(float)
    cols = a.columns[126:151]
    a = a[cols]
    a = a.sum(axis=1)

    return a

# PV-Freiflächenpotenzial nach Wingenbach / UBA 2013
selExlPV = {
        "access_distance": (5000, None ),
        #"agriculture_proximity": (None, 50 ),
        "agriculture_arable_proximity": (None, 50 ),
        #"agriculture_pasture_proximity": (None, 50 ),
        #"agriculture_permanent_crop_proximity": (None, 50 ),
        #"agriculture_heterogeneous_proximity": (None, 50 ),
        "airfield_proximity": (None, 5 ),    # Diss WB
        "airport_proximity": (None, 5 ),     # Diss WB
        "connection_distance": (10000, None ),
        "dni_threshold": (None, 3.0 ),
        "elevation_threshold": (1500, None ),
        #"ghi_threshold": (None, 3.0 ),
        "industrial_proximity": (None, 0 ),  # Diss Wingenbach / UBA 2013
        "lake_proximity": (None, 5 ),
        "mining_proximity": (None, 100 ),
        "ocean_proximity": (None, 10 ),
        "power_line_proximity": (None, 120 ),   # Diss WB
        "protected_biosphere_proximity": (None, 5 ), # UBA 2013
        "protected_bird_proximity": (None, 5 ), # UBA 2013
        "protected_habitat_proximity": (None, 5 ), # UBA 2013
        "protected_landscape_proximity": (None, 5 ), # UBA 2013
        "protected_natural_monument_proximity": (None, 5 ), # UBA 2013
        "protected_park_proximity": (None, 5 ), # UBA 2013
        "protected_reserve_proximity": (None, 5 ), # UBA 2013
        "protected_wilderness_proximity": (None, 5 ), # UBA 2013
        "camping_proximity": (None, 500),       # UBA 2013)
        #"touristic_proximity": (None, 800),
        #"leisure_proximity": (None, 1000),
        "railway_proximity": (None, 5 ),      # Diss WB
        "river_proximity": (None, 5 ),        # Abweichung vom standardwert (200)
        "roads_proximity": (None, 80 ),         # Diss WB
        "roads_main_proximity": (None, 80 ),    # Diss WB
        "roads_secondary_proximity": (None, 80 ),# Diss WB
        #"sand_proximity": (None, 5 ),
        "settlement_proximity": (None, 600 ),   # Diss WB
        "settlement_urban_proximity": (None, 1000 ),
        #"slope_threshold": (10, None ),
        "slope_north_facing_threshold": (3, None ),
        "wetland_proximity": (None, 5 ), # Diss WB / UBA 2013
        "waterbody_proximity": (None, 5 ), # Diss WB / UBA 2013
        "windspeed_100m_threshold": (None, 4.5 ),
        "windspeed_50m_threshold": (None, 4.5 ),
        "woodland_proximity": (None, 0 ),     # Abweichung vom standardwert (300) / Diss WB
        "woodland_coniferous_proximity": (None, 0 ), # Abweichung vom standardwert (300)
        "woodland_deciduous_proximity": (None, 0 ), # Abweichung vom standardwert (300)
        "woodland_mixed_proximity": (None, 0 ) # Abweichung vom standardwert (300)
        }


#search_string = 'base_year'
#path_to_file = '/home/dbeier/git-projects/disaggregator/disaggregator/config.yaml'
#path_out = '/home/dbeier/git-projects/disaggregator/disaggregator/config123.yaml'
#year = 2025
#change_year(path_to_file, search_string, path_out, year)



#a, b, c, d = load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2014)

#agora_2015  = load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2015)