from scipy.io import loadmat
from pathlib import Path
import numpy as np
import sys
import matplotlib.pyplot as plt
np.set_printoptions(suppress=True)
#Data sets Structure:
#Uteis
#.dtype.names
#.keys()

#11 - Randown Walk Part 1
# data_9['step']['date'][0][i][0]
# data_9['step'][0][i]['date'][0] <= Usar esse mais robusto

#5 - Battery Data Set - Part 1
#data_5 = loadmat(data_path5)['B0005']['cycle'][0,0]['data'][0,0]['Voltage_measured'][0,0][0]
#data_5 = loadmat(data_path5)['B0005']['cycle'][0,0][0][i]['data'][0,0]['Voltage_measured'][0] <= Usar esse mais robusto

#==================================================================
#Data Set 11
data_path9 = Path("Batery_data")/"11. Randomized Battery Usage Data Set"/"Part 1_Random Walk (caso base)"/"data"/"Matlab"/"RW9.mat"
data_path10 = Path("Batery_data")/"11. Randomized Battery Usage Data Set"/"Part 1_Random Walk (caso base)"/"data"/"Matlab"/"RW10.mat"
data_path11 = Path("Batery_data")/"11. Randomized Battery Usage Data Set"/"Part 1_Random Walk (caso base)"/"data"/"Matlab"/"RW11.mat"
data_path12 = Path("Batery_data")/"11. Randomized Battery Usage Data Set"/"Part 1_Random Walk (caso base)"/"data"/"Matlab"/"RW12.mat"
#==================================================================
#Data Set 5
data_path5 = Path("Batery_data")/"5. Battery Data Set"/"Part 1"/"B0005.mat"
data_path6 = Path("Batery_data")/"5. Battery Data Set"/"Part 1"/"B0006.mat"
data_path7 = Path("Batery_data")/"5. Battery Data Set"/"Part 1"/"B0007.mat"
data_path18 = Path("Batery_data")/"5. Battery Data Set"/"Part 1"/"B0018.mat"

#==================================================================

def Get_data(Cycle: int,Header: str,Path,Bat: str,Campo: str = None):
    """
    Recebe um dicionario com os valores requeridos do data set especificado (5) |
    Cycle => Cyclo especifico a ser acessado |
    Header => Nivel que deseja acessar - data, type, ambient_temperature, time |
    type: 	operation  type, can be charge, discharge or impedance |
	ambient_temperature:	ambient temperature (degree C) |
	time: 	the date and time of the start of the cycle, in MATLAB  date vector format [year, month, day, hour, minute, second]|
	data:	data structure containing the measurements |
    all: retorna toda a estrutura
    Campo => dado especifico a ser acessado (só funciona para data) |
    """
    #loadmat(data_path5)['B0005']['cycle'][0,0][0][Cycle][Header][0,0][Campo][0]
    if Header == 'data' and Campo != None: return loadmat(Path)[Bat]['cycle'][0,0][0][Cycle][Header][0,0][Campo][0]
    elif Header == 'all': return loadmat(Path)[Bat]['cycle'][0,0][0]
    else: return loadmat(Path)[Bat]['cycle'][0,0][0][Cycle][Header][0]

def Get_data_size(Path,Bat: str):
    return len(loadmat(Path)[Bat]['cycle'][0,0][0])

def amostrar_porcentagem_v2(lista, porcentagem):
    n = len(lista)
    num_amostras = max(1, int(round(n * porcentagem)))
    
    if num_amostras >= n:
        return lista.copy()
    
    passo = n / num_amostras
    
    indices = []
    for i in range(num_amostras):
        idx = int(i * passo)
        if idx >= n:
            idx = n - 1
        indices.append(idx)
    
    indices = sorted(set(indices))
    return [lista[i] for i in indices]

def amostrar_qtd_v2(lista, num_amostras):
    n = len(lista)

    if num_amostras >= n:
        return lista.copy()

    passo = n / num_amostras

    indices = []
    for i in range(num_amostras):
        idx = int(i * passo)
        if idx >= n:
            idx = n - 1
        indices.append(idx)

    indices = sorted(set(indices))
    return [lista[i] for i in indices]

#Path_list = [data_path5,data_path6,data_path7,data_path18]
#Path_name = ['B0005','B0006','B0007','B0018']
def ML_data_reciver(Path_list,Path_name,Qnt_data,Qnt_cycles,Black_listed):
    """
    Chame essa função para receber os dados
    para o machine learning
    Path_list => Lista do caminho do arquivo
    Path_name => Nome das Baterias (Talvez seja subistituido em versões futuras)
    Qnt_data => Numero de dados a ser extraido de cada arquivo
    Qnt_cycles => Numero de cyclos a ser extraido de cada arquivo
    """
    p = -1
    Discharge_out_data = {}
    Charge_out_data = {}
    for path in Path_list:
        p+=1
        #Indices de discharge e charge
        Disch_indx = []
        Charge_indx = []
        Imped_indx = []

        #[Cycle][Header][0]
        Data_set = Get_data(0,'all',path,Path_name[p])
        for i in range(Get_data_size(path,Path_name[p])):
            if Data_set[i]['type'][0] == 'discharge': Disch_indx.append(i)
            elif Data_set[i]['type'][0] == 'charge': Charge_indx.append(i)
            elif Data_set[i]['type'][0] == 'impedance': Imped_indx.append(i)

        #Retirar o primeiro/2 ultimo ciclo pois eles não representam o problema
        Disch_indx = Disch_indx[1:-2]
        Charge_indx = Charge_indx[1:-2]
        Imped_indx = Imped_indx[1:-2]

        Disch_indx = amostrar_qtd_v2(Disch_indx,Qnt_cycles)
        Charge_indx = amostrar_qtd_v2(Charge_indx,Qnt_cycles)
        Imped_indx = amostrar_qtd_v2(Imped_indx,Qnt_cycles)

        #Discharge
        data_name = Data_set[Disch_indx[0]]['data'][0,0].dtype.names[0:5]
        Aux_out_data = {}
        for fields in data_name:
            Temp_data = []

            for i in Disch_indx:
                if fields not in Black_listed: Temp_data.append(amostrar_qtd_v2(Data_set[i]['data'][0,0][fields][0],Qnt_data))
            
            if Temp_data != []: Aux_out_data[fields] = np.median(Temp_data, axis=0)

        #Capacity
        fields = Data_set[Disch_indx[0]]['data'][0,0].dtype.names[6]
        Temp_data = []
        for i in Disch_indx:
            if fields not in Black_listed: Temp_data.append(Data_set[i]['data'][0,0][fields][0][0])
        Temp_data = amostrar_qtd_v2(Temp_data,Qnt_data)
        if Temp_data != []: Aux_out_data[fields] = Temp_data.copy()

        Discharge_out_data[Path_name[p]] = Aux_out_data

        #Charge
        data_name = Data_set[Charge_indx[0]]['data'][0,0].dtype.names[0:5]
        Aux_out_data = {}
        for fields in data_name:
            Temp_data = []

            for i in Charge_indx:
                if fields not in Black_listed: Temp_data.append(amostrar_qtd_v2(Data_set[i]['data'][0,0][fields][0],Qnt_data))
            
            if Temp_data != []: Aux_out_data[fields] = np.median(Temp_data, axis=0)
        
        Charge_out_data[Path_name[p]] = Aux_out_data

    return cicle_track(Discharge_out_data,Charge_out_data,Path_name,Qnt_cycles)

    #Para entrar no algoritmo divide em 2 eixos
    #Um eixo contendo os paraemtros, e o eixo y com a capacidade

def flattening(Path_name,Data,data_size,Key_y):

    X_list,y_list=[],[]
    
    #Percorre cada dado
    for name in Path_name:
        data_flattened=Data[0][name]

        columns=list(data_flattened.keys())
        for i in range (data_size):

            cycle_lines=[]

            for keys in columns:
                
                #Preenche a matriz com a linha dos paraemtros e as colunas os vetores (Preenchendo o eixo x)
                if keys!=Key_y:
                    pontos = data_flattened[keys][i]
                    cycle_lines.extend(pontos if isinstance(pontos, (list, tuple)) else [pontos])
        
            #Preenche o eixo y
            X_list.append(cycle_lines)
            y_list.append(data_flattened[Key_y][i])

    #Retorna a matriz (X_list) e o vetor com as capacidades (y_list)
    return [X_list,y_list]


def Max_Min_data(Dados,Path_name,key):
    """
    Retorna o Maximo e o Minimo do conjunto de dados
    """
    Max_Discharg = sys.float_info.min
    Max_Charg = sys.float_info.min
    Min_Discharg = sys.float_info.max
    Min_Charg = sys.float_info.max

    for Name in Path_name:
        Max_Discharg = max(Max_Discharg, max(Dados[0][Name][key]))
        Min_Discharg = min(Min_Discharg, min(Dados[0][Name][key]))
        Max_Charg = max(Max_Charg, max(Dados[0][Name][key]))
        Min_Charg = min(Min_Charg, min(Dados[0][Name][key]))

    Max = (Max_Discharg + Max_Charg)/2
    Min = (Min_Discharg + Min_Charg)/2

    return [Max,Min]

def cicle_track(Discharge_out_data,Charge_out_data,Path_name,Qnt_cycles):
    """
    Coloca o Numero de ciclos nos Dados
    """
    for p in Path_name:
        Discharge_out_data[p]['Cicle'] = [-1*i for i in range(101)]
        Charge_out_data[p]['Cicle'] = [i for i in range(101)]
    
    return [Discharge_out_data,Charge_out_data]
    
def Limiar_Data(dados,percentil=10):
    """
    Retorna os X% piores dados
    """
    limiar = np.percentile(dados, percentil)

    if limiar > 1:
        return 1
    else:
        return limiar
    
def Previ_data(model,X_matrix,y_vet):
    """
    """
    X_matrix = X_matrix[0:100]
    y_vet = y_vet[0:100]
    Prediction = []
    Discg = 1
    for x in X_matrix:
        V = x[0]
        I = x[1]
        Discg -= 1
        Prediction.append(model.predict([[V,I,Discg]]))

    plot_Previ(Prediction,y_vet)

def plot_Previ(preditc,y_vet):
    """
    """
    plt.rcParams['font.size'] = 20
    x = range(len(preditc))
    plt.figure(figsize=(10,6))
    plt.plot(x,preditc,label='Previsão ML')
    plt.plot(x,y_vet,label='Banco de dados')
    plt.xlabel('Ciclos')
    plt.ylabel('Capacidade (Ah)')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.clf()


