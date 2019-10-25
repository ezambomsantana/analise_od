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
from ast import literal_eval

def calculate_distance(origin, dest):  
    return geopy.distance.geodesic(origin, dest).meters


folder_data = "../data/"
folder_images_maps = "/Users/eduardosantana/pesquisa/analise_od/images/maps/"
arq17 = "ind.csv"

data17 = pd.read_csv(arq17, header=0,delimiter=",", low_memory=False) 
data17.columns = ['id','path']

count_2 = 0
count_4 = 0
count_6 = 0

points = []
for index, row in data17.iterrows():
    tup = row['path']
    l = literal_eval(tup)
    elevacao = 0
    dist = 0
    last = 0
    last_pos = 0
    bigger = 0
    bigger_dist = 0
    dir = 'r'
    for item in l[0]:
        if (last != 0):
            dist_link = calculate_distance(last_pos, (item[0], item[1]))
            if last < item[2]:
                if dir == 's':
                    diff = item[2] - last
                    elevacao = elevacao + diff
                    dist = dist + dist_link
                else:
                    if elevacao > bigger:
                        bigger = elevacao
                        bigger_dist = dist
                    diff = item[2] - last
                    elevacao =  diff
                    dist = dist_link
                    dir = 's'
            elif last > item[2]:
                if dir == 'd':
                    diff = last - item[2]
                    elevacao = elevacao + diff
                    dist = dist + dist_link
                else:
                    if elevacao > bigger:
                        bigger = elevacao
                        bigger_dist = dist
                    diff = last - item[2]
                    elevacao =  diff
                    dist = dist_link
                    dir = 'd'
            else:
                dist = dist + dist_link
        last = item[2]
        last_pos = (item[0], item[1])

    if bigger_dist > 0:
        if (bigger/bigger_dist)*100 <= 2:
            count_2 = count_2 + 1
            points.append(l[0][0])
        elif (bigger/bigger_dist)*100 <= 4:
            count_4 = count_4 + 1
            points.append(l[0][0])
        elif (bigger/bigger_dist)*100 <= 6:
            count_6 = count_6 + 1
        if (bigger/bigger_dist)*100 > 100:
            print(row['id'])
print(count_2)
print(count_4)
print(count_6)

import pandas as pd
import folium

def generateBaseMap(default_location=[-23.533773, -46.625290], default_zoom_start=12):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start)
    return base_map

from folium.plugins import HeatMap

df_copy = pd.DataFrame(points, columns =['lat', 'long', 'alt']) 

df_copy['count'] = 1
base_map = generateBaseMap()
m = HeatMap(data=df_copy[['long', 'lat', 'count']].groupby(['long', 'lat']).sum().reset_index().values.tolist(), radius=8, max_zoom=13).add_to(base_map)
m.save("filename.html")
