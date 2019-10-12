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

folder_data = "/home/eduardo/dev/analise_od/data/"
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
data17_carros = data17_sp[data17_sp['MODOPRIN'].isin(['carro-dirigindo', 'carro-passageiro'])] 

def calculate_distance(row):  
    origin = utm.to_latlon(row['CO_O_X'],row['CO_O_Y'], 23, 'K')
    dest = utm.to_latlon(row['CO_D_X'],row['CO_D_Y'], 23, 'K')
    return geopy.distance.geodesic(origin, dest).meters

data17_carros['DISTANCE'] = data17_carros.apply(lambda x: calculate_distance(x), axis=1)

data_menor = data17_carros[data17_carros['DISTANCE'] <= 6000]
data_menor = data_menor.head(4350)
def calculate_distance_openservice(row):  
    if row.name not in dict_routes.keys(): 
        try:

            origin = utm.to_latlon(row['CO_O_X'],row['CO_O_Y'], 23, 'K')
            dest = utm.to_latlon(row['CO_D_X'],row['CO_D_Y'], 23, 'K')

            coords = ((origin[1],origin[0]), (dest[1], dest[0]))
            print(coords)
            client = openrouteservice.Client(key='5b3ce3597851110001cf62480f68a481f69543088477def361e9517d') # Specify your personal API key
            routes = client.directions(coords)
            geometry = routes['routes'][0]['geometry']
            elevs = client.elevation_line('encodedpolyline', geometry)
            lista = elevs['geometry']['coordinates']
            dist = routes['routes'][0]['segments'][0]['distance']
            duration = routes['routes'][0]['segments'][0]['duration']
            return (lista, dist, duration)

        except:
            print("An exception occurred")
            return ''

data_menor['DISTANCE_LIST'] = data_menor.apply(lambda x: calculate_distance_openservice(x), axis=1)
data_menor = data_menor.dropna(subset=['DISTANCE_LIST'])

frame = data_menor[['DISTANCE_LIST']]
print(frame)
teste = teste.append(frame)
print(teste)

teste.to_csv('indices.csv')


