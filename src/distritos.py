import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv
import networkx as nx

import sys  

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
            dict_pos[row['ZONA_O']] = [row['CO_O_X'], row['CO_O_Y']]
        if row['ZONA_D'] not in dict_pos:
            dict_pos[row['ZONA_D']] = [row['CO_D_X'], row['CO_D_Y']]


    data07['COORD_O'] = data07['ZONA_O'].apply(lambda x: dict_pos[x])
    data07['COORD_D'] = data07['ZONA_D'].apply(lambda x: dict_pos[x])

    df = data07[['ZONA_O', 'ZONA_D', 'COORD_O', 'COORD_D', 'FE_VIA']].dropna()

    print(df)

    df[['FE_VIA','float']] = df['FE_VIA'].str.split('.',expand=True)
    df["FE_VIA"] = df["FE_VIA"].astype(int)

    conj = df.groupby(['ZONA_O','ZONA_D']).sum().sort_values(by=['FE_VIA']).reset_index()
    conj2 = conj[conj['ZONA_O'] != conj['ZONA_D']]
    print (conj2.to_csv('teste.csv'))

    viagens_tipo(conj, 'ZONA_O')
    print(conj2['FE_VIA'].sum())

    conj2 = conj[conj['ZONA_O'] == conj['ZONA_D']]
    print(conj2['FE_VIA'].sum())

    G = nx.Graph()
    for x in conj['ZONA_O']:
        G.add_node(x)

    for index, row in conj.iterrows():    
        o = row['ZONA_O']
        d = row['ZONA_D']
        G.add_edge(o, d)

    pos = nx.nx_agraph.graphviz_layout(G)
    nx.draw_circular(G)
    plt.savefig("path.png")

def viagens_tipo(data, name):
    conj = data[[name, 'FE_VIA']].groupby([name]).sum().sort_values(by=['FE_VIA']).reset_index()
    conj.columns = [name, 'FE_VIA']
    conj.tail(10).plot.bar(x=name, y='FE_VIA')
    plt.savefig(folder + name, bbox_inches='tight', pad_inches=0.0)
    plt.close()    


if __name__ == '__main__':
    main()


