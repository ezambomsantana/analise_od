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

def load_districts():
    mapa = gpd.GeoDataFrame.from_file("/Users/eduardosantana/anexos/Distritos_2017_region.shp", encoding='latin-1')

    geos = []
    for index, row in mapa.iterrows():
        pairs = row['geometry']
        lista = []
        if (isinstance(pairs, Polygon)):
            for pair in pairs.exterior.coords:
                dest = utm.to_latlon(pair[0],pair[1], 23, 'K')
                lista.append((dest[1],dest[0]))
        geos.append(Polygon(lista))
    mapa['geometry'] = geos
    return map

def load_subway():
    metro = gpd.GeoDataFrame.from_file("/Users/eduardosantana/anexos/SIRGAS_SHP_linhametro_line.shp", encoding='latin-1')
    geos = []
    for index, row in metro.iterrows():
        pairs = row['geometry']
        lista = []
        for pair in pairs.coords:
            dest = utm.to_latlon(pair[0],pair[1], 23, 'K')
            lista.append((dest[1],dest[0]))
        geos.append(LineString(lista))
    metro['geometry'] = geos
    return metro

def load_data17():
    folder_data = "/Users/eduardosantana/pesquisa/analise_od/data/"
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