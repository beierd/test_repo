from emobpy import Mobility, Availability, Charging, DataBase
from emobpy.plot import NBplot  # Only for visualization for single time series
import pandas as pd
from matplotlib import pyplot as plt
import snippets, os
from sklearn import preprocessing

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


    # Summenprofil für Ladeleistung (23 to 8)
    ch_profiles_23to8 = pd.DataFrame()
    for k in keys_23to8:
        tmp = manager.db[k]["timeseries"]["charge_grid"]
        ch_profiles_23to8 = pd.concat([ch_profiles_23to8, tmp], axis=1)

    P_23to8 = ch_profiles_23to8.sum(axis=1)


    # Summenprofil für Ladeleistung (0 to 24)
    ch_profiles_0to24 = pd.DataFrame()
    for k in keys_0to24:
        tmp = manager.db[k]["timeseries"]["charge_grid"]
        ch_profiles_0to24 = pd.concat([ch_profiles_0to24, tmp], axis=1)

    P_0to24 = ch_profiles_0to24.sum(axis=1)

    P_sum = pd.concat([P_immediate, P_balanced, P_23to8, P_0to24], axis=1)
    P_sum.columns = ['immediate', 'balanced', '23to8', '0to24']

    # P_sum = pd.concat([P_immediate, P_balanced], axis=1)
    # P_sum.columns = ['immediate', 'balanced']

    return P_sum

# This part will take a long time and needs a lot of memory (>100G)
#path = '/home/dbeier/git-projects/emobpy_examples/casestudy/500ev/'
#P_500ev = get_charging_profiles_from_database(path)
#P_500ev.to_csv('P_500ev.csv')

# path = '/home/dbeier/git-projects/emobpy_examples/casestudy/1000ev/'
# P_1000ev = get_charging_profiles_from_database(path)
# P_1000ev.to_csv('P_1000ev.csv')
#
# path = '/home/dbeier/git-projects/emobpy_examples/casestudy/2500ev/'
# P_2500ev = get_charging_profiles_from_database(path)
# P_2500ev.to_csv('P_2500ev.csv')
#
# path = '/home/dbeier/git-projects/emobpy_examples/casestudy/5000ev/'
# P_5000ev = get_charging_profiles_from_database(path)
# P_5000ev.to_csv('P_5000ev.csv')


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


def return_normalized_charging_series(path):
    p = pd.read_csv(path, index_col='Unnamed: 0')
    # Cut off initial charging
    p.iloc[0:48] = p.iloc[48:96].values
    idx = pd.DatetimeIndex(p.index, freq='30min')
    p.set_index(idx, inplace=True)
    p_immediate = p['immediate']
    p_balanced = p['balanced']

    immediate_hourly = p_immediate.resample('H').sum()
    balanced_hourly = p_balanced.resample('H').sum()

    # Normalize Yearly energy use to 1
    immediate_norm = immediate_hourly * (1 / immediate_hourly.sum())
    balanced_norm = balanced_hourly * (1 / balanced_hourly.sum())

    return immediate_norm, balanced_norm


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


immediate_norm, balanced_norm = load_and_compare_charging_of_fleets()

# Load charging profiles and return normalized charging series
immediate, balanced = return_normalized_charging_series('P_5000ev.csv')

P_inst = 10 * 1e3 # 10 GWh
P_immediate = immediate.multiply(P_inst)
P_balanced = balanced.multiply(P_inst)



## Test if multiple runs lead to different results
path1 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_original/a_ts.csv'
path2 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_original/b_ts.csv'
path3 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_original/c_ts.csv'

a = return_sum_power(path1)
b = return_sum_power(path2)
c = return_sum_power(path3)

mean1 = (a + b + c) / 3

# Plot depicts charging profiles for immediate charging for three test runs (with random seed)
plt.figure()
plt.plot(a.values), plt.plot(b.values), plt.plot(c.values), plt.plot(mean1.values, LineWidth=3.5)

path1 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_random/a_ts.csv'
path2 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_random/b_ts.csv'
path3 = '/home/dbeier/git-projects/emobpy_examples/casestudy/csv/test_random/c_ts.csv'

ar = return_sum_power(path1)
br = return_sum_power(path2)
cr = return_sum_power(path3)
mean2 = (ar + br + cr) / 3

# Plot depicts charging profiles for immediate charging for three test runs (without random seed)
plt.figure()
plt.plot(ar.values), plt.plot(br.values), plt.plot(cr.values), plt.plot(mean2.values, LineWidth=3.5)

plt.figure(), plt.plot(mean1.values), plt.plot(mean2.values)


os.chdir('/home/dbeier/git-projects/emobpy_examples/casestudy')
P1 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev1')
P2 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev2')
P3 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev3')
P4 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev4')
P5 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev5')
P6 = get_charging_profiles_from_database(os.getcwd() + '/multiple_runs/XXev6')



str = '0to24'
mean = (P1[str] + P2[str] + P3[str] + P4[str] + P5[str] + P6[str]) / 6
plt.figure(1), plt.plot(P1[str]), plt.plot(P2[str]), plt.plot(P3[str]), plt.plot(P4[str]), plt.plot(P5[str]), \
plt.plot(P6[str]), plt.plot(mean, LineWidth=3.5), plt.legend()