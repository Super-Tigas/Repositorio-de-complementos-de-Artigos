from Data_handler import data_path5,data_path6,data_path7,data_path18
from Data_handler import ML_data_reciver,flattening,Max_Min_data,Limiar_Data,Previ_data
from mlalg import machinelearning,metrics,plot_results
from Battery_discharge import Battery_simulation_ML,Battery_simulation_Dakin
from Dakin import Dakin
import numpy as np

"""
'Voltage_measured'
'Current_measured'
'Temperature_measured'
'Current_load'
'Voltage_load'
'Capacity'
"""
"""
A fazeres
confirmar o grafico do alpha os eixos (X e Y)
fazer um grafico do erro crescendo com o tempo
"""


Black_listed = ['Temperature_measured','Voltage_load','Current_load'] # Não vão ser coletados
Key_y = 'Capacity'
Path_list = [data_path5,data_path6,data_path7,data_path18]
Path_name = ['B0005','B0006','B0007','B0018']
Qnt_data = 100 #Perto do Limite(150)
Qnt_cycles = 100


Dados = ML_data_reciver(Path_list,Path_name,Qnt_data,Qnt_cycles,Black_listed) #return [Discharge_out_data,Charge_out_data]

X_matrix,y_vet=flattening(Path_name,Dados,Qnt_data,Key_y)

model,y_test,y_pred=machinelearning(X_matrix,y_vet)

erro, r2 = metrics(y_test,y_pred)

print("Machine Learnig")
print(f"Erro Médio: {erro}")
print(f"R² (Acurácia científica): {r2}\n")

#Previ_data(model,X_matrix,y_vet)

base_V = Max_Min_data(Dados,Path_name,'Voltage_measured')[0]
base_C = Max_Min_data(Dados,Path_name,'Current_measured')[1] #As correntes são negativas

data_DSS = Battery_simulation_ML(model,base_V,base_C)

limiar = Limiar_Data(data_DSS[2])

data_DSS = np.array(data_DSS)

print("Modelo Dakin:")
Model_DK = Dakin(data_DSS,limiar,False)


Battery_simulation_Dakin(Model_DK)

