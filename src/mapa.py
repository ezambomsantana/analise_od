import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv
import networkx as nx
import utm

import sys  

import plotly.plotly as py
import plotly.graph_objs as go
import plotly

import re
from pyproj import Proj, transform

def teste():
    string = "1kmN2326E3989"

    x1 = int(re.sub('.*[EW]([0-9]+)', '\\1', string))*1000
    y1 = int(re.sub('.*N([0-9]+)[EW].*', '\\1', string))*1000

    inProj = Proj(init='EPSG:3035')
    outProj = Proj(init='epsg:4326')

    lng,lat = transform(inProj,outProj,x1,y1)
    print lat,lng

reload(sys)  
sys.setdefaultencoding('utf8')

folder = "/home/eduardo/dev/analise_od/src/"
arq87 = "dados87.csv"
arq97 = "dados97.csv"
arq07 = "dados07.csv"

def main():
    global folder

    csv_file = folder + "regioes97.csv"
    mydict = []
    with open(csv_file, mode='r') as infile:
        reader = csv.reader(infile, delimiter=";")
        mydict = {rows[0]:rows[1] for rows in reader}

    data07 = pd.read_csv(folder + arq07, dtype={'ZONA_O': str, 'ZONA_D': str, 'FE_VIA':str}, header=0,delimiter=";", low_memory=False) 

    data07 = data07[data07['MUNI_O'] == 36] 
    data07 = data07[data07['MUNI_D'] == 36] 

    data07['ZONA_O'] = data07['ZONA_O'].apply(lambda x: mydict[x])
    data07['ZONA_D'] = data07['ZONA_D'].apply(lambda x: mydict[x])


    dict_pos = {}
    for index, row in data07.iterrows():    
        if row['ZONA_O'] not in dict_pos:
            dict_pos[row['ZONA_O']] = utm.to_latlon(row['CO_O_X'], row['CO_O_Y'], 23, 'K')
        if row['ZONA_D'] not in dict_pos:
            dict_pos[row['ZONA_D']] = utm.to_latlon(row['CO_D_X'], row['CO_D_Y'], 23, 'K')


    data07['COORD_O_X'] = data07['ZONA_O'].apply(lambda x: dict_pos[x][0])
    data07['COORD_O_Y'] = data07['ZONA_O'].apply(lambda x: dict_pos[x][1])
    data07['COORD_D_X'] = data07['ZONA_D'].apply(lambda x: dict_pos[x][0])
    data07['COORD_D_Y'] = data07['ZONA_D'].apply(lambda x: dict_pos[x][1])

    df = data07[['ZONA_O', 'ZONA_D', 'COORD_O_X','COORD_O_Y', 'COORD_D_X','COORD_D_Y', 'FE_VIA']].dropna()


    df[['FE_VIA','float']] = df['FE_VIA'].str.split('.',expand=True)
    df["FE_VIA"] = df["FE_VIA"].astype(int)

    df = df.groupby(['ZONA_O', 'ZONA_D', 'COORD_O_X','COORD_O_Y', 'COORD_D_X','COORD_D_Y']).sum().sort_values(by=['FE_VIA']).reset_index()
    df = df[df['ZONA_O'] != df['ZONA_D']]

    print(df)

    districts = pd.DataFrame.from_dict(dict_pos, orient='index')
    districts = districts.reset_index()
    districts.columns = ['Regiao', 'X', 'Y']
    print(districts)

    max_value = float(df['FE_VIA'].max())
    airports = [go.Scattergeo(
        lon = districts['Y'],
        lat = districts['X'],
        hoverinfo = 'text',
        text = districts['Regiao'],
        mode = 'markers',
        marker = go.scattergeo.Marker(
            size = 2,
            color = 'rgb(255, 0, 0)',
            line = go.scattergeo.marker.Line(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        ))]

    flight_paths = []
    for index, row in df.head(1000).iterrows():    
        flight_paths.append(
            go.Scattergeo(
                lat = [row['COORD_O_X'], row['COORD_D_X']],
                lon = [row['COORD_O_Y'], row['COORD_D_Y']],
                mode = 'lines',
                line = go.scattergeo.Line(
                    width = 1,
                    color = 'red',
                ),
                opacity = 1,
            )
        )

    layout = go.Layout(
        title = go.layout.Title(
            text = 'Feb. 2011 American Airline flight paths<br>(Hover for airport names)'
        ),
        showlegend = False,
        geo = go.layout.Geo(
            scope = 'south america',
            projection = go.layout.geo.Projection(type = 'azimuthal equal area'),
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
        ),
    )

    fig = go.Figure(data = flight_paths + airports, layout = layout)
    py.plot(fig, filename = 'd3-flight-paths')

if __name__ == '__main__':
    main()
