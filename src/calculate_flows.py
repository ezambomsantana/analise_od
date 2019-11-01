import openrouteservice
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import csv
import unidecode
import math
import seaborn as sns
import geopy.distance
import utm
from shapely.geometry import shape, LineString, Polygon

teste = pd.read_csv('indices.csv', index_col=0)
dict_routes = teste.to_dict('index')
def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    data['MP_DIST'] = data['FE_VIA'] * data['DISTANCE']
    return data

folder_data = "../data/"
folder_images_maps = "/Users/eduardosantana/pesquisa/analise_od/images/maps/"
arq17 = "dados17.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])
data17['OX'] = data17['CO_O_X'].astype(int)
data17['OY'] = data17['CO_O_Y'].astype(int)
data17['DX'] = data17['CO_D_X'].astype(int)
data17['DY'] = data17['CO_D_Y'].astype(int)
data17['DISTANCE'] = 0

#filters

data17_sp = data17[data17['MUNI_O'] == 36] # Only SP

modos17 = {0:'outros',1:'metro',2:'trem',3:'metro',4:'onibus',5:'onibus',6:'onibus',7:'fretado', 8:'escolar',9:'carro-dirigindo', 10: 'carro-passageiro', 11:'taxi', 12:'taxi-nao-convencional', 13:'moto', 14:'moto-passageiro', 15:'bicicleta', 16:'pe', 17: 'outros'}
data17_sp['MODOPRIN'] = data17_sp['MODOPRIN'].replace(modos17)
data17_carros = data17_sp[data17_sp['MODOPRIN'].isin(['carro-dirigindo'])] 

def calculate_distance(row):  
    origin = utm.to_latlon(row['CO_O_X'],row['CO_O_Y'], 23, 'K')
    dest = utm.to_latlon(row['CO_D_X'],row['CO_D_Y'], 23, 'K')
    return geopy.distance.geodesic(origin, dest).meters

data17_carros['DISTANCE'] = data17_carros.apply(lambda x: calculate_distance(x), axis=1)

data_menor = data17_carros[data17_carros['DISTANCE'] <= 6000]

print(data_menor['FE_VIA'].sum())

flows = pd.read_csv("flows.csv", encoding='latin-1')
lines = []
viagens = []

flows = flows.set_index('index')
flows = flows.join(data_menor, lsuffix='_left', rsuffix='_right')

flow2 = flows[flows['elevation'] == 2]
flow4 = flows[flows['elevation'] == 4]

print(flow2['FE_VIA'].sum())
print(flow4['FE_VIA'].sum())


