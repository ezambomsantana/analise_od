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


folder_images_maps = "../../images/"
def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    data['MP_DIST'] = data['FE_VIA'] * data['DISTANCE']
    return data

mapa = gpd.GeoDataFrame.from_file("../../data/shapes/Distritos_2017_region.shp", encoding='latin-1')
mapa = mapa.to_crs({"init": "epsg:4326"})
mapa['NomeDistri'] = mapa['NomeDistri'].apply(lambda x: unidecode.unidecode(x))

mapa = mapa[mapa['NumeroDist'] <=96]
print(mapa)

zonas = gpd.GeoDataFrame.from_file("../../data/shapes/Zonas_2017_region.shp", encoding='latin-1')
zonas = zonas.to_crs({"init": "epsg:4326"}) 
zonas['NomeDistri'] = zonas['NomeDistri'].apply(lambda x: unidecode.unidecode(x))
zonas['NomeZona'] = zonas['NomeZona'].apply(lambda x: unidecode.unidecode(x))

zonas_teste = zonas[zonas['NumeroMuni'] == 36]

print(zonas_teste['NumDistrit'].unique())

folder_data = "../../data/"
arq17 = "dados17.csv"

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])

data17 = data17.drop(['ID_DOM', 'FE_DOM', 'VIA_BICI','TP_ESTBICI','F_FAM','FE_FAM','FAMILIA','NO_MORAF',
                      'CONDMORA','QT_BANHO','QT_EMPRE','QT_AUTO','QT_MICRO','QT_LAVALOU','QT_GEL1'], axis=1)

data17['DISTANCE'] = 0

data17 = data17[data17['MODOPRIN'] == 15]

print(data17['FE_VIA'].sum())

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

    df = mapa.set_index('NomeDistri').join(data_mp).join(data_mp2).join(data_renda).join(data_trans).join(data_mp_dist)
    df['MEDIA'] = df['MP'] / df['FE_VIA']
    df['MEDIA_DIST'] = df['MP_DIST'] / df['FE_VIA']
    df = df.reset_index()

    df = df.drop(['NumeroDist', 'Area_ha'], axis=1)

    return df


teste = load_districts("15", "NOME_D")


cmap = mpl.cm.Blues(np.linspace(0,1,20))
cmap = mpl.colors.ListedColormap(cmap[10:,:-1])

print(teste)

fig, ax = plt.subplots(1, 1)
teste.plot(column='FE_VIA', ax=ax, legend=True, cmap=cmap)

plt.axis('off')
plt.savefig(folder_images_maps + 'quantidade_bike.png', bbox_inches='tight', pad_inches=0.0)