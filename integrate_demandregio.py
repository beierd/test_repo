from disaggregator import data, config, spatial, temporal
import pandas as pd
import logging

ec_hh_ic = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1)

#SSH Key test
#SSH Key test2

#Generate region pick for testing
dict_nuts3_name = config.region_id_to_nuts3(nuts3_to_name=True)
cfg = config.get_config()
cfg["base_year"]=2016

if cfg["use_nuts_2016"] is True:
     del dict_nuts3_name['DE915'], dict_nuts3_name['DE919']

region_pick = list(dict_nuts3_name.keys())[0:3]
all_regions = list(dict_nuts3_name.keys())


def get_demandregio_hhload_by_NUTS3_profile(year, region_pick, method='SLP'):
    """
    Parameters
    ----------
    year : int
        Year of interest
    region_pick : list
        Selected regions in NUTS-3 format
    method : string
        Chosen method to generate temporal profile, either 'SLP' or 'ZVE'

    Returns: pd.DataFrame
        Dataframe containing yearly household load for selection
    -------
    """

    if method is 'SLP':
        elc_consumption_hh_spattemp = data.elc_consumption_HH_spatiotemporal(year=year)
        df = elc_consumption_hh_spattemp[region_pick]

    elif method is 'ZVE':
        logging.warning('Can be lengthy for larger lists')
        list_result = []
        sum_load = data.elc_consumption_HH_spatial(year=year)
        for reg in region_pick:
            elc_consumption_hh_spattemp_zve = temporal.make_zve_load_profiles(year=year, reg=reg) * sum_load[reg]
            list_result.append(elc_consumption_hh_spattemp_zve)
        df = pd.concat(list_result, axis=1, sort=False)

    else:
        raise ValueError('Chosen method is not valid')

    return df


def get_demandregio_heatload_by_NUTS3_annual(year, region_pick, by='buildings', weight_by_income='True'):

    """
    Parameters
    ----------
    year : int
        Year of interest
    region_pick : list
        Selected regions in NUTS-3 format
    by : string
        Can be either 'buildings' or 'households'
    weight_by_income : bool
        Choose whether heat demand shall be weighted by household income

    Returns: pd.DataFrame
        Dataframe containing yearly household load for selection
    -------
    """
    # Abbildung des Witterungseinflusses über Abweichung im Gasverbrauch zwischen 2010-2018
    year_norm = pd.DataFrame({'Faktor' :[1.16, 0.94, 1.02, 1.07, 0.89, 0.97, 1.01, 1, 0.93]}, index=range(2010, 2019))

    qdem_temp = spatial.disagg_households_heat(by=by, weight_by_income=weight_by_income)
    qdem_temp = qdem_temp.SpaceHeatingPlusHotWater.sum(axis=1)
    qdem_temp = qdem_temp.multiply(year_norm.loc[year]['Faktor'])
    df = qdem_temp[region_pick]

    return df


get_demandregio_heatload_by_NUTS3_annual(region_pick, by='buildings')




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





# ToDo:
# Auswahl des Jahres sollte Effekt auf Verbrauch haben
# Integration ZVE statt SLP


# # Read yearly power consumption by NUTS-3 region from FfE-Database
ec_hh_ic = spatial.disagg_households_power(by='households', weight_by_income=True).sum(axis=1)

# Select Power Consumption for the NUTS-3 regions within the selected shape
E_el_hh = ec_hh_ic[region_pick]

#elc_consumption_hh_spattemp_zve = temporal.make_zve_load_profiles(year=year)
