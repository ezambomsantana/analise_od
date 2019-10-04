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

def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    data['MP_DIST'] = data['FE_VIA'] * data['DISTANCE']
    return data

def load_districts(vehicle):
    mapa = gpd.GeoDataFrame.from_file("/home/eduardo/Distritos_2017_region.shp", encoding='latin-1')
    mapa = mapa.to_crs({"init": "epsg:4326"})

    folder_data = "/home/eduardo/dev/analise_od/data/"
    arq17 = "dados17_distance.csv"

    data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=",", low_memory=False) 
    data17 = data17.dropna(subset=['CO_O_X'])

    csv_file = folder_data + "regioes17.csv"
    mydict = []
    with open(csv_file, mode='r') as infile:
        reader = csv.reader(infile, delimiter=";")
        mydict = {rows[0]:rows[1] for rows in reader}

    data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    data17['NUM_TRANS'] = data17[['MODO1', 'MODO2','MODO3','MODO4']].count(axis=1)

    data17 = calculate_weighted_mean(data17)
    modos17 = {0:'outros',1:'metro',2:'trem',3:'metro',4:'onibus',5:'onibus',6:'onibus',7:'fretado', 8:'escolar',9:'carro-dirigindo', 10: 'carro-passageiro', 11:'taxi', 12:'taxi-nao-convencional', 13:'moto', 14:'moto-passageiro', 15:'bicicleta', 16:'pe', 17: 'outros'}
    

    if vehicle != "0":
        print(vehicle)

        vehicles = vehicle.split(",")
        print(vehicles)
        vehicles_int = []
        for v in vehicles:
            vehicles_int.append(int(v))
        data17 = data17[data17['MODOPRIN'].isin(vehicles_int)] 
        
    coletivo = ['onibus','trem','metro']
    privado = ['carro-dirigindo','moto','bicicleta','taxi']

    motorizado = ['onibus','trem','metro', 'carro-dirigindo','moto','taxi']
    nao_motorizado = ['bicicleta', 'pe']

    data17 = data17[data17['H_SAIDA'] >= 5]
    data17 = data17[data17['H_SAIDA'] <= 10]

    data_mp2 = data17[['NOME_O',  'MP']].groupby(['NOME_O']).sum().sort_values(by=['MP']).reset_index()
    data_mp2 = data_mp2.set_index('NOME_O')

    data_mp_dist = data17[['NOME_O',  'MP_DIST']].groupby(['NOME_O']).sum().sort_values(by=['MP_DIST']).reset_index()
    data_mp_dist = data_mp_dist.set_index('NOME_O')

    data_mp = data17[['NOME_O', 'MUNI_O', 'FE_VIA']].groupby(['NOME_O','MUNI_O']).sum().sort_values(by=['NOME_O']).reset_index()
    data_mp = data_mp.set_index('NOME_O')
    mapa['NomeDistri'] = mapa['NomeDistri'].apply(lambda x: unidecode.unidecode(x))

    data_renda = data17[['NOME_O', 'RENDA_FA']].groupby(['NOME_O']).mean().sort_values(by=['RENDA_FA']).reset_index()
    data_renda = data_renda.set_index('NOME_O')

    data_trans = data17[['NOME_O', 'NUM_TRANS']].groupby(['NOME_O']).mean().sort_values(by=['NUM_TRANS']).reset_index()
    data_trans = data_trans.set_index('NOME_O')

    df = mapa.set_index('NomeDistri').join(data_mp).join(data_mp2).join(data_renda).join(data_trans).join(data_mp_dist)
    df['MEDIA'] = df['MP'] / df['FE_VIA']
    df['MEDIA_DIST'] = df['MP_DIST'] / df['FE_VIA']
    df = df.reset_index()
    return df

def load_subway():
    metro = gpd.GeoDataFrame.from_file("/home/eduardo/SIRGAS_SHP_linhametro_line.shp", encoding='latin-1')
    metro.crs = {'init' :'epsg:22523'}
    metro = metro.to_crs({"init": "epsg:4326"})
    return metro

def load_data17():
    folder_data = "/home/eduardo/dev/analise_od/data/"
    arq17 = "dados17.csv"

    data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
    data17 = data17.dropna(subset=['CO_O_X']).head(100)
    geos = []
    for index, row in data17.iterrows():
        lat = row['CO_O_X']
        lon = row['CO_O_Y']
        dest = utm.to_latlon(lat,lon, 23, 'K')
        geos.append((dest[1],dest[0]))
    data17['coords'] = geos
    return data17