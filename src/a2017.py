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

    data17 = pd.read_csv(folder_data + arq17, dtype={'ZONA_O': str, 'ZONA_D': str, 'FE_VIA':str}, header=0,delimiter=";", low_memory=False) 

    csv_file = folder_data + "regioes17.csv"
    mydict = []
    with open(csv_file, mode='r') as infile:
        reader = csv.reader(infile, delimiter=";")
        mydict = {rows[0]:rows[1] for rows in reader}

    data17['NOME_O'] = data17['ZONA_O'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    data17['NOME_D'] = data17['ZONA_D'].apply(lambda x: '' if pd.isnull(x) else mydict[x])
    
    modos87 = {0:'outros',1:'onibus',2:'onibus',3:'fretado',4:'escolar',5:'carro-dirigindo',6:'carro-passageiro', 7:'taxi',8:'onibus',9:'metro', 10:'trem',11:'moto', 12:'bicicleta', 13:'pe', 14:'caminhao',15:'outros'}
    modos97 = {0:'outros',1:'onibus',2:'fretado',3:'escolar',4:'carro-dirigindo',5:'carro-passageiro',6:'taxi',7:'onibus',8:'metro', 9:'trem',10:'moto', 11:'bicicleta', 12:'pe',13:'outros'}
    modos07 = {0:'outros',1:'onibus',2:'onibus',3:'onibus',4:'fretado',5:'escolar',6:'carro-dirigindo',7:'carro-passageiro', 8:'taxi',9:'onibus', 10:'onibus',11:'onibus', 12:'metro', 13:'trem', 14:'moto',15:'bicicleta', 16:'pe', 17:'outros'}
    modos17 = {0:'outros',1:'metro',2:'trem',3:'metro',4:'onibus',5:'onibus',6:'onibus',7:'fretado', 8:'escolar',9:'carro-dirigindo', 10: 'carro-passageiro', 11:'taxi', 12:'taxi-nao-convencional', 13:'moto', 14:'moto-passageiro', 15:'bicicleta', 16:'pe', 17: 'outros'}
    
    order_neighborhood(data17, modos17,'publico')
    order_neighborhood(data17, modos17,'privado')

def calculate_weighted_mean(data):
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if math.isnan(x) else x)
    data['FE_VIA'] = data['FE_VIA'].apply(lambda x: 1 if int(x) == 0 else x)
    data['MP'] = data['FE_VIA'] * data['DURACAO']
    return data

def order_neighborhood(data17, modos17, tipo):
  data17 = calculate_weighted_mean(data17)
  print(data17)


if __name__ == '__main__':
    main()
