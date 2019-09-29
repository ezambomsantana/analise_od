# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
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
import json

app = Flask(__name__)
api = Api(app)

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

folder_data = "/Users/eduardosantana/pesquisa/analise_od/data/"
folder_images_maps = "/Users/eduardosantana/pesquisa/analise_od/images/maps/"
arq17 = "dados17.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X']).head(100)
geos = []
for index, row in data17.iterrows():
    lat = row['CO_O_X']
    lon = row['CO_O_Y']
    lista = []
    dest = utm.to_latlon(lat,lon, 23, 'K')
    geos.append((dest[1],dest[0]))
data17['coords'] = geos
print(data17['coords'])
class Metro(Resource):
    def get(self):
        return metro.to_json()


class Distritos(Resource):
    def get(self):
        return mapa.to_json()

class Pontos(Resource):
    def get(self):
        return data17['coords'].to_json()

api.add_resource(Metro, '/metro')
api.add_resource(Distritos, '/distritos') 
api.add_resource(Pontos, '/pontos')


if __name__ == '__main__':
     app.run(port='5002')