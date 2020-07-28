from disaggregator import config, plot, spatial, temporal, data
from matplotlib import pyplot as plt
import pandas as pd

# Teste Funktionalität der Funktion

# Wirkt plausibel und funktioniert, mit HH allerdings nur kleiner Teil des Stromverbrauchs abgedeckt und SLP Methode
# nicht bahnbrechend neu
testprofiles_SLP = get_demandregio_hhload_by_NUTS3_profile(2013, region_pick, method="SLP")
# ZVE Methode mit bugs
testprofiles_ZVE = get_demandregio_hhload_by_NUTS3_profile(2013, region_pick, method="ZVE")
# Die Variante kommt nah an reale Werte, Jahreswahl scheint allerdings schwer
testprofiles_heatload = get_demandregio_heatload_by_NUTS3_annual(2011, all_regions, by='buildings', weight_by_income=True)
# Summe macht nur etwa 60% des Endenergieverbrauch RW+WW aus, berücksichtigt nur Gas
testprofiles_heatload_year = spatial.disagg_households_heatload(year=2015, weight_by_income=False)


endenergieverbrauch_q_gas = pd.DataFrame(columns=['Waermeverbrauch'], index=range(2010, 2019))
for n in range(2010, 2019):
    testprofiles_heatload_year = spatial.disagg_households_heatload(year=n, weight_by_income=False)
    endenergieverbrauch_q_gas.loc[n]['Waermeverbrauch']=testprofiles_heatload_year.HotWater.sum()+testprofiles_heatload_year.SpaceHeating.sum()
    #endenergieverbrauch_q.append(endenergieverbrauch_q, pd.Series(testprofiles_heatload_year.HotWater.sum()+testprofiles_heatload_year.SpaceHeating.sum())) #, ignore_index=True)
    print(testprofiles_heatload_year.sum(axis=1).sum())


endenergieverbrauch_q = pd.DataFrame(columns=['Q'], index=range(2010, 2019))
for n in range(2010, 2019):
    tmp = get_demandregio_heatload_by_NUTS3_annual(n, all_regions, by='buildings', weight_by_income=True)
    endenergieverbrauch_q.loc[n]['Q']= tmp.sum()
    #endenergieverbrauch_q.append(endenergieverbrauch_q, pd.Series(testprofiles_heatload_year.HotWater.sum()+testprofiles_heatload_year.SpaceHeating.sum())) #, ignore_index=True)







