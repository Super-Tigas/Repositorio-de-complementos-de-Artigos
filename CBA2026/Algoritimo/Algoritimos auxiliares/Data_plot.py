from Data_handler import Get_data
from Data_handler import Get_data_size,amostrar_porcentagem_v2
from plot_aux import ggrad_av
from Data_handler import data_path5,data_path6,data_path7,data_path18
import time
import matplotlib.pyplot as plt
from pathlib import Path
import os

Path_list = [data_path5,data_path6,data_path7,data_path18]
Path_name = ['B0005','B0006','B0007','B0018']
p = -1
ts = time.time()
for path in Path_list:
    p+=1
    #Indices de discharge e charge
    Disch_indx = []
    Charge_indx = []
    Imped_indx = []

    # Pra medir o tempo dessa brincadeira
    #print(f'Time: {time.time() - ts:.3f} s')

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

    #print(f'{Disch_indx} | {len(Disch_indx)}')
    #print(f'{Charge_indx} | {len(Charge_indx)}')
    #print(f'{Imped_indx} | {len(Imped_indx)}')

    # 'data': return loadmat(data_path5)['B0005']['cycle'][0,0][0][Cycle][Header][0,0][Campo][0]
    # 'all' : return loadmat(data_path5)['B0005']['cycle'][0,0][0]
    #  else : return loadmat(data_path5)['B0005']['cycle'][0,0][0][Cycle][Header][0]

    os.makedirs(Path("Graficos")/Path_name[p], exist_ok=True)
    Grafico_path = Path("Graficos")/Path_name[p]
    #Discharge
    idx = [0, 1, 2, 3, 4, 6]
    data_plot_dis = Data_set[Disch_indx[0]]['data'][0,0].dtype.names[0:5]
    y_Axs = ['Battery terminal voltage (Volts)','Battery output current (Amps)','Battery temperature (degree C)','Current measured at charger (Amps)','Voltage measured at charger (Volts)']
    for_var = -1
    Disch_indx_Ams = amostrar_porcentagem_v2(Disch_indx,1)
    color_map = ggrad_av(int(len(Disch_indx_Ams)))
    for fields in data_plot_dis:
        for_var+=1
        color_v = -1
        for i in Disch_indx_Ams:
            color_v+=1
            x = Data_set[i]['data'][0,0]['Time'][0]
            y = Data_set[i]['data'][0,0][fields][0]
            if i == Disch_indx_Ams[0]: pass
            elif i == Disch_indx_Ams[-1]: plt.plot(x,y,'r',label='Fim dos testes')
            else: plt.plot(x,y,color_map[color_v],alpha=0.25)

        plt.plot(Data_set[Disch_indx_Ams[0]]['data'][0,0]['Time'][0],Data_set[Disch_indx_Ams[0]]['data'][0,0][fields][0],'b',label='Início dos testes')
        plt.xlabel('Tempo (s)')
        plt.ylabel(y_Axs[for_var])
        plt.title(f'Curvas de descarga: {fields}')
        plt.legend()
        plt.grid(True)
        plt.savefig(Grafico_path/f'Discharge_{fields}.png', dpi=300, bbox_inches='tight')
        plt.clf()
    #==============================================
    #Charge
    data_plot_charg = Data_set[Charge_indx[0]]['data'][0,0].dtype.names[0:5]
    y_Axs = ['Battery terminal voltage (Volts)','Battery output current (Amps)','Battery temperature (degree C)','Current measured at charger (Amps)','Voltage measured at charger (Volts)']
    for_var = -1
    Charge_indx_Ams = amostrar_porcentagem_v2(Charge_indx,1)
    color_map = ggrad_av(int(len(Charge_indx_Ams)))
    for fields in data_plot_charg:
        for_var+=1
        color_v = -1
        for i in Charge_indx_Ams:
            color_v+=1
            x = Data_set[i]['data'][0,0]['Time'][0]
            y = Data_set[i]['data'][0,0][fields][0]
            if i == Charge_indx_Ams[0]: pass
            elif i == Charge_indx_Ams[-1]: plt.plot(x,y,'r',label='Fim dos testes')
            else: plt.plot(x,y,color_map[color_v],alpha=0.25)

        plt.plot(Data_set[Charge_indx_Ams[0]]['data'][0,0]['Time'][0],Data_set[Charge_indx_Ams[0]]['data'][0,0][fields][0],'b',label='Início dos testes')
        plt.xlabel('Tempo (s)')
        plt.ylabel(y_Axs[for_var])
        plt.title(f'Curvas de carga: {fields}')
        plt.legend()
        plt.grid(True)
        plt.savefig(Grafico_path/f'Charge_{fields}.png', dpi=300, bbox_inches='tight')
        plt.clf()
    #==============================================
    #Capacity
    data_plot_impd = Data_set[Disch_indx_Ams[0]]['data'][0,0].dtype.names[6]
    fields = data_plot_impd
    y = []
    for i in Disch_indx_Ams:
        y.append([Data_set[i]['data'][0,0][data_plot_impd][0,0]][0])
    x = range(len(Disch_indx_Ams))
    plt.plot(x,y)
    plt.xlabel('Cycles')
    plt.ylabel('Battery capacity (Ahr)')
    plt.title(f'Curvas de descarga: {fields}')
    plt.legend()
    plt.grid(True)
    plt.savefig(Grafico_path/f'Discharge_{fields}.png', dpi=300, bbox_inches='tight')
    plt.clf()

print(f'Time: {time.time() - ts:.3f} s')

