# Import all the stuff needed
import os
import reegis
import my_reegis
import oemof.solph as solph
from my_reegis import alternative_scenarios
import deflex
import pandas as pd
import numpy as np
import matplotlib
from reegis import config as cfg
from my_reegis import results
from my_reegis import reegis_plot
from my_reegis import upstream_analysis
from my_reegis import plots_de21
from matplotlib import pyplot as plt


def multiple_jdl(inp_df):

    plt_df = inp_df
    plt_df.reset_index(inplace=True)
    del plt_df['index']

    for col in plt_df.columns:
        series = plt_df[col].sort_values(ascending=False)
        series = series.reset_index()
        plt_df[col]=series[col].values

    return plt_df

# Auswertung von DE02-Szenarien
# Laden mehrere Szenarien über "fetch_scenarios"
# de02_scens = results.fetch_scenarios('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/DB', sc_filter={'map':'de02'})
# de02_scens.sort()

de21_scens = results.fetch_scenarios('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/DB', sc_filter={'map':'de21'})
de21_scens.sort()

scens_dict={}
for i in range(0, len(de21_scens)):
    tmp = results.load_es(de21_scens[i])
    key = de21_scens[i][-8:-5]
    scens_dict[key] = tmp

scens = [x for x in scens_dict.keys()]

# Jahresdauerlinie der Strompreise / Emissionen im Vergleich

erg_em, erg_mcp, em_total, new_df= pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

for n in scens:
    es = scens_dict.get(n)
    cost_em = upstream_analysis.get_emissions_and_costs(es, with_chp=True)
    #tmp_em, tmp_mcp= cost_em.emission.sort_values(ascending=False), cost_em.mcp.sort_values(ascending=False)
    erg_em[n] = cost_em.emission
    erg_mcp[n] = cost_em.mcp
    em_total[n] = cost_em.emission_absolute
    #plt.plot(np.arange(8760),tmp_em)
    #plt.plot(np.arange(8760),tmp_mcp)

# Plot 1: Mittlere Emissionen
new_df = multiple_jdl(erg_em)

plt.figure()
plt.plot(new_df)
plt.title('Mittlere Emissionen des Kraftwerksparks', size='large')
plt.xlabel('Stunde des Jahres', size='large')
plt.ylabel('Emissionen in g/kWh', size='large')
plt.legend(scens)

# Plot 2: MCP
new_df = multiple_jdl(erg_mcp)

plt.figure(); plt.plot(new_df); plt.title('Marginale Grenzkosten', size='large')
plt.xlabel('Stunde des Jahres', size='large'); plt.ylabel('Kosten in €/MWh', size='large'); plt.legend(scens)


## Überschüsse in SH, Entwicklung von emissionen und Vollaststunden
flh_all, cost_em_param_all, excess_all, lb_saldo_sh, lb_saldo=pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

for n in scens:
    flh = results.fullloadhours(scens_dict.get(n), dropnan=True)['flh']
    cost_em_param = results.fetch_cost_emission(scens_dict.get(n))['emission']
    mrbb=results.get_multiregion_bus_balance(scens_dict.get(n))
    excess = mrbb.DE13.out.excess['electricity']['all']
    #excess = mrbb.DE01.out.excess['electricity']['all']
    p_saldo = mrbb.groupby(level=[0,2], axis=1).sum()
    lb_saldo_sh[n] = p_saldo.DE13.trsf + p_saldo.DE13.source - p_saldo.DE13.demand
    #lb_saldo[n] = p_saldo.DE01.trsf + p_saldo.DE01.source - p_saldo.DE01.demand
    flh_all[n]=flh
    cost_em_param_all[n]=cost_em_param
    excess_all[n]=excess
    exc_tmp = excess.sort_values(ascending=False)


# Plot 3: Leistungsbilanzsaldo
plt_df = multiple_jdl(lb_saldo_sh)
plt.figure(); plt.plot(plt_df); plt.legend(scens)
plt.title('Jahresdauerlinie Leistungsbilanz SH'); plt.xlabel('Stunde des Jahres', size='large')
plt.ylabel('Über- / Unterdeckung in MW', size='large')

# Plot 4: Überschüsse
plt_df = multiple_jdl(excess_all)
plt.figure(); plt.clf(); plt.plot(plt_df, linewidth=2.5)
plt.xscale('log'); plt.legend(scens); plt.title('Überschussleistung SH')
plt.xlabel('Stunde des Jahres', size='large'); plt.ylabel('Überschussleistung in MW', size='large')

# # # Plot 5: Überschüsse 2-Knoten-Modell
# plt_df = multiple_jdl(excess_all)
# plt.figure(); plt.clf(); plt.plot(plt_df, linewidth=2.5)
# plt.xscale('log'); plt.legend(scens); plt.title('Überschussleistung 2-Knoten-Modell')
# plt.xlabel('Stunde des Jahres', size='large'); plt.ylabel('Überschussleistung in MW', size='large')
#
# # Plot 6: Leistungsbilanzsaldo 2-Knoten-Modell
# plt_df = multiple_jdl(lb_saldo)
# plt.figure(); plt.plot(plt_df); plt.legend(scens)
# plt.title('Jahresdauerlinie Leistungsbilanz SH'); plt.xlabel('Stunde des Jahres', size='large')
# plt.ylabel('Über- / Unterdeckung in MW', size='large')