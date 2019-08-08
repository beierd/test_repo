import os
import reegis
import my_reegis
import deflex
import pandas as pd
import matplotlib
from reegis import config as cfg
from my_reegis import results
from my_reegis import reegis_plot
from my_reegis import upstream_analysis
from my_reegis import plots_de21
from matplotlib import pyplot as plt
#import PyQt5
#matplotlib.use('Qt5Agg')

# Ini-Dateien von deflex/reegis auslesen, da script außerhalb der Repos ist
cfg.init(paths=[os.path.dirname(deflex.__file__),
                os.path.dirname(my_reegis.__file__)])

# Ergebnis-Energieystem laden
de21_2014 = results.load_es('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/deflex_2014_de21.esys')
de02_2014 = results.load_es('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/deflex_2014_de02.esys')
#de17_2014 = results.load_es('/home/dbeier/reegis/scenarios/deflex/2014/results_cbc/deflex_2014_de17.esys')
#de02_2013 = results.load_es('/home/dbeier/reegis/scenarios/deflex/2013/results_cbc/deflex_2013_de02.esys')
results_obj = de21_2014.results['main']

# Results

# Kosten und Emissionen des Gesamtsystems
cost_em = upstream_analysis.get_emissions_and_costs(de02_2014,with_chp=True)

# Vollaststunden je Erzeugungseinheit
vlh = results.fullloadhours(de02_2014)

# Index des DataFrame auslesen
index = vlh.index
# Überprüfe alle indexlevel auf den Bestandteil DE13 = SH
sh = [x for x in index if 'DE13' in x[0:4]]
# Filtere DataFrame mit erstelltem Index
sh_data = vlh.loc[sh]



# Zeitreihen
# Filter:In- und Exporte nach source/storage/shortage etc.
multi_reg_res = results.get_multiregion_bus_balance(de02_2014).groupby(
    level=[1, 2], axis=1).sum()

# Vollständige Multiindex DF
# Level 0 = Regionen
# Level 1 = in / out flow
# Level 2 = Flüsse sortiert nach oemof Klassen
# Level 3 = chp / ee / electricity / pp
# Level 4 = Energieträger (bio/geo/coal/hydro/solar/wind etc.)

mrr0 = results.get_multiregion_bus_balance(de02_2014)
test=mrr0['DE01']

# Zeigt level 2: oemof objects
mrr1 = results.get_multiregion_bus_balance(de21_2014).groupby(level=[0,4], axis=1).sum()


# mrr1['electricity'][1000:3100].plot()
# plt.show()

#
mrr2 = results.get_multiregion_bus_balance(de21_2014).groupby(level=[1, 2], axis=1)



# Installierte Leistungen abfragen
# Level 0 : oemof classes (dem/excess/line/shortage/source/storage/trsf)
# Level 1 : chp/ee/electricity/pp
# Level 2 : Regionen + Energieträger (von?)
# Level 3 : Regionen + Energieträger (nach?)
nv = results.get_nominal_values(de02_2014, cat='bus', tag='electricity', subtag=None)
nv_sort = nv.groupby(level=[2,3]).sum()

# Sortieren nach typ
#nv_sort = nv.groupby(['ee','trsf'])



# MCP(?) für alle Szenarien -> Funktioniert nicht, weil nicht angelegt
#mcp_all = upstream_analysis.fetch_mcp_for_all_scenarios("/home/dbeier/reegis/scenarios/deflex/2014/results_cbc",'cbc')




# Plots

#plots_de21.de21_grid(rmap='de21')

# Plot für Market Clearing Preis
cost_em['mcp'][1000:2000].plot()
plt.show()

# Energieflussbilanzen um alle Knoten
my_reegis.reegis_plot.plot_multiregion_io(de02_2014)
plt.show()

# Fehler: Length of order must be same as number of levels (4), got 3 -> Lösbar durch level = [1, 2, 3]
# reegis_plot.show_region_values_gui(de21_2014)
# plt.show()

# Plot all buses
reegis_plot.plot_bus_view(es=de02_2014)
plt.show()

# Plot regions
# Anmerkung David: Genauer erforschen!
# reegis_plot.plot_regions(deflex_map=None, fn=None, data=None, textbox=True,
#                  data_col=None, cmap=None, label_col='data_col', color=None,
#                  edgecolor='#9aa1a9', legend=True, ax=None, offshore=None,
#                  simple=None)

#DE 13 ist SH und DE20 SH-angebundes offshore Gebiet
d = {'DE01': 0.7, 'DE02': 0.5, 'DE03': 2, 'DE04': 2, 'DE05': 1,'DE06': 1.5, 'DE07': 1.5, 'DE08': 2, 'DE09': 2.5, 'DE10': 3, 'DE11': 2.5, 'DE12': 3, 'DE13': 10.1, 'DE14': 0.5, 'DE15': 1,
'DE16': 2, 'DE17': 2.5, 'DE18': 3, 'DE19': 0, 'DE20': 0, 'DE21': 0}
s = pd.Series(d)
df = pd.DataFrame(s, columns=['value'])
p1 = reegis_plot.plot_regions(offshore=['DE21', 'DE20', 'DE19'], legend=False, label_col='index', textbox=False)
p2 = reegis_plot.plot_regions(offshore=['DE21', 'DE20', 'DE19'], legend=False)
p3 = reegis_plot.plot_regions(data=df, data_col='value', label_col=None)
plt.show()

## Übung: Installierte PV-Leistung plotten

# Vollaststunden je Erzeugungseinheit
vlh = results.fullloadhours(de21_2014)
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
mrbb = results.get_multiregion_bus_balance(de21_2014)
p_saldo = mrbb.groupby(level=[0,2], axis=1).sum()

# Bilde für jede Region die Differenz aus Im- und Export. Negative Werte bedeuten Überschuss (Verbraucherpfeilsystem)
list_temp = []
for n in region_pv:
    tmp = pd.DataFrame(data = p_saldo[n]['import'] - p_saldo[n]['export'], columns=[n])
    list_temp.append(tmp)

lb = pd.concat(list_temp, axis=1)
index = lb.index

mycmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    'mycmap', [
        (0, 'darkgreen'),
        (0.1, 'yellow'),
        (0.5, 'orangered'),
        (1, 'red')])



hh = 1000 - 1 # Stunde des Jahres, die angezeigt werden soll (vorne)
lb_t = lb[hh:hh+1]
lb_plt = pd.DataFrame(lb_t.iloc[0,:])
lb_plt = pd.DataFrame(lb_plt, columns=[str(index[hh])])

plt_lb = reegis_plot.plot_regions(data=lb_plt, data_col= str(index[hh]), cmap=mycmap, label_col=None)
plt.title('Leistungsbilanz')
plt.show()



#plt.title(str(index[hh]))






# Plot power lines plot erst nochmal verstehen ... Was ist data und was ist key?
# reegis_plot.plot_power_lines(cmap_lines=None, cmap_bg=None, direction=True,
#                      vmax=None, label_min=None, label_max=None, unit='GWh',
#                      size=None, ax=None, legend=True, unit_to_label=False,
#                      divide=1, decimal=0)


#plots_de21.de21_region(custom_coordinates=False, draw_02_line=False)