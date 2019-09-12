import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import numpy as np
import math
import csv

folder_data = "/home/eduardo/dev/analise_od/data/"
folder_images = "/home/eduardo/dev/analise_od/images/"
arq87 = "dados87.csv"
arq97 = "dados97.csv"
arq07 = "dados07.csv"
arq17 = "dados17.csv"

def main():

    global folder_data
    global folder_images

    data87 = pd.read_csv(folder_data + arq87, dtype=None, header=0,delimiter=";", low_memory=False) 
    data97 = pd.read_csv(folder_data + arq97, dtype=None, header=0,delimiter=";", low_memory=False) 
    data07 = pd.read_csv(folder_data + arq07, dtype=None, header=0,delimiter=";", low_memory=False) 
    data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str}, header=0,delimiter=";", low_memory=False) 

    csv_file = folder_data + "regioes17.csv"
    mydict = []
    with open(csv_file, mode='r') as infile:
        reader = csv.reader(infile, delimiter=";")
        mydict = {rows[0]:rows[1] for rows in reader}

    data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    
    num_trips(data87, data97, data07, data17)

    transporte_2017 = [1, 2, 3, 4, 5, 6, 8]
    transporte_2007 = [1, 9 , 12, 13]
    transporte_1997 = [1, 7 , 8, 9]
    transporte_1987 = [1, 2, 3, 9, 9 , 10]

    data_morning_sp87 = filter_data(data87, 'MUNIORIG', 'MUNIORIG', 1, transporte_1987)
    data_morning_sp97 = filter_data(data97, 'MUNIORIG', 'MUNIORIG', 36, transporte_1997)
    data_morning_sp07 = filter_data(data07, 'MUNI_O', 'MUNI_D', 36, transporte_2007)
    data_morning_sp17 = filter_data(data17, 'MUNI_O', 'MUNI_D', 36, transporte_2017)
        
    medias87 = get_medias(data_morning_sp87)
    medias97 = get_medias(data_morning_sp97)
    medias07 = get_medias(data_morning_sp07)
    medias17 = get_medias(data_morning_sp17)

    save_violin_plot(medias87, 'publico87.png')
    save_violin_plot(medias97, 'publico97.png')
    save_violin_plot(medias07, 'publico07.png')
    save_violin_plot(medias17, 'publico17.png')

    modos87 = {0:'outros',1:'onibus',2:'onibus',3:'fretado',4:'escolar',5:'carro-dirigindo',6:'carro-passageiro', 7:'taxi',8:'onibus',9:'metro', 10:'trem',11:'moto', 12:'bicicleta', 13:'pe', 14:'caminhao',15:'outros'}
    modos97 = {0:'outros',1:'onibus',2:'fretado',3:'escolar',4:'carro-dirigindo',5:'carro-passageiro',6:'taxi',7:'onibus',8:'metro', 9:'trem',10:'moto', 11:'bicicleta', 12:'pe',13:'outros'}
    modos07 = {0:'outros',1:'onibus',2:'onibus',3:'onibus',4:'fretado',5:'escolar',6:'carro-dirigindo',7:'carro-passageiro', 8:'taxi',9:'onibus', 10:'onibus',11:'onibus', 12:'metro', 13:'trem', 14:'moto',15:'bicicleta', 16:'pe', 17:'outros'}
    modos17 = {0:'outros',1:'metro',2:'trem',3:'metro',4:'onibus',5:'onibus',6:'onibus',7:'fretado', 8:'escolar',9:'carro-dirigindo', 10: 'carro-passageiro', 11:'taxi', 12:'taxi-nao-convencional', 13:'moto', 14:'moto-passageiro', 15:'bicicleta', 16:'pe', 17: 'outros'}
    
    mean_travel_time(data87, data97, data07, data17, modos87, modos97, modos07, modos17, ['onibus','trem','metro','escolar'],'publico')
    mean_travel_time(data87, data97, data07, data17, modos87, modos97, modos07, modos17, ['carro-dirigindo','moto','bicicleta','taxi','pe'],'privado')

    order_neighborhood(data17, modos17, ['onibus','trem','metro'], ['carro-dirigindo','moto','bicicleta','taxi'])

    get_times_by_modoprin(data87, modos87, 'tempo87.png')
    get_times_by_modoprin(data97, modos97, 'tempo97.png')
    get_times_by_modoprin(data07, modos07, 'tempo07.png')
    get_times_by_modoprin(data17, modos17, 'tempo17.png')

    viagens_tipo(data87, 'viagens_modo87.png')
    viagens_tipo(data97, 'viagens_modo97.png')
    viagens_tipo(data07, 'viagens_modo07.png')
    viagens_tipo(data17, 'viagens_modo17.png')

    tipo_viagem(data87,data97,data07,data17)


def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    return data

def order_neighborhood(data17, modos17, publico, privado):

  data17 = data17[data17['MUNI_O'] == 36] 
  data17 = data17[data17['MUNI_D'] == 36] 
    
  data17 = data17[data17['H_SAIDA'] >= 6 ]
  data17 = data17[data17['H_SAIDA'] <= 9]

  data17 = data17[data17['MOTIVO_O'].isin([8])]
  data17 = data17[data17['MOTIVO_D'].isin([1,2,3])]
  
  data17 = calculate_weighted_mean(data17)

  data17['MODOPRIN'] = data17['MODOPRIN'].replace(modos17)

  data17_publico = data17[data17['MODOPRIN'].isin(publico)] 
  data17_privado = data17[data17['MODOPRIN'].isin(privado)] 

  tudo = data17[data17['MODOPRIN'].isin(publico + privado)] 

  calculate_corr(tudo, 'publico')
#  calculate_corr(data17_privado, 'privado')
 # calculate_corr(tudo, 'tudo')

def calculate_corr(data, type):

  data_mp = data[['NOME_O', 'MP']].groupby(['NOME_O']).sum().sort_values(by=['MP']).reset_index()
  data_mp = data_mp.set_index('NOME_O')

  data_fe = data[['NOME_O', 'FE_VIA']].groupby(['NOME_O']).sum().sort_values(by=['FE_VIA']).reset_index()
  data_fe = data_fe.set_index('NOME_O')

  data_renda = data[['NOME_O', 'RENDA_FA']].groupby(['NOME_O']).mean().sort_values(by=['RENDA_FA']).reset_index()
  data_renda = data_renda.set_index('NOME_O')

  data_inst = data[['NOME_O', 'DURACAO']].groupby(['NOME_O']).mean().sort_values(by=['DURACAO']).reset_index()
  data_inst = data_inst.set_index('NOME_O')

  df_row = data_mp.join(data_fe).join(data_renda).join(data_inst)
  df_row['MEDIA'] = df_row['MP'] / df_row['FE_VIA']

  print(df_row.sort_values(by=['RENDA_FA']))

  print(df_row.corr(method ='pearson'))


def mean_travel_time(data87, data97, data07, data17, modos87, modos97, modos07, modos17, tipos, tipo):

  data87 = calculate_weighted_mean(data87)
  data97 = calculate_weighted_mean(data97)
  data07 = calculate_weighted_mean(data07)
  data17 = calculate_weighted_mean(data17)

  data87['MODOPRIN'] = data87['MODOPRIN'].replace(modos87)
  data97['MODOPRIN'] = data97['MODOPRIN'].replace(modos97)
  data07['MODOPRIN'] = data07['MODOPRIN'].replace(modos07)
  data17['MODOPRIN'] = data17['MODOPRIN'].replace(modos17)

  fig, ax = plt.subplots()
  data87_2 = data87[data87['MODOPRIN'].isin(tipos)] 
  data97_2 = data97[data97['MODOPRIN'].isin(tipos)] 
  data07_2 = data07[data07['MODOPRIN'].isin(tipos)] 
  data17_2 = data17[data17['MODOPRIN'].isin(tipos)] 

  dataFinal = [
    ['87', data87_2['MP'].sum() / data87_2['FE_VIA'].sum()], 
    ['97', data97_2['MP'].sum() / data97_2['FE_VIA'].sum()], 
    ['07', data07_2['MP'].sum() / data07_2['FE_VIA'].sum()], 
    ['17', data17_2['MP'].sum() / data17_2['FE_VIA'].sum()]
  ]

  df = pd.DataFrame(dataFinal, columns = ['ano', 'mean_travel']) 
  ax = df.plot(ax = ax,
    x='ano',
    y='mean_travel',
    marker='o', 
    title='Travel time (s) vs. DR ratio (%)',
    grid=True,
  )

  for x in tipos:

    data87_2 = data87[data87['MODOPRIN'].isin([x])] 
    data97_2 = data97[data97['MODOPRIN'].isin([x])] 
    data07_2 = data07[data07['MODOPRIN'].isin([x])] 
    data17_2 = data17[data17['MODOPRIN'].isin([x])] 

    dataFinal = [
      ['87', data87_2['MP'].sum() / data87_2['FE_VIA'].sum()], 
      ['97', data97_2['MP'].sum() / data97_2['FE_VIA'].sum()], 
      ['07', data07_2['MP'].sum() / data07_2['FE_VIA'].sum()], 
      ['17', data17_2['MP'].sum() / data17_2['FE_VIA'].sum()]
    ]

    df = pd.DataFrame(dataFinal, columns = ['ano', 'mean_travel']) 

    ax = df.plot(ax = ax,
        x='ano',
        y='mean_travel',
        marker='o', 
        grid=True,
    )
  ax.set_title('Tempo de viagem por tipo de transporte')
  ax.legend(['geral'] + tipos)
  plt.savefig(folder_images + tipo + '_tempo_tipo_transporte.png', bbox_inches='tight', pad_inches=0.0)
  plt.close()
        
def tipo_viagem(data87, data97, data07, data17):
  conj87 = data87[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj87.columns = ['MODOPRIN', 'FE_VIA']
  conj87 = conj87.set_index('MODOPRIN')

  conj97 = data97[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj97.columns = ['MODOPRIN', 'FE_VIA']
  conj97 = conj97.set_index('MODOPRIN')

  conj07 = data07[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj07.columns = ['MODOPRIN', 'FE_VIA']
  conj07 = conj07.set_index('MODOPRIN')

  conj17 = data17[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj17.columns = ['MODOPRIN', 'FE_VIA']
  conj17 = conj17.set_index('MODOPRIN')

  novo = pd.concat([conj87['FE_VIA'], conj97['FE_VIA'], conj07['FE_VIA'], conj17['FE_VIA']], axis=1, keys=['1987', '1997','2007', '2017'])
  novo.plot( y=["1987", "1997", "2007", "2017"], kind="bar")
  plt.savefig(folder_images + 'numero_transporte.png', bbox_inches='tight', pad_inches=0.0)
  plt.close()
    

def viagens_tipo(data, name):
    conj = data[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
    conj.columns = ['MODOPRIN', 'FE_VIA']
    conj.plot.bar(x='MODOPRIN', y='FE_VIA')
    plt.savefig(folder_images + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()

def get_times_by_modoprin(data, modos, name):
    data['MODOPRIN'] = data['MODOPRIN'].replace(modos)

    individual = data[data['MODOPRIN'].isin(['carro-dirigindo','moto','bicicleta','taxi','pe'])] 
    publico = data[data['MODOPRIN'].isin(['onibus','trem','metro','escolar'])] 

    individual = individual.sort_values(by=['MODOPRIN'])
    publico = publico.sort_values(by=['MODOPRIN'])

    sns.violinplot(x="MODOPRIN", y="DURACAO", data=individual, palette="muted")
    plt.savefig(folder_images + 'individual_' + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()
    
    sns.violinplot(x="MODOPRIN", y="DURACAO", data=publico, palette="muted")
    plt.savefig(folder_images + 'publico_' + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()
    
def num_trips(data87, data97, data07, data17):
    trips = {'year': ['1987','1997','2007', '2017'], 'trips': [data87['FE_VIA'].sum(),data97['FE_VIA'].sum(),data07['FE_VIA'].sum(), data17['FE_VIA'].sum()]}
    teste = pd.DataFrame.from_dict(trips, orient='index').transpose()
    teste.plot.bar(x='year', y='trips')
    plt.xlabel('Ano da Pesquisa')
    plt.ylabel('Numero de Viagens')
    plt.savefig(folder_images + 'total_viagens_od.png', bbox_inches='tight', pad_inches=0.0)
    plt.close()

def filter_data(data, cod_origin, cod_destination, id_city, array_transportation):

    data = data[data[cod_origin] == id_city] 
    data = data[data[cod_destination] == id_city] 
    
    data = data[data['MODOPRIN'].isin(array_transportation)]  # trans. publico

    data_manha = data[data['H_SAIDA'] >= 6 ]
    data_manha = data_manha[data_manha['H_SAIDA'] <= 9]
    return data_manha

def get_medias(data):
    medias = data[['ZONA_O', 'DURACAO']].groupby(['ZONA_O']).mean().sort_values(by=['DURACAO'])
    m = medias.head(20).reset_index()['ZONA_O'].tolist()
    p = medias.tail(20).reset_index()['ZONA_O'].tolist()

    melhores = data[data['ZONA_O'].isin(m)]
    piores = data[data['ZONA_O'].isin(p)]
    
    teste = {'Menores':melhores['DURACAO'].tolist(),'Maiores':piores['DURACAO'].tolist(), 'Geral':data['DURACAO'].tolist()}
    teste = pd.DataFrame.from_dict(teste, orient='index').transpose()
    return teste

def save_violin_plot(data, nome):
    sns.violinplot(data=data, alpha=0.5)
    plt.xlabel('Tipo de Distrito: Distritos com menores medias, maiores medias e a media geral da cidade')
    plt.ylabel('Tempo de viagem')
    plt.savefig(folder_images + nome, bbox_inches='tight', pad_inches=0.0)
    plt.close()


if __name__ == '__main__':
    main()
