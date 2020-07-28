from disaggregator import config, spatial, temporal, data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import os
import snippets

data.cfg["base_year"] = 2015

hc_hh = spatial.disagg_households_heat(by='households').sum(axis=1)

# Haushaltsgasverbrauch nach LK
df_gas = spatial.disagg_households_gas()
ratio_EFH = data.percentage_EFH_MFH(MFH=False)
ratio_MFH = data.percentage_EFH_MFH(MFH=True)

heat_EFH = hc_hh.multiply(ratio_EFH)
heat_MFH = hc_hh.multiply(ratio_MFH)

df_temp_EFH = data.standard_load_profile_gas(typ='EFH')
df_temp_MFH = data.standard_load_profile_gas(typ='MFH')

df_temp_EFH = data.transpose_spatiotemporal(df_temp_EFH)
df_temp_MFH = data.transpose_spatiotemporal(df_temp_MFH)

heat_st_EFH = temporal.disagg_temporal(heat_EFH, df_temp_EFH, time_indexed=True)
heat_st_MFH = temporal.disagg_temporal(heat_MFH, df_temp_MFH, time_indexed=True)

heat_st_MFH = temporal.disagg_temporal(hc_hh, df_temp_MFH, time_indexed=True)


#heatload = heat_st_EFH + heat_st_MFH
#heatload_plot = heatload.sum(axis=1)
#plt.figure(6)
#plt.plot(heatload_plot)


def get_heat_by_nuts3(year):
    data.cfg["base_year"] = year
    hc_hh = spatial.disagg_households_heat(by='households').sum(axis=1)
    df_gas = spatial.disagg_households_gas()

# SLPs berücksichtigen unterschiedliche Wetterjahre, sogar auf LK-Ebene, aber nur für 2014-2016 vorhanden
# Wärmelast hc_hh variiert leicht über die Jahre, aber deutlich geringer als Gas. Gas dürfte relevanter für Witterungseinfluss sein
# Idee: Gesamte Wärmelast als Grundlage und Skalierung über Gasverbräuche
# Alternativ vorhanden: Außentemperatur 2006-2019
# Gasverbräuche Industrie und CTS nur für 2015 ...
# Vor allem: Keine Auftrennung der Gasverwendung in der Industrie


# Industriegasverbrauch
# Zahlen 2017
# Industriewärmeverbrauch nach BDEW: 515 TWh Prozesswärme, 47 TWh Raumwärme, 5 TWh Warmwasser
# GHD Wärmeverbrauch nach BDEW: 42 TWh Prozesswärme, 197 TWh Raumwärme, 19 TWh Warmwasser



def get_CTS_heatload(year, region_pick):

    data.cfg['base_year'] = year
    heatload_hh = data.gas_consumption_HH().sum()/0.47
    heatload_CTS = 0.37 * heatload_hh  #Verhältnis aus dem Jahr 2017
    gc_CTS = spatial.disagg_CTS_industry(sector='CTS', source='gas', use_nuts3code=True)
    sum_gas_CTS = gc_CTS.sum().sum()
    inc_fac = heatload_CTS / sum_gas_CTS
    gc_CTS_new = gc_CTS.multiply(inc_fac)
    gc_CTS_combined = gc_CTS_new.sum()
    df = gc_CTS_combined[region_pick]

    return df



def get_industry_heating_hotwater(year, region_pick):
    data.cfg['base_year'] = year
    heatload_hh = data.gas_consumption_HH().sum()/0.47
    heatload_industry = 0.089 * heatload_hh  #Verhältnis aus dem Jahr 2017
    gc_industry = spatial.disagg_CTS_industry(sector='industry', source='gas', use_nuts3code=True)
    sum_gas_industry = gc_industry.sum().sum()
    inc_fac = heatload_industry / sum_gas_industry
    gc_industry_new = gc_industry.multiply(inc_fac)
    gc_industry_combined = gc_industry_new.sum()
    df = gc_industry_combined[region_pick]

    return df

def get_industry_CTS_process_heat(year, region_pick):
    data.cfg['base_year'] = year
    gc_industry = spatial.disagg_CTS_industry(sector='industry', source='gas', use_nuts3code=True)
    sum_gas_industry = gc_industry.sum().sum()
    inc_fac = (515 + 42) * 1e6 / sum_gas_industry
    ph_industry = gc_industry.multiply(inc_fac)
    ph_industry_combined = ph_industry.sum()
    df = ph_industry_combined[region_pick]

    return df



test0 = get_household_heatload_by_NUTS3(2017, all_regions)
test1 = get_CTS_heatload(2017, all_regions)
test2 = get_industry_heating_hotwater(2017, all_regions)
test3 = get_industry_CTS_process_heat(2017, all_regions)

df_heating = pd.concat([test0, test1, test2])
df_heating.columns = ['Households', 'CTS', 'Industry']



