import geopandas as gpd
import numpy as np
import pandas as pd
import csv
import unidecode
import math
import utm
from shapely.geometry import shape, LineString, Polygon

def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    data['MP_DIST'] = data['FE_VIA'] * data['DISTANCE']
    return data

mapa = gpd.GeoDataFrame.from_file("../data/shapes/Distritos_2017_region.shp", encoding='latin-1')
mapa = mapa.to_crs({"init": "epsg:4326"})
mapa['NomeDistri'] = mapa['NomeDistri'].apply(lambda x: unidecode.unidecode(x))

zonas = gpd.GeoDataFrame.from_file("../data/shapes/Zonas_2017_region.shp", encoding='latin-1')
zonas = zonas.to_crs({"init": "epsg:4326"}) 
zonas['NomeDistri'] = zonas['NomeDistri'].apply(lambda x: unidecode.unidecode(x))
zonas['NomeZona'] = zonas['NomeZona'].apply(lambda x: unidecode.unidecode(x))

folder_data = "../data/"
arq17 = "dados17_distance.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=",", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])

csv_file = folder_data + "regioes17.csv"
mydict = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=";")
    mydict = {rows[0]:rows[1] for rows in reader}

csv_file = folder_data + "zonas17.csv"
zonas_nomes = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=";")
    zonas_nomes = {rows[0]:rows[1] for rows in reader}

data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])

data17['ZONA_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else zonas_nomes[x])
data17['ZONA_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else zonas_nomes[x])

data17['NUM_TRANS'] = data17[['MODO1', 'MODO2','MODO3','MODO4']].count(axis=1)

data17 = calculate_weighted_mean(data17)

def load_districts(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo):

    data17_copy = data17

    if vehicle != "0":
        vehicles = vehicle.split(",")
        vehicles_int = []
        for v in vehicles:
            vehicles_int.append(int(v))
        data17_copy = data17_copy[data17_copy['MODOPRIN'].isin(vehicles_int)] 

    if sexo != "0":
        data17_copy = data17_copy[data17_copy['SEXO'].isin([int(sexo)])]

    if horarioInicio != "0":
        data17_copy = data17_copy[data17_copy['H_SAIDA'] >= int(horarioInicio)]

    if horarioFim != "0":
        data17_copy = data17_copy[data17_copy['H_SAIDA'] <= int(horarioFim)]

    if origin != "0":
        data17_copy = data17_copy[data17_copy['NOME_O'] == origin]
    
    if motivo != "0":
        motivo = motivo.split(",")
        motivo_int = []
        for v in motivo:
            motivo_int.append(int(v))
        data17_copy = data17_copy[data17_copy['MOTIVO_D'].isin(motivo_int)]

    data_mp2 = data17_copy[[orde,  'MP']].groupby([orde]).sum().sort_values(by=['MP']).reset_index()
    data_mp2 = data_mp2.set_index(orde)

    data_mp_dist = data17_copy[[orde,  'MP_DIST']].groupby([orde]).sum().sort_values(by=['MP_DIST']).reset_index()
    data_mp_dist = data_mp_dist.set_index(orde)

    data_mp = data17_copy[[orde, 'MUNI_O', 'FE_VIA']].groupby([orde,'MUNI_O']).sum().sort_values(by=[orde]).reset_index()
    data_mp = data_mp.set_index(orde)

    data_renda = data17_copy[[orde, 'RENDA_FA']].groupby([orde]).mean().sort_values(by=['RENDA_FA']).reset_index()
    data_renda = data_renda.set_index(orde)

    data_trans = data17_copy[[orde, 'NUM_TRANS']].groupby([orde]).mean().sort_values(by=['NUM_TRANS']).reset_index()
    data_trans = data_trans.set_index(orde)

    df = mapa.set_index('NomeDistri').join(data_mp).join(data_mp2).join(data_renda).join(data_trans).join(data_mp_dist)
    df['MEDIA'] = df['MP'] / df['FE_VIA']
    df['MEDIA_DIST'] = df['MP_DIST'] / df['FE_VIA']
    df = df.reset_index()
    return df

def load_subway():
    metro = gpd.GeoDataFrame.from_file("../data/shapes//SIRGAS_SHP_linhametro_line.shp", encoding='latin-1')
    metro.crs = {'init' :'epsg:22523'}
    metro = metro.to_crs({"init": "epsg:4326"})
    return metro

def load_cptm():
    cptm = gpd.GeoDataFrame.from_file("../data/shapes//SIRGAS_SHP_linhatrem_line.shp", encoding='latin-1')
    cptm.crs = {'init' :'epsg:22523'}
    cptm = cptm.to_crs({"init": "epsg:4326"})
    return cptm


def load_data17():
    folder_data = "../data/"
    arq17 = "dados17.csv"

    data17_2 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
    data17_2 = data17_2.dropna(subset=['CO_O_X']).head(100)
    geos = []
    for index, row in data17_2.iterrows():
        lat = row['CO_O_X']
        lon = row['CO_O_Y']
        dest = utm.to_latlon(lat,lon, 23, 'K')
        geos.append((dest[1],dest[0]))
    data17_2['coords'] = geos
    return data17_2

def load_graph(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo):
    df = load_districts(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo)
    origin_distrito = df[df['NomeDistri'] == origin]
    print(df['FE_VIA'])
    lines = []
    viagens = []
    for index, row in df.iterrows():
        if ~np.isnan(row['FE_VIA']):
            origin = origin_distrito['geometry'].iloc[0].centroid
            dest = row['geometry'].centroid
            line = LineString([origin, dest])
            lines.append(line)
            viagens.append(row['FE_VIA'])
    frame = pd.DataFrame(list(zip(lines, viagens)), columns =['geometry', 'FE_VIA'])
    grafo = gpd.GeoDataFrame(frame)
    return grafo

def load_graph_zonas(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo):
    df = load_zonas(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo)
    origin_distrito = df[df['NomeZona'] == origin]
    print(df['FE_VIA'])
    lines = []
    viagens = []
    for index, row in df.iterrows():
        if ~np.isnan(row['FE_VIA']):
            origin = origin_distrito['geometry'].iloc[0].centroid
            dest = row['geometry'].centroid
            line = LineString([origin, dest])
            lines.append(line)
            viagens.append(row['FE_VIA'])
    frame = pd.DataFrame(list(zip(lines, viagens)), columns =['geometry', 'FE_VIA'])
    grafo = gpd.GeoDataFrame(frame)
    return grafo

def load_curitiba():
    curitiba = gpd.GeoDataFrame.from_file("../data/shapes/DIVISA_DE_REGIONAIS.shp", encoding='latin-1')
    curitiba.crs = {'init' :'epsg:22522'}
    curitiba = curitiba.to_crs({"init": "epsg:4326"})
    print(curitiba)
    return curitiba

def load_zonas(vehicle, sexo, horarioInicio, horarioFim, origin, orde, motivo):

    data17_copy = data17

    if vehicle != "0":
        vehicles = vehicle.split(",")
        vehicles_int = []
        for v in vehicles:
            vehicles_int.append(int(v))
        data17_copy = data17_copy[data17_copy['MODOPRIN'].isin(vehicles_int)] 

    if sexo != "0":
        data17_copy = data17_copy[data17_copy['SEXO'].isin([int(sexo)])]

    if horarioInicio != "0":
        data17_copy = data17_copy[data17_copy['H_SAIDA'] >= int(horarioInicio)]

    if horarioFim != "0":
        data17_copy = data17_copy[data17_copy['H_SAIDA'] <= int(horarioFim)]

    if origin != "0":
        data17_copy = data17_copy[data17_copy['ZONA_O'] == origin]
    
    if motivo != "0":
        motivo = motivo.split(",")
        motivo_int = []
        for v in motivo:
            motivo_int.append(int(v))
        data17_copy = data17_copy[data17_copy['MOTIVO_D'].isin(motivo_int)]

    data_mp2 = data17_copy[[orde,  'MP']].groupby([orde]).sum().sort_values(by=['MP']).reset_index()
    data_mp2 = data_mp2.set_index(orde)

    data_mp_dist = data17_copy[[orde,  'MP_DIST']].groupby([orde]).sum().sort_values(by=['MP_DIST']).reset_index()
    data_mp_dist = data_mp_dist.set_index(orde)

    data_mp = data17_copy[[orde, 'MUNI_O', 'FE_VIA']].groupby([orde,'MUNI_O']).sum().sort_values(by=[orde]).reset_index()
    data_mp = data_mp.set_index(orde)

    data_renda = data17_copy[[orde, 'RENDA_FA']].groupby([orde]).mean().sort_values(by=['RENDA_FA']).reset_index()
    data_renda = data_renda.set_index(orde)

    data_trans = data17_copy[[orde, 'NUM_TRANS']].groupby([orde]).mean().sort_values(by=['NUM_TRANS']).reset_index()
    data_trans = data_trans.set_index(orde)

    df = zonas.set_index('NomeZona').join(data_mp).join(data_mp2).join(data_renda).join(data_trans).join(data_mp_dist)
    df['MEDIA'] = df['MP'] / df['FE_VIA']
    df['MEDIA_DIST'] = df['MP_DIST'] / df['FE_VIA']
    df = df.reset_index()
    return df
