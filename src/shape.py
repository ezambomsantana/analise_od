# -*- coding: utf-8 -*-
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import csv
import unidecode
import math
import seaborn as sns
import geopy.distance

coords_1 = (52.2296756, 21.0122287)
coords_2 = (52.406374, 16.9251681)


def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    return data

folder_data = "/home/eduardo/dev/analise_od/data/"
folder_images_maps = "/home/eduardo/dev/analise_od/images/maps/"
arq17 = "dados17.csv"

mapa = gpd.GeoDataFrame.from_file("/home/eduardo/Distritos_2017_region.shp", encoding='latin-1')
metro = gpd.GeoDataFrame.from_file("/home/eduardo/SIRGAS_SHP_linhametro_line.shp", encoding='latin-1')

data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str, 'CO_O_X': float, 'CO_O_Y': float, 'CO_D_X': float, 'CO_D_Y': float}, header=0,delimiter=";", low_memory=False) 
data17 = data17.dropna(subset=['CO_O_X'])
print(data17['CO_O_X'])

csv_file = folder_data + "regioes17.csv"
mydict = []
with open(csv_file, mode='r') as infile:
    reader = csv.reader(infile, delimiter=";")
    mydict = {rows[0]:rows[1] for rows in reader}

data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
data17['NUM_TRANS'] = data17[['MODO1', 'MODO2','MODO3','MODO4']].count(axis=1)

data17 = calculate_weighted_mean(data17)

modos17 = {0:'outros',1:'metro',2:'trem',3:'metro',4:'onibus',5:'onibus',6:'onibus',7:'fretado', 8:'escolar',9:'carro-dirigindo', 10: 'carro-passageiro', 11:'taxi', 12:'taxi-nao-convencional', 13:'moto', 14:'moto-passageiro', 15:'bicicleta', 16:'pe', 17: 'outros'}
  
coletivo = ['onibus','trem','metro']
privado = ['carro-dirigindo','moto','bicicleta','taxi']

motorizado = ['onibus','trem','metro', 'carro-dirigindo','moto','taxi']
nao_motorizado = ['bicicleta', 'pe']

data17['MODOPRIN'] = data17['MODOPRIN'].replace(modos17)
data17 = data17[data17['MODOPRIN'].isin(coletivo + privado)] 

data17 = data17[data17['H_SAIDA'] >= 5]
data17 = data17[data17['H_SAIDA'] <= 10]

data_mp2 = data17[['NOME_O',  'MP']].groupby(['NOME_O']).sum().sort_values(by=['MP']).reset_index()
data_mp2 = data_mp2.set_index('NOME_O')

data_mp = data17[['NOME_O', 'MUNI_O', 'FE_VIA']].groupby(['NOME_O','MUNI_O']).sum().sort_values(by=['NOME_O']).reset_index()
data_mp = data_mp.set_index('NOME_O')
mapa['NomeDistri'] = mapa['NomeDistri'].apply(lambda x: unidecode.unidecode(x))

data_renda = data17[['NOME_O', 'RENDA_FA']].groupby(['NOME_O']).mean().sort_values(by=['RENDA_FA']).reset_index()
data_renda = data_renda.set_index('NOME_O')

data_trans = data17[['NOME_O', 'NUM_TRANS']].groupby(['NOME_O']).mean().sort_values(by=['NUM_TRANS']).reset_index()
data_trans = data_trans.set_index('NOME_O')

df = mapa.set_index('NomeDistri').join(data_mp).join(data_mp2).join(data_renda).join(data_trans)
df['MEDIA'] = df['MP'] / df['FE_VIA']

df = df[df['MUNI_O'] == 36]

fig, ax = plt.subplots(1, 1)

df.plot(column='MEDIA', ax=ax, legend=True, cmap='OrRd')
metro.plot(ax=ax, color='blue')
plt.savefig(folder_images_maps + 'tempo.png', bbox_inches='tight', pad_inches=0.0)

plt.clf()

fig, ax = plt.subplots(1, 1)

df.plot(column='NUM_TRANS', ax=ax, legend=True, cmap='OrRd')
metro.plot(ax=ax, color='blue')
plt.savefig(folder_images_maps + 'num_integracoes.png', bbox_inches='tight', pad_inches=0.0)

plt.clf()

ax = sns.regplot(x="MEDIA", y="RENDA_FA", data=df, lowess=True)
plt.savefig(folder_images_maps + 'scatter_renda_tempo.png', bbox_inches='tight', pad_inches=0.0)

plt.clf()

data17_coletivo = data17[data17['MODOPRIN'].isin(coletivo)] 
data17_privado = data17[data17['MODOPRIN'].isin(privado)] 

data17_coletivo = data17_coletivo[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).mean().sort_values(by=['FE_VIA']).reset_index()
data17_coletivo = data17_coletivo.set_index('NOME_O')

data17_privado = data17_privado[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).mean().sort_values(by=['FE_VIA']).reset_index()
data17_privado = data17_privado.set_index('NOME_O')

df = mapa.set_index('NomeDistri').join(data17_coletivo).join(data17_privado,lsuffix='_coletivo', rsuffix='_privado').join(data_mp)
df['por_coletivo'] = df['FE_VIA_coletivo'] / (df['FE_VIA_coletivo'] + df['FE_VIA_privado'])
df['por_privado'] = df['FE_VIA_privado'] / (df['FE_VIA_coletivo'] + df['FE_VIA_privado'])
df = df[df['MUNI_O'] == 36]

fig, ax = plt.subplots(1, 1)
metro.plot(ax=ax, color='blue')
df.plot(column='por_coletivo', ax=ax, legend=True, cmap='OrRd')
plt.savefig(folder_images_maps + 'porcentagem_coletivo.png', bbox_inches='tight', pad_inches=0.0)


fig, ax = plt.subplots(1, 1)
metro.plot(ax=ax, color='blue')
df.plot(column='por_privado', ax=ax, legend=True, cmap='OrRd')
plt.savefig(folder_images_maps + 'porcentagem_privado.png', bbox_inches='tight', pad_inches=0.0)





data17_motorizado = data17[data17['MODOPRIN'].isin(motorizado)] 
data_nao_motorizado = data17[data17['MODOPRIN'].isin(nao_motorizado)] 

data17_motorizado = data17_motorizado[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).mean().sort_values(by=['FE_VIA']).reset_index()
data17_motorizado = data17_motorizado.set_index('NOME_O')

data_nao_motorizado = data_nao_motorizado[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).mean().sort_values(by=['FE_VIA']).reset_index()
data_nao_motorizado = data_nao_motorizado.set_index('NOME_O')

df = mapa.set_index('NomeDistri').join(data17_motorizado).join(data_nao_motorizado,lsuffix='_motorizado', rsuffix='_nao_motorizado').join(data_mp)
df['por_motorizado'] = df['FE_VIA_motorizado'] / (df['FE_VIA_motorizado'] + df['FE_VIA_nao_motorizado'])
df['por_nao_motorizado'] = df['FE_VIA_nao_motorizado'] / (df['FE_VIA_motorizado'] + df['FE_VIA_nao_motorizado'])
df = df[df['MUNI_O'] == 36]

fig, ax = plt.subplots(1, 1)
metro.plot(ax=ax, color='blue')
df.plot(column='por_motorizado', ax=ax, legend=True, cmap='OrRd')
plt.savefig(folder_images_maps + 'porcentagem_motorizado.png', bbox_inches='tight', pad_inches=0.0)

fig, ax = plt.subplots(1, 1)
metro.plot(ax=ax, color='blue')
df.plot(column='por_nao_motorizado', ax=ax, legend=True, cmap='OrRd')
plt.savefig(folder_images_maps + 'porcentagem_nao_motorizado.png', bbox_inches='tight', pad_inches=0.0)