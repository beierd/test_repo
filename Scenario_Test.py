import deflex
import reegis
import pandas
from deflex import basic_scenario


# Definition der Parameter
year = 2014
geom = 'de02'


deflex.basic_scenario.create_basic_scenario(year=year, rmap=geom)


name = '{0}_{1}_{2}'.format('deflex', year, geom)
path = os.path.join(cfg.get('paths', 'scenario'), 'deflex', str(year))

