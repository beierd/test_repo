from emobpy import Mobility, Availability, Charging, DataBase
from emobpy.plot import NBplot  # Only for visualization for single time series
import pandas as pd
from matplotlib import pyplot as plt
import snippets


def get_charging_profiles_from_database(path):

    # Load profiles from Files
    manager = DataBase(path)
    manager.update()

    # Liste mit Availability Profilen
    keys_driving = [k for k, v in manager.db.items() if v['kind'] == 'driving']
    keys_availability = [k for k, v in manager.db.items() if v['kind'] == 'availability']
    keys_charging = [k for k, v in manager.db.items() if v['kind'] == 'charging']
    keys_immediate = [k for k, v in manager.db.items() if v['kind'] == 'charging' and v['option'] == 'immediate' ]
    keys_balanced = [k for k, v in manager.db.items() if v['kind'] == 'charging' and v['option'] == 'balanced' ]
    keys_23to8 = [k for k, v in manager.db.items() if v['kind'] == 'charging' and v['option'] == 'from_23_to_8_at_home']
    keys_0to24 = [k for k, v in manager.db.items() if v['kind'] == 'charging' and v['option'] == 'from_0_to_24_at_home']

    # Summenprofil für Fahrleistung in kmd
    driving_profiles = pd.DataFrame()
    for k in keys_driving:
        test = manager.db[k]["timeseries"]["consumption"]
        driving_profiles = pd.concat([driving_profiles, test], axis=1)

    cum_profile = driving_profiles.sum(axis=1)


    # Summenprofil für Ladeleistung (immediate)
    ch_profiles_immediate = pd.DataFrame()
    for k in keys_immediate:
        tmp = manager.db[k]["timeseries"]["charge_grid"]
        ch_profiles_immediate = pd.concat([ch_profiles_immediate, tmp], axis=1)

    P_immediate = ch_profiles_immediate.sum(axis=1)


    # Summenprofil für Ladeleistung (balanced)
    ch_profiles_balanced = pd.DataFrame()
    for k in keys_balanced:
        tmp = manager.db[k]["timeseries"]["charge_grid"]
        ch_profiles_balanced = pd.concat([ch_profiles_balanced, tmp], axis=1)

    P_balanced = ch_profiles_balanced.sum(axis=1)


    # # Summenprofil für Ladeleistung (23 to 8)
    # ch_profiles_23to8 = pd.DataFrame()
    # for k in keys_23to8:
    #     tmp = manager.db[k]["timeseries"]["charge_grid"]
    #     ch_profiles_23to8 = pd.concat([ch_profiles_23to8, tmp], axis=1)
    #
    # P_23to8 = ch_profiles_23to8.sum(axis=1)
    #
    #
    # # Summenprofil für Ladeleistung (0 to 24)
    # ch_profiles_0to24 = pd.DataFrame()
    # for k in keys_0to24:
    #     tmp = manager.db[k]["timeseries"]["charge_grid"]
    #     ch_profiles_0to24 = pd.concat([ch_profiles_0to24, tmp], axis=1)
    #
    # P_0to24 = ch_profiles_0to24.sum(axis=1)

    # P_sum = pd.concat([P_immediate, P_balanced, P_23to8, P_0to24], axis=1)
    # P_sum.columns = ['immediate', 'balanced', '23to8', '0to24']

    P_sum = pd.concat([P_immediate, P_balanced], axis=1)
    P_sum.columns = ['immediate', 'balanced']

    return P_sum


path = '/home/dbeier/git-projects/emobpy_examples/casestudy/500ev/'
P_500ev = get_charging_profiles_from_database(path)
P_500ev.to_csv('P_500ev.csv')

path = '/home/dbeier/git-projects/emobpy_examples/casestudy/1000ev/'
P_1000ev = get_charging_profiles_from_database(path)
P_1000ev.to_csv('P_1000ev.csv')

path = '/home/dbeier/git-projects/emobpy_examples/casestudy/2500ev/'
P_2500ev = get_charging_profiles_from_database(path)
P_2500ev.to_csv('P_2500ev.csv')

path = '/home/dbeier/git-projects/emobpy_examples/casestudy/5000ev/'
P_5000ev = get_charging_profiles_from_database(path)
P_5000ev.to_csv('P_5000ev.csv')







#plt.figure()
#plt.plot(P_immediate_200ev, label='Direkte Ladung', linewidth=3)
#plt.plot(P_balanced_200ev, label='Gleichmäßige Ladung', linewidth=3)
#plt.plot(P_0to24_200ev, label="0 to 24", linewidth=3)
#plt.plot(P_23to8_200ev, label="23 to 8", linewidth=3)
#plt.legend(), plt.grid()

#plt.figure()
#plt.plot(snippets.plt_jdl(P_immediate_200ev), label="Direkte Ladung")
#plt.plot(snippets.plt_jdl(P_balanced_200ev), label="Gleichmäßige Ladung")
#plt.legend()
#plt.ylim([0, 100])

#plt.figure()
#plt.plot(P_immediate_200ev*factor, label='200ev', linewidth=3)
#plt.plot(P_immediate_500ev, label='500ev', linewidth=3)
#plt.legend()
