# Import all the stuff needed
import os
import reegis
import my_reegis
from my_reegis import alternative_scenarios
import deflex
import pandas as pd
import matplotlib
from reegis import config as cfg
from my_reegis import results
from my_reegis import reegis_plot
from my_reegis import upstream_analysis
from my_reegis import plots_de21
from matplotlib import pyplot as plt

cfg.init(paths=[os.path.dirname(deflex.__file__),
                os.path.dirname(my_reegis.__file__)])

# Schritt 1a: Erstelle ein Szenario aus Daten aus dem Internet
year = 2014 # Zur Wahl stehen 2014, 2013, 2012
#geom = 'de21' # Geometrien sind de02, de17, de21, de22
#p = deflex.basic_scenario.create_basic_scenario(year, rmap=my_rmap )

# for geom in ['de02', 'de17', 'de21']:
#     for inc_fac in [1.5, 2, 3, 4]:
#         # Schritt 1b: Alternativ: Lade vorhandenes Szenario
#         name = '{0}_{1}_{2}'.format('deflex', year, geom)
#         path = os.path.join(cfg.get('paths', 'scenario'), 'deflex', str(year))
#         csv_dir = name + '_csv'
#         csv_path = os.path.join(path, csv_dir)
#         meta = {'year': year,
#                 'model_base': 'deflex',
#                 'map': geom,              #
#                 'solver': cfg.get('general', 'solver')}
#         sc = deflex.Scenario(name=name, year=2014, meta=meta)
#         sc.load_csv(csv_path)
#
#
#         # Schritt 2: Manipuliere Daten, um gewünschtes Szenario zu erhalten
#         # Erhöhe Anteil EE
#         #inc_fac = 1
#         alternative_scenarios.increase_re_share(sc, inc_fac)
#         # Reduziere Kraftwerkspark (Kernkraft, Braun- und Steinkohle)
#         alternative_scenarios.reduce_power_plants(sc, nuclear = 1, lignite = 1, hard_coal = 1)
#
#
#         # Erhöhe WP-Anteil -> Fehlermeldung, ggf. muss Kennlinie eingegeben werden
#         #alternative_scenarios.more_heat_pumps(sc,heat_pump_fraction=0.5, cop=2.5)
#
#
#         # Schritt 3: Bereite Berechnung vor
#         # Schreibe die Table Collection in das Energiesystemobjekt
#         sc.table2es()
#         # Erstelle Optimierungsmodell
#         sc.create_model()
#         # Löse das Optimierungsmodell
#         sc.solve()
#         # Speichere den Dump
#         res_path = os.path.join(path, 'results_{0}'.format(cfg.get('general', 'solver')),'DB')
#         os.makedirs(res_path, exist_ok=True)
#         inc_fac_str = str(inc_fac*100)
#         out_file = os.path.join(res_path, name + '_' + inc_fac_str +  '.esys')
#         sc.dump_es(out_file)
#

# Schritt 4: Analyse der Ergebnisse
# Laden des dumps
# Festlegen von EE-Anteil, Jahr und Geometrie zum Laden der Ergebnisse
ee, year, geom = 100, 2014, 'de17'
inc_ee = '_' + str(ee)
name = '{0}_{1}_{2}'.format('deflex', year, geom)
path = os.path.join('/home/dbeier/reegis/scenarios/deflex', str(year))
res_path = os.path.join(path, 'results_cbc','DB', name +  '.esys')

# Lade gelöstes Energiesystem der Wahl in den Workspace
#sc_calc = results.load_es(res_path)
sc_calc = results.load_es('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/deflex_2014_de02.esys')

# Market Clearing Prices und Emissionen des Systems
cost_em_param = results.fetch_cost_emission(sc_calc, with_chp=True)
cost_em = upstream_analysis.get_emissions_and_costs(sc_calc,with_chp=True)

# Plotte MCP und Emissionen
cost_em.mcp[1000:2000].plot()
plt.show()
cost_em.emission[1000:2000].plot()
plt.show()

# Energieflussbilanzen um alle Knoten
my_reegis.reegis_plot.plot_multiregion_io(sc_calc)
plt.show()

# Ergebnisse der Optimierung (Bus-Balance)
# Vollständige Multiindex DF
# Level 0 = Regionen
# Level 1 = in / out flow
# Level 2 = Flüsse sortiert nach oemof Klassen
# Level 3 = chp / ee / electricity / pp
# Level 4 = Energieträger (bio/geo/coal/hydro/solar/wind etc.)
mrbb = results.get_multiregion_bus_balance(sc_calc).groupby(level=[0,4], axis=1).sum()

# Vollaststunden der Technologien ausgeben lassen
flh = results.fullloadhours(sc_calc)

# Plot all buses
reegis_plot.plot_bus_view(es=sc_calc)
plt.show()

# Geoplots
#DE 13 ist SH und DE20 SH-angebundes offshore Gebiet
d = {'DE01': 0.7, 'DE02': 0.5, 'DE03': 2, 'DE04': 2, 'DE05': 1,'DE06': 1.5, 'DE07': 1.5, 'DE08': 2, 'DE09': 2.5, 'DE10': 3, 'DE11': 2.5, 'DE12': 3, 'DE13': 10.1, 'DE14': 0.5, 'DE15': 1,
'DE16': 2, 'DE17': 2.5, 'DE18': 3, 'DE19': 0, 'DE20': 0, 'DE21': 0}
s = pd.Series(d)
df = pd.DataFrame(s, columns=['value'])
p1 = reegis_plot.plot_regions(offshore=['DE21', 'DE20', 'DE19'], legend=False, label_col='index', textbox=False)
p2 = reegis_plot.plot_regions(data=df, data_col='value', label_col=None)
plt.show()

