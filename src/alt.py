import folium as folium
import geopandas as gpd
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import unidecode
import math
import utm
from shapely.geometry import shape, LineString, Polygon
import matplotlib as mpl
import xmltodict


folder_images_maps = "../images/"
def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    data['MP_DIST'] = data['FE_VIA'] * data['DISTANCE']
    return data

zonas = gpd.GeoDataFrame.from_file("../data/shapes/Zonas_2017_region.shp", encoding='latin-1')
zonas = zonas.to_crs({"init": "epsg:4326"}) 

zonas['NomeDistri'] = zonas['NomeDistri'].apply(lambda x: unidecode.unidecode(x))
zonas['NomeZona'] = zonas['NomeZona'].apply(lambda x: unidecode.unidecode(x))

zonas = zonas[zonas['NumeroMuni'] == 36]

print(zonas)

teste = pd.read_csv('../data/alts.csv', index_col='id')
print(teste)

csv_file = "../data/alts.csv"
mydict = []
xs = []
ys = []
zs = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=",")
    mydict = {rows[0]:rows[1] for rows in reader}
        
with open('../data/labeled_network.xml') as fd:
    doc = xmltodict.parse(fd.read())
    
    for element in doc['network']['nodes']['node']:

        if element['@id'] in mydict:

            teste = mydict[element['@id']]
            x = str(element['@x'])
            y = str(element['@y'])
            xs.append(float(x))
            ys.append(float(y))
            zs.append(int(teste))

frame = pd.DataFrame(list(zip(xs, ys, zs)), columns =['x', 'y','z'])
    
gdf = gpd.GeoDataFrame(
    frame, geometry=gpd.points_from_xy(frame.x, frame.y))
print(gdf)
sjoin = gpd.sjoin(zonas, gdf, op='contains')

conj17 = sjoin[['NomeZona', 'z']].groupby(['NomeZona']).std().sort_values(by=['z']).reset_index()
conj17.columns = ['NomeZona', 'media']
conj17 = conj17.set_index('NomeZona')
print(conj17)

conj17.to_csv('distrito_inclinacao.csv')