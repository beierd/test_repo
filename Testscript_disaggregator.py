from disaggregator import config, data, plot, spatial, temporal
from matplotlib import pyplot as plt
import pandas as pd
# Legt eine config-Datei an mit wesentlichen Informationen zum Zugriff auf Datenbank, Basisjahr etc.
cfg = config.get_config()

# Landkreise mit NUTS3-Code und Name extrahieren
dict_nuts3_name = config.dict_region_code(keys='id_ags', values='natcode_nuts3', level='lk',
                     raw=False)


# Vordefinierte Funktionen für Datenbankzugriff
df_spatial = data.database_description('spatial')
df_temporal = data.database_description('temporal')
df_pop = data.population()
df_HH = data.households_per_size()
df_ls = data.living_space()

# Gesamter HH-Verbrauch, bei True Verbrauch nach HH-Größe
elc_consumption_hh = data.elc_consumption_HH(by_HH_size=False)
# Jahresstromverbrauch der Haushalte nach Landkreis -> Datenbankabfrage
elc_consumption_hh_spat = data.elc_consumption_HH_spatial()
# Nach Ansicht des Konsortiums ggf. die beste Option. Strombedarf wird unter Berücksichtigung der unterschiedlichen
# Haushaltsgrößen "bottom-up" ermittelt. Zusätzlich erfolgt Einkommensgewichtung
ec_hh_ic = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1)
#elc_consumption_hh_spat = elc_consumption_hh_spat.pipe(data.append_region_name) # Füge Landkreisnamen hinzu
# Gibt SLP skaliert auf Gesamthaushaltsverbrauch zurück (in MW)
elc_consumption_hh_temp = data.elc_consumption_HH_temporal()
# Gibt Matrix mit SLP-Vebräuchen für jede Region zurück
elc_consumption_hh_spattemp = data.elc_consumption_HH_spatiotemporal(year=2012, freq='15T')
# 15-Min Auflösung zurückgeben
bla = data.reshape_spatiotemporal(freq='15T', key='elc_cons_HH_spatiotemporal')

# Selektieren von einzelnen Regionen
region_pick = ['DE111', 'DE116', 'DE11B'] #Testweise Auswahl von Regionen
sel_elc_consumption_hh_spattemp = elc_consumption_hh_spattemp[region_pick] # SLP-Profile für Auswahl
sel_elc_consumption_hh_yearly = elc_consumption_hh_spat[region_pick] # Jahresstromverbrauch in MWh



df_inc = data.income(by='population')

# Plots funktionieren so weit. Diverse Möglichkeiten sich Daten auf Landkreisebene anzuschauen
fig, ax = plot.choropleth_map(df_pop/1e6, relative=False, unit='Mio. cap', axtitle='Population absolute')
fig, ax = plot.choropleth_map(df_HH, relative=True, unit='households', axtitle='Households /w', colorbar_each_subplot=True, add_percentages=False)

### Räumliche Disaggregation - Zuordnung von Energieverbräuchen ###
# Jahresstromverbräuche nach Haushalten und Einwohnern
ec_pop = spatial.disagg_households_power(by='population', weight_by_income=False)
ec_hh = spatial.disagg_households_power(by='households', weight_by_income=False)
# Einkommensgewichtung der Verbräuche, da als großer Einflussfaktor identifiziert
ec_pop_ic = spatial.disagg_households_power(by='population', weight_by_income=True)

# Wärmeverbrauch
df_heat = spatial.disagg_households_heat(by='households')
df_heat_bld = spatial.disagg_households_heat(by='buildings')
df_gas_td = spatial.disagg_households_gas(how='top-down')
df_gas_bu = spatial.disagg_households_gas(how='bottom-up')
#df_gas_bu2 = spatial.disagg_households_gas(how='bottom-up_2')




# Erstellung Verhaltensbasierter Lastprofile
# Hole SLP aus Datenbank
idx = pd.date_range(start='{}-01-01'.format(2012), end='{}-12-31 23:00'.format(2012), freq='1H')
SLP = data.database_get(dimension='temporal', table_id=23, year=2012)
SLP_h = pd.DataFrame(SLP.loc[0][8], index=idx) #SLP für Landkreis DE111
SLP = data.database_get(dimension='temporal', table_id=25, year =2012)
SLP_h2 = pd.DataFrame(SLP.loc[0][8], index=idx) #SLP für Landkreis DE111

zvelp=pd.DataFrame([], index=idx)
regions = df_heat.index

for i in range(0,2):
    reg = regions[i]
    zvelp_temp = temporal.make_zve_load_profiles(return_profile_by_application=False, return_profile_by_typeday=False, reg=reg, year=2012)
    #zvelp = pd.concat([zvelp,zvelp_temp],sort=False)
    zvelp[reg]=zvelp_temp[reg]


# Vergleich von SLP und ZVE Profil (normiert)

plt.plot(SLP_h)
plt.plot(SLP_h2)

test2014 = temporal.make_zve_load_profiles(year=2014, reg ='DE111')
test2015 = temporal.make_zve_load_profiles(year=2015, reg ='DE111')
test2016 = temporal.make_zve_load_profiles(year=2016, reg ='DE111')

test = test2014
test.append(test2015)
test.append(test2016)

# Extrahiere Stromverbrauch für reegis
from disaggregator import data

cfg = config.get_config()

# ToDo: Fallunterscheidungen einbauen (SLP, ZVE), Bedarf Top-Down / Bottom-Up


# elc_consumption_hh_spattemp_slp = data.elc_consumption_HH_spatiotemporal(year=year, freq=freq)
elc_consumption_hh_spattemp_zve = temporal.make_zve_load_profiles(year=year)

# ToDo Bedarf für heat demand

# ToDo Zukunftsprojektionen erstellen


########
# Demo CTS industry aggregations 

df_CTS = temporal.disagg_temporal_power_CTS(detailed=False, use_nuts3code=True)


# In der Tabelle sind Stromverbräuche je LK bis 2060 drin
#test = data.database_get('spatial', table_id=55, internal_id_2=1 , year=2020)

ec_hh_2030 = temporal.create_projection(ec_hh, target_year = 2030, by='population')

# Get households heat consumption by nuts3-region
hc_hh = spatial.disagg_households_heat(by='households').sum(axis=1)