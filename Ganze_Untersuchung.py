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

for geom in ['de02', 'de17', 'de21']:

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
    inc_fac = 1
    alternative_scenarios.increase_re_share(sc, inc_fac)
    # Reduziere Kraftwerks
    alternative_scenarios.reduce_power_plants(sc, nuclear = 0.5, lignite = 0, hard_coal = 0.5)
    # Erhöhe WP-Anteil -> Fehlermeldung, ggf. muss Kennlinie eingegeben werden
    #alternative_scenarios.more_heat_pumps(sc,heat_pump_fraction=0.5, cop=2.5)


    # Schritt 3: Bereite Berechnung vor
    # Schreibe die Table Collection in das Energiesystemobjekt
    sc.table2es()
    # Erstelle Optimierungsmodell
    sc.create_model()
    # Löse das Optimierungsmodell
    sc.solve()
    # Speichere den Dump
    res_path = os.path.join(path, 'results_{0}'.format(cfg.get('general', 'solver')),'DB')
    os.makedirs(res_path, exist_ok=True)
    inc_fac = str(inc_fac*100)
    out_file = os.path.join(res_path, name + '_' + inc_fac +  '.esys')
    sc.dump_es(out_file)



    # Schritt 4: Analyse der Ergebnisse
    #csv_path = os.path.join(path, 'results_cbc', name + '.esys')
    #sc_calc = results.load_es(out_file)
    #cost_em = upstream_analysis.get_emissions_and_costs(sc_calc,with_chp=True)

