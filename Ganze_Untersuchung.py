# Import all the stuff needed
import os
import reegis
import my_reegis
import time
from my_reegis import alternative_scenarios
import deflex
import pandas as pd
import numpy as np
from reegis import config as cfg
from my_reegis import results
from my_reegis import reegis_plot
from my_reegis import upstream_analysis
from my_reegis import plots_de21
from matplotlib import pyplot as plt
import oemof_visio as oev

#cfg.init(paths=[os.path.dirname(deflex.__file__),
#                os.path.dirname(my_reegis.__file__)])


cfg.init()

exit(0)
# # Schritt 1a: Erstelle ein Szenario mit Reegis aus Daten aus dem Internet
year = 2014 # Zur Wahl stehen 2014, 2013, 2012
geom = 'de21' # Geometrien sind de02, de17, de21, de22
#p = deflex.basic_scenario.create_basic_scenario(year, rmap=geom )

for geom in ['de02']:
    for inc_fac in [1.55]:
        # Schritt 1b: Alternativ: Lade vorhandenes Szenario
        name = '{0}_{1}_{2}'.format('deflex', year, geom)
        path = os.path.join(cfg.get('paths', 'scenario'), 'deflex', str(year))
        csv_dir = name + '_csv'
        csv_path = os.path.join(path, csv_dir)
        meta = {'year': year,
                'model_base': 'deflex',
                'map': geom,              #
                'solver': cfg.get('general', 'solver')}
        sc = deflex.Scenario(name=name, year=2014, meta=meta)
        sc.load_csv(csv_path)


        # Schritt 2: Manipuliere Daten, um gewünschtes Szenario zu erhalten
        # Erhöhe Anteil EE
        #inc_fac = 1
        alternative_scenarios.increase_re_share(sc, inc_fac)
        # Reduziere Kraftwerkspark (Kernkraft, Braun- und Steinkohle)
        alternative_scenarios.reduce_power_plants(sc, lignite = 0)
        # Füge Gas Kapazitäten hinzu
        #alternative_scenarios.add_one_gas_turbine(sc, nominal_value=20000)
        # Erhöhe WP-Anteil -> Fehlermeldung, ggf. muss Kennlinie eingegeben werden
        #alternative_scenarios.more_heat_pumps(sc,heat_pump_fraction=0.5, cop=2.5)

        # Schritt 3: Bereite Berechnung vor
        # Schreibe die Table Collection in das Energiesystemobjekt
        sc.table2es()
        # Erstelle Optimierungsmodell
        sc.create_model()

        # setze emission limit 25% weniger
        em_limit = 181869813461 * 0,75


        def generic_integral_limitdflx(om, keyword, flows=None, limit=None):
            if flows is None:
                flows = {}
                for (i, o) in om.flows:
                    if hasattr(om.flows[i, o], keyword):
                        flows[(i, o)] = om.flows[i, o]

            else:
                for (i, o) in flows:
                    if not hasattr(flows[i, o], keyword):
                        raise AttributeError(
                            ('Flow with source: {0} and target: {1} '
                             'has no attribute {2}.').format(
                                i.label, o.label, keyword))

            limit_name = "integral_limit_" + keyword

            setattr(om, limit_name, po.Expression(
                expr=sum(om.flow[inflow, outflow, t]
                         * om.timeincrement[t]
                         * sequence(getattr(flows[inflow, outflow], keyword))[t]
                         for (inflow, outflow) in flows
                         for t in om.TIMESTEPS)))

            setattr(om, limit_name + "_constraint", po.Constraint(
                expr=(getattr(om, limit_name) <= limit)))

            return om

        # emission absolute aus szenarienrechnung: 181869813461
        generic_integral_limitdflx(sc.model, keyword='emission', limit=em_limit)

        # Löse das Optimierungsmodell
        sc.solve()
        # Speichere den Dump
        res_path = os.path.join(path, 'results_{0}'.format(cfg.get('general', 'solver')),'DB')
        os.makedirs(res_path, exist_ok=True)
        inc_fac_str = str(int(inc_fac*100))
        out_file = os.path.join(res_path, name + '_' + inc_fac_str +  '.esys')
        sc.dump_es(out_file)


# Schritt 4: Analyse der Ergebnisse
# Laden des dumps
# Festlegen von EE-Anteil, Jahr und Geometrie zum Laden der Ergebnisse
ee, year, geom = 200, 2014, 'de21'
inc_ee = '_' + str(ee)
name = '{0}_{1}_{2}'.format('deflex', year, geom)
path = os.path.join('/home/dbeier/reegis/scenarios/deflex', str(year))
res_path = os.path.join(path, 'results_cbc','DB', name + inc_ee + '.esys')

# Lade gelöstes Energiesystem der Wahl in den Workspace
sc_calc = results.load_es(res_path)
#sc_calc = results.load_es('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/deflex_2014_de02.esys')

# Market Clearing Prices und Emissionen des Systems
cost_em_param = results.fetch_cost_emission(sc_calc, with_chp=True)
cost_em = upstream_analysis.get_emissions_and_costs(sc_calc,with_chp=True)

# Plotte MCP und Emissionen
cost_em.mcp[1000:2000].plot()
plt.title('Market Clearing Prices')
plt.ylabel('€/MWh')
plt.show()
cost_em.emission[1000:2000].plot()
plt.title('Mittlere Emissionen')
plt.ylabel('g/kWh_el')
plt.show()


# Energieflussbilanzen um alle Knoten: Händisch
# multi_reg_res = results.get_multiregion_bus_balance(sc_calc).groupby(
#     level=[1, 2], axis=1).sum()
#
# multi_reg_res[('out', 'losses')] = (multi_reg_res[('out', 'export')] -
#                                     multi_reg_res[('in', 'import')])
# del multi_reg_res[('out', 'export')]
# del multi_reg_res[('in', 'import')]
#
# oev.plot.io_plot(df_in=multi_reg_res['in'],
#                  df_out=multi_reg_res['out'],
#                  smooth=True)
# plt.show()

# Deckung der Last mit "run"
my_reegis.reegis_plot.plot_multiregion_io(sc_calc)
plt.show()


# Mittlere Emissionen
mrbb = results.get_multiregion_bus_balance(sc_calc).groupby(level=[0,3], axis=1).sum()
EE = mrbb.DE01['ee'] + mrbb.DE02['ee']; share_ee = EE / mrbb.DE01['electricity']
em_mean = (1-share_ee)*cost_em.emission


# Vollaststunden der Technologien ausgeben lassen
flh = results.fullloadhours(sc_calc)

# Emissionen nach Energeiträgern aufgelöst
results.emissions(sc_calc)

# Plot all buses
reegis_plot.plot_bus_view(es=sc_calc)
# Für Konsole
#reegis_plot.plot_bus_view2(es=sc_calc)

#Geoplots
#DE 13 ist SH und DE20 SH-angebundes offshore Gebiet
d = {'DE01': 0.7, 'DE02': 0.5, 'DE03': 2, 'DE04': 2, 'DE05': 1,'DE06': 1.5, 'DE07': 1.5, 'DE08': 2, 'DE09': 2.5, 'DE10': 3, 'DE11': 2.5, 'DE12': 3, 'DE13': 10.1, 'DE14': 0.5, 'DE15': 1,
'DE16': 2, 'DE17': 2.5, 'DE18': 3, 'DE19': 0, 'DE20': 0, 'DE21': 0}
s = pd.Series(d)
df = pd.DataFrame(s, columns=['value'])
p1 = reegis_plot.plot_regions(offshore=['DE21', 'DE20', 'DE19'], legend=False, label_col='index', textbox=False)
p2 = reegis_plot.plot_regions(data=df, data_col='value', label_col=None)
plt.show()


# Level 0 = Regionen
# Level 1 = in / out flow
# Level 2 = Flüsse sortiert nach oemof Klassen
# Level 3 = chp / ee / electricity / pp
# Level 4 = Energieträger (bio/geo/coal/hydro/solar/wind etc.)
## Mittlere CO2-Belastung berechnen
mrbb = results.get_multiregion_bus_balance(sc_calc).groupby(level=[0,4], axis=1).sum()


## Übung: Installierte PV-Leistung plotten

# Vollaststunden je Erzeugungseinheit
vlh = results.fullloadhours(sc_calc)
# Index des DataFrame auslesen
index = vlh.index
# Überprüfe alle indexlevel auf den Bestandteil solar
solar = [x for x in index if 'solar' in x[2]]
# Extrahiere Installierte Leistung je Bundesland

p_inst_solar = vlh.loc[solar]['nominal_value']
#region_pv = p_inst_solar.index.get_level_values(3) Zugriff auf eine Indexebene über .get_level_values

pv_inst = {}
for i,v in p_inst_solar.items():
    pv_inst.update({i[3]:v})

s = pd.Series(pv_inst)
df = pd.DataFrame(s, columns=['value'])
p1 = reegis_plot.plot_regions(data=df, data_col='value', label_col=None)
plt.title('Installierte PV-Leistung nach Netzzone')
plt.show()

region_pv = p_inst_solar.index.get_level_values(3)


## Übung: Erzeugungsschwerpunkte für Zeitschritt x darstellen
mrbb = results.get_multiregion_bus_balance(sc_calc)
p_saldo = mrbb.groupby(level=[0,2], axis=1).sum()

# Bilde für jede Region die Differenz aus Im- und Export. Negative Werte bedeuten Überschuss (Verbraucherpfeilsystem)
list_temp = []
for n in region_pv:
    #tmp = pd.DataFrame(data = p_saldo[n]['import'] - p_saldo[n]['export'], columns=[n])
    tmp = pd.DataFrame(data=p_saldo[n]['export'] - p_saldo[n]['import'] , columns=[n])
    list_temp.append(tmp)

lb = pd.concat(list_temp, axis=1)
index = lb.index

plt.figure()
for hh in range(0,12,3):
    #hh = 8550 - 1 # Stunde des Jahres, die angezeigt werden soll (vorne)
    plt.clf()
    lb_t = lb[hh:hh+1]
    lb_plt = pd.DataFrame(lb_t.iloc[0,:])
    lb_plt = pd.DataFrame(lb_plt, columns=[str(index[hh])])

    plt_lb = reegis_plot.plot_regions(data=lb_plt, data_col= str(index[hh]), label_col=None)
    plt.title('Leistungsbilanz  ' + str(lb.index[hh]))
    plt.show()
    time.sleep(2)
