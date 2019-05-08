import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv
import networkx as nx
import utm

import sys  

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import plotly
import mplleaflet



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

    data07['NOME_O'] = data07['ZONA_O'].apply(lambda x: mydict[x])
    data07['NOME_D'] = data07['ZONA_D'].apply(lambda x: mydict[x])


    dict_pos = {}
    for index, row in data07.iterrows():    
        if row['ZONA_O'] not in dict_pos:
            dict_pos[row['ZONA_O']] = utm.to_latlon(row['CO_O_X'], row['CO_O_Y'], 23, 'K')
            dict_pos[row['ZONA_O']] = [dict_pos[row['ZONA_O']][1], dict_pos[row['ZONA_O']][0]]
        if row['ZONA_D'] not in dict_pos:
            dict_pos[row['ZONA_D']] = utm.to_latlon(row['CO_D_X'], row['CO_D_Y'], 23, 'K')
            dict_pos[row['ZONA_D']] = [dict_pos[row['ZONA_D']][1], dict_pos[row['ZONA_D']][0]]


    data07['COORD_O_X'] = data07['ZONA_O'].apply(lambda x: dict_pos[x][0])
    data07['COORD_O_Y'] = data07['ZONA_O'].apply(lambda x: dict_pos[x][1])
    data07['COORD_D_X'] = data07['ZONA_D'].apply(lambda x: dict_pos[x][0])
    data07['COORD_D_Y'] = data07['ZONA_D'].apply(lambda x: dict_pos[x][1])

    df = data07[['ZONA_O', 'ZONA_D', 'COORD_O_X','COORD_O_Y', 'COORD_D_X','COORD_D_Y', 'FE_VIA', 'NOME_O', 'NOME_D']].dropna()


    df[['FE_VIA','float']] = df['FE_VIA'].str.split('.',expand=True)
    df["FE_VIA"] = df["FE_VIA"].astype(int)

    df = df.groupby(['ZONA_O', 'ZONA_D', 'COORD_O_X','COORD_O_Y', 'COORD_D_X','COORD_D_Y', 'NOME_O', 'NOME_D']).sum().sort_values(by=['FE_VIA']).reset_index()
    df = df[df['ZONA_O'] != df['ZONA_D']]

    print(df)

    G = nx.Graph()
    for i, row in df.iterrows():
        G.add_node(row['ZONA_O'])

    for index, row in df.iterrows():    
        o = row['ZONA_O']
        d = row['ZONA_D']
        G.add_edge(o, d)
    
    fig, ax = plt.subplots()

    nx.draw_networkx_nodes(G ,pos=dict_pos,node_size=10,node_color='red',edge_color='k',alpha=.5, with_labels=True)
    nx.draw_networkx_edges(G ,pos=dict_pos,edge_color='gray', alpha=.1)
    nx.draw_networkx_labels(G ,dict_pos, label_pos =10.3)

    mplleaflet.show(fig=ax.figure)


if __name__ == '__main__':
    main()
