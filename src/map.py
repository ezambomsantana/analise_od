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


folder_images_maps = "../images/"
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

zonas_teste = zonas[zonas['NumeroMuni'] == 36]

folder_data = "../data/"
arq17 = "dados17.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])

data17 = data17.drop(['ID_DOM', 'FE_DOM', 'VIA_BICI','TP_ESTBICI','F_FAM','FE_FAM','FAMILIA','NO_MORAF',
                      'CONDMORA','QT_BANHO','QT_EMPRE','QT_AUTO','QT_MICRO','QT_LAVALOU','QT_GEL1'], axis=1)

data17['DISTANCE'] = 0

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

modos17 = {0:'Other',1:'Work',2:'Work',3:'Work',4:'School',5:'Shopping',6:'Health',7:'Entertainment', 8:'House',9:'Seek Employment', 10: 'Personal Issues', 11:'Food'}
data17['MOTIVO_D'] = data17['MOTIVO_D'].replace(modos17)

data17 = data17[data17['MOTIVO_D'] == 'Health']

data17 = calculate_weighted_mean(data17)

def load_districts(vehicle, orde):

    data17_copy = data17

    if vehicle != "0":
        vehicles = vehicle.split(",")
        vehicles_int = []
        for v in vehicles:
            vehicles_int.append(int(v))
        data17_copy = data17_copy[data17_copy['MODOPRIN'].isin(vehicles_int)] 
    
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

    data_dur = data17_copy[[orde, 'DURACAO']].groupby([orde]).mean().sort_values(by=['DURACAO']).reset_index()
    data_dur = data_dur.set_index(orde)

    df = mapa.set_index('NomeDistri').join(data_dur).join(data_mp).join(data_mp2).join(data_renda).join(data_trans).join(data_mp_dist)
    df['MEDIA'] = df['MP'] / df['FE_VIA']
    df['MEDIA_DIST'] = df['MP_DIST'] / df['FE_VIA']
    df = df.reset_index()

    df = df.drop(['NumeroDist', 'Area_ha'], axis=1)

    return df


teste = load_districts("0", "ZONA_O")
teste2 = teste.to_crs({'init': 'epsg:3857'})

teste2['area'] = teste2['geometry'].area / 10**6
teste2['indice'] = teste['FE_VIA'] / teste2['area']

cmap = mpl.cm.OrRd(np.linspace(0,1,20))
cmap = mpl.colors.ListedColormap(cmap[10:,:-1])

fig, ax = plt.subplots(1, 1)
teste2.plot(column='indice', ax=ax, legend=True, cmap=cmap)

plt.axis('off')
plt.savefig(folder_images_maps + 'quantidade_bike.png', bbox_inches='tight', pad_inches=0.0)





fig, ax = plt.subplots(1, 1)
teste2.plot(column='DURACAO', ax=ax, legend=True, cmap=cmap)

plt.axis('off')
plt.savefig(folder_images_maps + 'duracao_viagem_saude.png', bbox_inches='tight', pad_inches=0.0)







flows = pd.read_csv("../data/flows.csv", encoding='latin-1')
lines = []
viagens = []

flows = flows.set_index('index')

flows = flows.join(data17, lsuffix='_left', rsuffix='_right')

distri = flows[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).sum().sort_values(by=['FE_VIA']).reset_index()
distri.columns = ['NOME_O', 'FE_VIA_CARRO']
distri = distri.set_index('NOME_O')
distri['FE_VIA_CARRO'] = distri['FE_VIA_CARRO'].astype(int)
distri.columns = ['Viagens']

distri = mapa.set_index('NomeDistri').join(distri)
fig, ax = plt.subplots(1, 1)

distri2 = distri.to_crs({'init': 'epsg:3857'})

distri2['area'] = distri2['geometry'].area / 10**6
distri2['indice'] = distri2['Viagens'] / distri2['area']



distri2.plot(column='indice', ax=ax, legend=True, cmap=cmap)

plt.axis('off')
plt.savefig(folder_images_maps + 'quantidade_bike_potencial.png', bbox_inches='tight', pad_inches=0.0)

teste = teste.fillna(0)
distri = distri.fillna(0)

teste = teste.set_index('index').join(distri[['Viagens']], lsuffix='_left', rsuffix='_right')
teste['JOIN'] = teste['Viagens'] - teste['FE_VIA']

print(teste['JOIN'])
teste['JOIN'] = teste['JOIN'].clip(lower=0)
print(teste['JOIN'])

teste2 = teste.to_crs({'init': 'epsg:3857'})

teste2['area'] = teste2['geometry'].area / 10**6
teste2['indice'] = teste2['JOIN'] / teste2['area']

fig, ax = plt.subplots(1, 1)
teste2.plot(column='indice', ax=ax, legend=True, cmap=cmap)

plt.axis('off')
plt.savefig(folder_images_maps + 'quantidade_bike_join.png', bbox_inches='tight', pad_inches=0.0)