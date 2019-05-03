import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

folder = "/home/eduardo/dev/analise_od/src/"
arq87 = "dados87.csv"
arq97 = "dados97.csv"
arq07 = "dados07.csv"

def main():

    global folder

    data87 = pd.read_csv(folder + arq87, dtype=None, header=0,delimiter=";", low_memory=False) 
    data97 = pd.read_csv(folder + arq97, dtype=None, header=0,delimiter=";", low_memory=False) 
    data07 = pd.read_csv(folder + arq07, dtype=None, header=0,delimiter=";", low_memory=False) 

    num_trips(data87, data97, data07)

    transporte_2007 = [1, 9 , 12, 13]
    transporte_1997 = [1, 7 , 8, 9]
    transporte_1987 = [1, 2, 3, 9, 9 , 10]

    data_morning_sp87 = filter_data(data87, 'MUNIORIG', 'MUNIORIG', 1, transporte_1987)
    data_morning_sp97 = filter_data(data97, 'MUNIORIG', 'MUNIORIG', 36, transporte_1997)
    data_morning_sp07 = filter_data(data07, 'MUNI_O', 'MUNI_D', 36, transporte_2007)
        
    medias87 = get_medias(data_morning_sp87)
    medias97 = get_medias(data_morning_sp97)
    medias07 = get_medias(data_morning_sp07)

    save_violin_plot(medias87, 'publico87.png')
    save_violin_plot(medias97, 'publico97.png')
    save_violin_plot(medias07, 'publico07.png')

    modos87 = {0:'outros',1:'onibus',2:'onibus',3:'onibus',8:'onibus',4:'escolar',5:'carro',7:'taxi',9:'metro', 10:'trem',11:'moto', 12:'bicicleta', 14:'outros', 13:'pe',15:'outros', 6:'carro'}
    modos97 = {0:'outros',1:'onibus',2:'onibus',3:'escolar',7:'onibus',4:'carro',5:'carro',6:'taxi',8:'metro', 9:'trem',10:'moto', 11:'bicicleta', 14:'outros', 12:'pe',15:'outros', 13:'carro'}
    modos07 = {0:'outros',1:'onibus',2:'onibus',3:'onibus',4:'onibus',5:'escolar',6:'carro',7:'carro', 8:'taxi',9:'onibus', 10:'onibus',11:'onibus', 12:'metro', 13:'trem', 14:'moto',15:'bicicleta', 16:'pe'}
    
    get_times_by_modoprin(data87, modos87, 'tempo87.png')
    get_times_by_modoprin(data97, modos97, 'tempo97.png')
    get_times_by_modoprin(data07, modos07, 'tempo07.png')

    viagens_tipo(data87, 'viagens_modo87.png')
    viagens_tipo(data97, 'viagens_modo97.png')
    viagens_tipo(data07, 'viagens_modo07.png')

    tipo_viagem(data87,data97,data07)

        
def tipo_viagem(data87, data97, data07):
  conj87 = data87[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj87.columns = ['MODOPRIN', 'FE_VIA']
  conj87 = conj87.set_index('MODOPRIN')

  conj97 = data97[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj97.columns = ['MODOPRIN', 'FE_VIA']
  conj97 = conj97.set_index('MODOPRIN')

  conj07 = data07[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
  conj07.columns = ['MODOPRIN', 'FE_VIA']
  conj07 = conj07.set_index('MODOPRIN')

  novo = pd.concat([conj87['FE_VIA'], conj97['FE_VIA'], conj07['FE_VIA']], axis=1, keys=['1987', '1997','2007'])
  novo.plot( y=["1987", "1997", "2007"], kind="bar")
  plt.savefig(folder + 'numero_transporte.png', bbox_inches='tight', pad_inches=0.0)
  plt.close()
    

def viagens_tipo(data, name):
    conj = data[['MODOPRIN', 'FE_VIA']].groupby(['MODOPRIN']).sum().sort_values(by=['FE_VIA']).reset_index()
    conj.columns = ['MODOPRIN', 'FE_VIA']
    conj.plot.bar(x='MODOPRIN', y='FE_VIA')
    plt.savefig(folder + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()

def get_times_by_modoprin(data, modos, name):
    data['MODOPRIN'] = data['MODOPRIN'].replace(modos)

    individual = data[data['MODOPRIN'].isin(['carro','moto','bicicleta','taxi','pe'])] 
    publico = data[data['MODOPRIN'].isin(['onibus','trem','metro','escolar'])] 

    sns.violinplot(x="MODOPRIN", y="DURACAO", data=individual, palette="muted")
    plt.savefig(folder + 'individual_' + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()
    
    sns.violinplot(x="MODOPRIN", y="DURACAO", data=publico, palette="muted")
    plt.savefig(folder + 'publico_' + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()
    
def num_trips(data87, data97, data07):
    trips = {'year': ['1987','1997','2007'], 'trips': [data87['FE_VIA'].sum(),data97['FE_VIA'].sum(),data07['FE_VIA'].sum()]}
    teste = pd.DataFrame.from_dict(trips, orient='index').transpose()
    teste.plot.bar(x='year', y='trips')
    plt.xlabel('Ano da Pesquisa')
    plt.ylabel('Numero de Viagens')
    plt.savefig(folder + 'total_viagens_od.png', bbox_inches='tight', pad_inches=0.0)
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
    plt.savefig(folder + nome, bbox_inches='tight', pad_inches=0.0)
    plt.close()


if __name__ == '__main__':
    main()
