### Within this script releant energy system data for a mid-term scenario is fetched and processed

import scenario_builder
from disaggregator import data
from scenario_builder import cop_precalc, snippets
from deflex import geometries as geo_deflex
from reegis import land_availability_glaes, demand_disaggregator, entsoe, demand_heat
from reegis import geometries as geo_reegis
from scenario_builder import emobpy_processing
import pandas as pd
import os


# Set parameters and get data needed for all scenarios
nuts3_index = data.database_shapes().index
de21 = geo_deflex.deflex_regions(rmap='de21')
year = 2015
path_to_data = '/home/dbeier/reegis/data/scenario_data/commodity_sources_costs.xls'
profile = entsoe.get_entsoe_load(2014).reset_index(drop=True)["DE_load_"]
norm_profile = profile.div(profile.sum())

heat_profiles_reegis = demand_heat.get_heat_profiles_by_region(de21, 2014, name='test')

profile_lt = snippets.return_normalized_domestic_profiles(de21, heat_profiles_reegis)
profile_ht = snippets.return_normalized_industrial_profiles(de21, heat_profiles_reegis)

# Fetch costs and emission applicable for scenario (sheet1)
costs = snippets.get_cost_emission_scenario_data(path_to_data)

# Fetch overall res potential
res_potential = land_availability_glaes.aggregate_capacity_by_region(de21)




###
# 1. Status Quo scenario
keys = ['Storage', 'commodity_source', 'decentralised_heat', 'lt_heat_series', 'ht_heat_series', 'elc_series',
        'storages', 'transformer', 'transmission', 'volatile_series', 'volatile_source']
scen_dict_sq = dict.fromkeys(keys)

# Write scenario costs to dict
scen_dict_sq['commodity_source'] = costs['StatusQuo']

# Fetch electricity consumption for all NUTS3-Regions
elc_consumption_sq =  demand_disaggregator.aggregate_power_by_region(de21, year, elc_data=None)
elc_profile_sq = pd.DataFrame(columns=elc_consumption_sq.index)

for reg in elc_consumption_sq.index:
    elc_profile_sq[reg] = elc_consumption_sq.sum(axis=1)[reg] * norm_profile

# Fetch heat consumption for all NUTS3-Regions
heat_consumption_sq = demand_disaggregator.aggregate_heat_by_region(de21, year, heat_data=None)

lt_heat_profile_sq = pd.DataFrame(columns=heat_consumption_sq.index)
ht_heat_profile_sq = pd.DataFrame(columns=heat_consumption_sq.index)

for reg in heat_consumption_sq.index[0:18]:
    lt_heat_profile_sq[reg] = heat_consumption_sq['lt-heat'][reg] * profile_lt[reg]
    ht_heat_profile_sq[reg] = heat_consumption_sq['ht-heat'][reg] * profile_ht[reg]

scen_dict_sq['elc_series'] = elc_profile_sq
scen_dict_sq['lt_heat_series'] = lt_heat_profile_sq
scen_dict_sq['ht_heat_series'] = ht_heat_profile_sq




# 2. NEP 2035
E_wp = 28.7 + 1e6 # 28.7 TWh elektrische Energie in MWh

# Load NEP2030 pp capacities
# Match NEP capacity with land availability
path_to_NEP_capacities= '/home/dbeier/reegis/data/scenario_data/NEP2030_capacities.xls'
NEP_capacities = snippets.transform_NEP_capacities_to_de21(path_to_NEP_capacities)

# ToDo: Älteste Kraftwerke der Tpyen auf Bundesländerebene reduzieren und dann in de21 transformieren

# Load and prepare demand series
# Electrical base load should be similar to today
elc_profile_NEP_base =  elc_profile_sq # MWh

# According to NEP scenario 25 TWh of electrical energy is used for charging BEVs. Profile generated with emobpy
E_emob = 25 * 1e6 # 25 TWh electrical energy in MWh (scaling factor)
ch_power = emobpy_processing.return_averaged_charging_series(weight_im=0.4, weight_bal=0.4, weight_night=0.2)
elc_profile_NEP_emob = E_emob * ch_power





# Demand Series (Wärmebedarf runter, el. Lastprofil um E-Mob ergänzen)

# 3. All Electric

# 4. SynFuel