from disaggregator import config, spatial, temporal, data
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import os
import snippets

data.cfg["base_year"] = 2015

### Spatial disaggregations of power consumption per sector

def get_households_power():

    # Get households power consumption by nuts3-region and convert to MWh -> Klappt nur bis 2015
    ec_hh = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1) *1000
    df_temp = (pd.read_csv(config.data_out('ZVE_timeseries_AllRegions_2015.csv'),
                           engine='c', index_col=0, parse_dates=True,
                           infer_datetime_format=True)
                  .pipe(data.transpose_spatiotemporal)
               )

    ec_hh_temp = temporal.disagg_temporal(ec_hh, df_temp, time_indexed=True)

    return ec_hh_temp


# Get households power consumption by nuts3-region and convert to MWh -> Klappt nicht für 2018ff
ec_hh = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1) *1000

# Get CTS power consumption by nuts3-region
ec_CTS_detail = spatial.disagg_CTS_industry(sector='CTS', source='power', use_nuts3code=True)
ec_CTS = ec_CTS_detail.sum()

# Get industry power consumption
ec_industry_detail = spatial.disagg_CTS_industry(sector='industry', source='power', use_nuts3code=True)
ec_industry = ec_industry_detail.sum()

# Should be slightly above 500 TWh
sumcheck = (ec_hh.sum() + ec_CTS.sum() + ec_industry.sum())/1e6


#### Temporal disaggregations
df_CTS = temporal.disagg_temporal_power_CTS(detailed=False, use_nuts3code=True)
powerprofile_CTS = df_CTS.sum(axis=1)

# Industrielastprofile nach nuts3 und kummuliert
df_ec_industry_no_self_gen = temporal.disagg_temporal_industry(source='power', no_self_gen=False,
                                                               detailed=False, use_nuts3code=True, low=0.35)

powerprofile_industry = df_ec_industry_no_self_gen.sum(axis=1)

# Haushaltslastprofil mit SLP
powerprofile_hh_SLP = data.elc_consumption_HH_spatiotemporal(year=2015).sum(axis=1)

# Haushaltsprofil mit ZVE
powerprofile_hh_ZVE = get_households_power().sum(axis=1)
powerprofile_hh_ZVE.index = pd.date_range(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00", freq='H')

# Bildung der Summenprofile
cum_profile_SLP = powerprofile_CTS.resample('H').sum() + powerprofile_industry.resample('H').sum() + powerprofile_hh_SLP
cum_profile_ZVE = powerprofile_CTS.resample('H').sum() + powerprofile_industry.resample('H').sum() + powerprofile_hh_ZVE

# Einlesen der Agoradaten
agora_2015 = snippets.load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/',
                                                   year=2015)

#z = snippets.load_agora_from_owncloud(path_to_data='ownCloud/FhG-owncloud-Quarree-AB3/Daten/Agora/', year=2015)

load_agora = agora_2015[0]
load_agora = load_agora[0:8760]
load_agora.index = pd.date_range(start="2015-01-01 00:00:00", end="2015-12-31 23:45:00", freq='H')

# Plot der Lastgänge im Vergleich
plt.figure(1)
plt.plot(cum_profile_ZVE, linewidth=2, label='Disaggregator-Load')
plt.plot(load_agora, linewidth=2, label='Agora-Load')
plt.legend()

plt.figure(2)
plt.plot(powerprofile_industry.resample('H').sum(), linewidth=2, label='Industrie')
plt.plot(powerprofile_CTS.resample('H').sum() , linewidth=2, label='GHD')
plt.legend()

plt.figure(3)
disaggregator_load = snippets.plt_jdl(cum_profile_ZVE)
agora_load = snippets.plt_jdl(load_agora)
plt.plot(disaggregator_load, label='Disaggregator')
plt.plot(agora_load, label='Agora')


# Lastprofilglättung
plt.figure(8)
ax = load_agora.plot(label='Agora', linewidth=3, color='black')

for n in range(1, 15, 2):
    profile_mean = cum_profile_ZVE.rolling(window=n).mean()
    #profile_mean[0:len(profile_mean) - n + 1] = profile_mean[n - 1:len(profile_mean)].values
    profile_mean[0:n-1]=36000
    profile_mean.plot(ax=ax, label='Window=' + str(n))

plt.legend()

