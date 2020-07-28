from emobpy import Mobility, Availability, Charging, DataBase
from emobpy.plot import NBplot  # Only for visualization for single time series
import pandas as pd

from IPython.display import display, HTML
display(HTML("<style>.container { width:98% !important; }</style>"))


# create mobility instance for Driving electricity consumption ts.
m = Mobility()

prm = {'person':'ev_user',
        'group':'freetime',  # two alternatives only: 'commuter' or 'freetime'
        'refdate':'01/01/2015',
        'energy_consumption': 0.18,
        'hours': 8760,
        'timestep_in_hrs':0.5}

m.setParams(prm)

stats1 = pd.read_csv('/home/dbeier/git-projects/emobpy_examples/openmod/' + 'stats/1_daytrips.csv')
stats2 = pd.read_csv('/home/dbeier/git-projects/emobpy_examples/openmod/' + 'stats/2_departurepurposetrip.csv')
stats3 = pd.read_csv('/home/dbeier/git-projects/emobpy_examples/openmod/' + 'stats/3_tripdistance.csv')

m.setStats(stats1,stats2,stats3)

# Now set rules
rules={'weekday':
            {
             'last_trip_to':{'home':True},
             'overall_min_time_at':{'home':7}
            },
        'weekend':
            {
             'last_trip_to':{'home':True},
             'overall_min_time_at':{'home':7}
            }
       }

m.setRules(rules)
#m.initial_conf()
m.run()

profile = m.timeseries

#m.save_profile('db')
#m.initial_conf()

#db = DataBase('db')
#db.update()
#viz = NBplot(db)
#viz.sgplot_dp('ev_user_W3_93127')


# Grid Availability
manager = DataBase('db')
manager.db
manager.update()
bla = manager.db.keys()

ga = Availability('ev_user_W3_c21b7')

chdata = {'prob_charging_point' :
                 {
                  'leisure':  {'public':0.5,'none':0.5},
                  'shopping': {'public':0.5,'none':0.5},
                  'home':     {'public':0.5,'none':0.5},
                  'driving':  {'none':1.0}
                  },
        'capacity_charging_point' :
                  {'public':22,'none':0}
            }

ga.setScenario(chdata)
ga.setVehicleFeature(40, 0.9)
ga.setBatteryRules(0.5, 0.05, altern=[50,60,70])
ga.loadSettingDriving(manager)
ga.run()

chprofile = ga.timeseries
ga.save_profile('db')
manager.update()
viz = NBplot(manager)
viz.sgplot_ga('ev_user_W3_c21b7_avai_fdd70')




# Synthesis: Electrical load profile
manager = DataBase('db')
manager.update()

for k in manager.db.keys():
    print(k,':',manager.db[k]['kind'])

imm = Charging('ev_user_W3_c21b7_avai_fdd70')

# Charging strategy "immediate"
imm.loadScenario(manager)
imm.setSubScenario('immediate')
imm.run()
imm.save_profile('db')

# Charging strategy "balanced"
bal = Charging('ev_user_W3_c21b7_avai_fdd70')
bal.loadScenario(manager)
bal.setSubScenario('balanced')
bal.run()
bal.save_profile('db')

# Cjarging strategy from 22 to 10
hom = Charging('ev_user_W3_c21b7_avai_fdd70')
hom.loadScenario(manager)
hom.setSubScenario('from_22_to_10_at_home')
hom.run()
hom.save_profile('db')

manager.update()
viz = NBplot(manager)
viz.sgplot_ged('ev_user_W3_c21b7_avai_fdd70_from_22_to_10_at_home_dc9b7')


