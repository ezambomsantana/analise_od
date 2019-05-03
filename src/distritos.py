import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv

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

    df = data07[['ZONA_O', 'ZONA_D', 'FE_VIA']].dropna()
    df['ZONA_O'] = df['ZONA_O'].apply(lambda x: mydict[x])
    df['ZONA_D'] = df['ZONA_D'].apply(lambda x: mydict[x])
    df[['FE_VIA','float']] = df['FE_VIA'].str.split('.',expand=True)
    df["FE_VIA"] = df["FE_VIA"].astype(int)

    conj = df.groupby(['ZONA_O','ZONA_D']).sum().sort_values(by=['FE_VIA']).reset_index()
    conj = conj[conj['ZONA_O'] != conj['ZONA_D']]
    print (conj.to_csv('teste.csv'))

    viagens_tipo(conj, 'ZONA_O')

def viagens_tipo(data, name):
    conj = data[[name, 'FE_VIA']].groupby([name]).sum().sort_values(by=['FE_VIA']).reset_index()
    conj.columns = [name, 'FE_VIA']
    conj.tail(10).plot.bar(x=name, y='FE_VIA')
    plt.savefig(folder + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()    


if __name__ == '__main__':
    main()


