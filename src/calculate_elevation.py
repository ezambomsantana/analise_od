import openrouteservice
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import csv
import unidecode
import math
import geopy.distance
import utm
from shapely.geometry import shape, LineString, Polygon, Point
from ast import literal_eval
from sp_grid import create

def calculate_distance(origin, dest):  
    return geopy.distance.geodesic(origin, dest).meters

folder_data = "../data/"
folder_images_maps = "/Users/eduardosantana/pesquisa/analise_od/images/maps/"
arq17 = "indices.csv"

data17 = pd.read_csv(arq17, header=0,delimiter=",", low_memory=False) 
data17.columns = ['id','path']

data17 = data17.dropna()

count_2 = 0
count_4 = 0
count_6 = 0

points = []
for index, row in data17.iterrows():
    tup = row['path']
    indice = row['id']
    if tup == '':
        continue
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
            origin = l[0][0]
            dest = l[0][-1]
            line = LineString([(origin[0], origin[1]), (dest[0], dest[1])])
            points.append([line,2,l[1],l[2], indice])
            
        elif (bigger/bigger_dist)*100 <= 4:
            count_4 = count_4 + 1       
            origin = l[0][0]
            dest = l[0][-1]
            line = LineString([(origin[0], origin[1]), (dest[0], dest[1])])
            points.append([line,4,l[1],l[2], indice])
        elif (bigger/bigger_dist)*100 <= 6:
            count_6 = count_6 + 1
        if (bigger/bigger_dist)*100 > 100:
            print(row['id'])
print(count_2)
print(count_4)
print(count_6)

def calculate_grids():
    global points

    grids = create().geodataframe()
    origins_x = []
    origins_y = []
    dests_x = []
    dests_y = []
    elevations = []
    distances = []
    times = []
    indices = []
    i = []
    j = []
    count = 0
    for item in points:
        achou_origin = False
        achou_dest = False      
        origin_index = 0
        origin_dest = 0  
        for index, row in grids.iterrows():   
            polygon = row['geometry'] 
            if polygon.contains(Point(item[0].coords[0])):
                origin_index = index 
                i.append(row['i'])    
                achou_origin = True     
            if polygon.contains(Point(item[0].coords[1])):
                origin_dest = index                
                j.append(row['j'])    
                achou_dest = True   

        if achou_origin and achou_dest:
            count = count + 1
            print(count)
            rowOrigin = grids.iloc[[origin_index]]
            rowdest = grids.iloc[[origin_dest]]

            origin = rowOrigin['geometry'].centroid
            dest = rowdest['geometry'].centroid

            origin = origin.iloc[0]
            dest = dest.iloc[0]

            line = LineString([origin, dest])
            origins_x.append(origin.x)
            origins_y.append(origin.y)
            dests_x.append(dest.x)
            dests_y.append(dest.y)
            elevations.append(item[1])
            distances.append(item[2])
            times.append(item[3])
            indices.append(item[4])
            continue

    frame = pd.DataFrame(list(zip(indices, i,j,elevations, distances, times, origins_x, origins_y, dests_x, dests_y)), columns =['index','i','j','elevation','distance','time','origin_x', 'origin_y', 'dest_x', 'dest_y'])
    frame.to_csv('flows.csv')
    return frame

calculate_grids()