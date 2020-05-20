#import os
#import deflex
#from reegis import config as cfg

from deflex import basic_scenario
from oemof.tools import logger
a=4
#cfg.init(paths=[os.path.dirname(deflex.__file__),
#                os.path.dirname(my_reegis.__file__)])

#from deflex import main, basic_scenario, scenario_tools, demand


basic_scenario.create_basic_scenario(2014, 'de02')
#main.main(year=2012,rmap='de02')
#main.basic_scenario()
#demand.get_heat_profiles_deflex()



#deflex.main.main(year=20 12, rmap = 'de02')