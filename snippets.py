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

#search_string = 'base_year'
#path_to_file = '/home/dbeier/git-projects/disaggregator/disaggregator/config.yaml'
#path_out = '/home/dbeier/git-projects/disaggregator/disaggregator/config123.yaml'
#year = 2025
#change_year(path_to_file, search_string, path_out, year)



#a, b, c, d = load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2014)

#agora_2015  = load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2015)