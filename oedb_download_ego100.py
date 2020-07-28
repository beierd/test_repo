import requests
import pandas as pd


def get_eGo100_res(path):
        oep_url= 'https://openenergy-platform.org'
        # Include Filters
        schema = 'supply'
        table = 'ego_dp_res_powerplant'
        where = 'scenario=eGo+100&where=version=v0.4.5'
        column= 'column=electrical_capacity&column=generation_type&column=generation_subtype&column=flag' \
                '&column=thermal_capacity&column=comment&column=geom&column=nuts&column=version&column=scenario'
        result = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where+'&'+column+'&',)
        #result = requests.get(oep_url+'/api/v0/schema/'+schema+'/tables/'+table+'/rows/?where='+where+'&'+column,)
        df_ego100 = pd.DataFrame(result.json())
        df_ego100.to_csv(path)


def load_prepare_ego_data(path):
        df = pd.read_csv(path)
        df.drop('Unnamed: 0', axis=1, inplace=True)
        df.electrical_capacity = pd.to_numeric(df.electrical_capacity)
        return df





path = '/home/dbeier/Daten/eGo100.csv'