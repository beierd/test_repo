from disaggregator import data, config, spatial
from deflex import geometries as geo_deflex
from reegis import geometries as geo_reegis
import integrate_demandregio, Land_Availability_GLAES
import pandas as pd
import os



#data.cfg['base_year'] = 2015
nuts3_regions = list(config.dict_region_code(keys='natcode_nuts3', values='name').keys())
nuts3_regions[0:2]=[]

# Fetch electricity consumption for all NUTS3-Regions
elc_consumption = integrate_demandregio.get_demandregio_electricity_consumption_by_nuts3(2015, nuts3_regions)
data.cfg["base_year"] = 2014
ec_hh = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1) * 1000
elc_consumption['households'] = ec_hh

# Fetch heat consumption for all NUTS3-Regions
heat_consumption = integrate_demandregio.get_combined_heatload_for_region(2015, nuts3_regions)
heat_hh = integrate_demandregio.get_household_heatload_by_NUTS3(2014, nuts3_regions, how='top-down')
heat_consumption['Households'] = heat_hh

# Load suitable PV/Wind-areas from csv
filename = os.getcwd() + '/GLAES_Eignungsflaechen_Wind_PV_own_assumptions.csv'
suitable_area = pd.read_csv(filename)
suitable_area.set_index('nuts3', drop=True, inplace=True)

# Alternatively if no precalculation is available:
# path = os.getcwd() + '/nuts3_geojson/'
# suitable_area = Land_Availability_GLAES.get_pv_wind_areas_by_nuts3(path, create_geojson=True)

# Define installable capacity per square meter in MW
p_per_qm_wind = 8 / 1e6 # 8 W/m² Fläche
p_per_qm_pv = 200 / 1e6 # 200 W/m² Fläche -> eta=20%


# Calculate maximum installable capacity for onshore wind and rooftop-PV
P_max_wind = suitable_area['wind_area'] * p_per_qm_wind
P_max_pv = suitable_area['pv_area'] * p_per_qm_pv


calc_de17 = True
calc_de22 = True
calc_de22_NEP2030 = True

if calc_de17:

    de17_list = geo_reegis.get_federal_states_polygon().index
    dflx_input_fedstates = pd.DataFrame(index=de17_list, columns = ['power','lt-heat','ht-heat','P_wind', 'P_pv'])

    for zone in de17_list:
        region_pick = integrate_demandregio.get_nutslist_per_zone(region_sel=zone, zones='fed_states')
        dflx_input_fedstates.loc[zone]['power'] = elc_consumption.sum(axis=1)[region_pick].sum()
        dflx_input_fedstates.loc[zone]['lt-heat'] = (heat_consumption['Households']+heat_consumption['CTS']+heat_consumption['Industry'])[region_pick].sum()
        dflx_input_fedstates.loc[zone]['ht-heat'] = heat_consumption['ProcessHeat'][region_pick].sum()
        dflx_input_fedstates.loc[zone]['P_wind'] = P_max_wind[region_pick].sum()
        dflx_input_fedstates.loc[zone]['P_pv'] = P_max_pv[region_pick].sum()


if calc_de22:
    # Get indices for zones of interest
    de22_list = geo_deflex.deflex_regions(rmap='de22', rtype='polygons').index
    # Aggregate values for de17 and de22 regions to prepare for
    # Create empty Dataframe
    dflx_input = pd.DataFrame(index=de22_list, columns = ['power','lt-heat','ht-heat','P_wind', 'P_pv'])

    for zone in de22_list:
        region_pick = integrate_demandregio.get_nutslist_per_zone(region_sel=zone, zones='de22')
        dflx_input.loc[zone]['power'] = elc_consumption.sum(axis=1)[region_pick].sum()
        dflx_input.loc[zone]['lt-heat'] = (heat_consumption['Households']+heat_consumption['CTS']+
                                           heat_consumption['Industry'])[region_pick].sum()
        dflx_input.loc[zone]['ht-heat'] = heat_consumption['ProcessHeat'][region_pick].sum()
        dflx_input.loc[zone]['P_wind'] = P_max_wind[region_pick].sum()
        dflx_input.loc[zone]['P_pv'] = P_max_pv[region_pick].sum()


# Get installed capacities NEP2030
NEP2030_capacity = pd.read_excel('NEP2030_capacities.xls')
NEP2030_capacity.set_index('fedstate', drop=True, inplace=True)
NEP2030_capacity = NEP2030_capacity.multiply(1e3)

if calc_de22 and calc_de17:
    test = pd.concat([dflx_input_fedstates, NEP2030_capacity['onshore'],NEP2030_capacity['offshore'],
                    NEP2030_capacity['solar pv']], axis=1)

    test.drop(['N0', 'N1','O0','P0'], axis=0, inplace=True)

# Skalierung des Bundesländerzubaus auf Landkreise anhand der Eignungsfläche
# Achtung: NEP in einigen Bundesländern mit höheren Werten
scaling_wind = test['onshore'] / test['P_wind']
scaling_pv = test['solar pv'] / test['P_pv']

# Zuordnung der installierten Leistungen zu den jeweiligen Landkreisen
P_NEP = pd.DataFrame(index=P_max_wind.index, columns=['onshore', 'pv'])

for zone in scaling_wind.index:
    region_pick = integrate_demandregio.get_nutslist_per_zone(region_sel=zone, zones='fed_states')
    for nuts3 in region_pick:
        P_NEP.loc[nuts3]['onshore'] = P_max_wind[nuts3] * scaling_wind[zone]
        P_NEP.loc[nuts3]['pv'] = P_max_pv[nuts3] * scaling_pv[zone]


if calc_de22_NEP2030:
    # Aggregate values for de17 and de22 regions to prepare for
    # Create empty Dataframe
    dflx_input_NEP2030 = pd.DataFrame(index=de22_list, columns = ['power','lt-heat','ht-heat','P_wind', 'P_pv'])
    # Lower heat consumption due to efficiency measures
    heat_NEP2030 = heat_consumption.multiply(0.75)
    elc_consumption_NEP2030 = elc_consumption # Add load profiles for e-mobility

    for zone in de22_list:
        region_pick = integrate_demandregio.get_nutslist_per_zone(region_sel=zone, zones='de22')
        dflx_input_NEP2030.loc[zone]['power'] = elc_consumption.sum(axis=1)[region_pick].sum()
        dflx_input_NEP2030.loc[zone]['lt-heat'] = (heat_NEP2030['Households']+heat_NEP2030['CTS']+
                                           heat_NEP2030['Industry'])[region_pick].sum()
        dflx_input_NEP2030.loc[zone]['ht-heat'] = heat_consumption['ProcessHeat'][region_pick].sum()
        dflx_input_NEP2030.loc[zone]['P_wind'] = P_NEP['onshore'][region_pick].sum()
        dflx_input_NEP2030.loc[zone]['P_pv'] = P_NEP['pv'][region_pick].sum()