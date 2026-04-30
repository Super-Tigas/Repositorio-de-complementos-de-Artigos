import dss
import pandas as pd
import matplotlib.pyplot as plt
import os
"""
A fazeres:
Remover os: Idlig_logic,D
do Swich logic
"""
#===================================
#   MODELO MACHINE LEARNIG
#===================================

def Battery_simulation_ML(model,V_base,I_base):
    """
    Simula a descarga da bateria
    """

    # Inicializa engine
    dss_engine = dss.DSS

    # Carrega o sistema
    dss_engine.Text.Command = "clear"
    dss_engine.Text.Command = "compile 34Bus/Run_IEEE34Mod1.dss"

    #Dakin
    capacity_data = []
    Time = []
    Corrente = []
    SOC = []

    Dias = int(30e5)
    Firts_loop = True

    #Setup
    dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
    capacity = float(dss_engine.ActiveCircuit.ActiveCktElement.Properties("kWhrated").Val)

    dss_engine.Circuits.SetActiveBus("844")

    I_base_A = 8

    dss_engine.Text.Command = "Edit Storage.bess844 dispmode=discharge"
    dss_engine.Text.Command = "Edit Storage.bess844 kw=400"  # Descarga plena

    Charg = 0
    Discg = 0
    Dispmode = False #Descarga
    Idlig_logic = False
    for D in range(Dias):

        #Desliga a bateria
        #dss_engine.Text.Command = 'Edit Storage.BESS844 enabled=no'

        # Controle de carga e descarga
        dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
        carga = float(dss_engine.ActiveCircuit.ActiveCktElement.Properties("kWhstored").Val)

        #Troca de carga
        Dispmode,Swich = estereze(carga,Dispmode,0.9,0.2,capacity)

        Charg,Discg = Swich_logic(dss_engine,Swich,Dispmode,Idlig_logic,D,[Charg,Discg])


        #Degradação
        #dss_engine.Text.Command = (f"Edit Storage.bess844 kWhrated={capacity}")
        # Resolve o caso
        #dss_engine.Text.Command = "set number=24"
        dss_engine.Text.Command = "set number=1"
        dss_engine.Text.Command = "Solve"

        #Pegar os valores de Tensão e corrente
        dss_engine.Circuits.SetActiveElement("Storage.bess844")
        I_medida = dss_engine.ActiveCircuit.ActiveCktElement.CurrentsMagAng[0]

        I_pu = I_medida / I_base_A
        I = I_pu * I_base
        
        #Tensão
        dss_engine.Circuits.SetActiveBus("844")
        V_pu = dss_engine.ActiveCircuit.ActiveBus.puVmagAngle[0]
        V = V_pu * V_base

        #Modelo
        if not Dispmode: 
            capacity_model = model.predict([[V,I,Discg]])
            capacity_model = capacity_model[0]
        #Primeira iteração, valores base capacity
        if Firts_loop: 
            capacity_base_ML = capacity_model
            capacity_base_OPDSS = capacity
            Firts_loop = False

        #Capacity
        if Swich:
            if not Dispmode: 
                capacity_old = capacity #Salva a capacity antes da degradação
                capacity = capacity_base_OPDSS/capacity_base_ML * capacity_model
            
                #Degradação
                Degradation(dss_engine,capacity,capacity_old)


                #Armazenamento para Dakin
                capacity_data.append(capacity/capacity_base_OPDSS)
                Time.append(D)
                Corrente.append(I_medida)
                SOC.append(carga/capacity)


        #Monitoramento
        dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
        estado = dss_engine.ActiveCircuit.ActiveCktElement.Properties("State").Val
        potencia_kw = dss_engine.ActiveCircuit.ActiveCktElement.Properties("kW").Val
        enabled = dss_engine.ActiveCircuit.ActiveCktElement.Properties("enabled").Val
        V_pu = dss_engine.ActiveCircuit.ActiveBus.puVmagAngle[0]

        #print([V,I,capacity,estado,potencia_kw,enabled,V_pu,carga,Charg,Discg])

        if abs(Discg) > 100:
            #Plot_Battery(dss_engine,capacity_data)
            return [capacity_data,Time,Corrente,SOC]
        
#===================================
#   MODELO DAKIN
#===================================

def Battery_simulation_Dakin(model):
    """
    Simula a descarga da bateria
    """
    # Inicializa engine
    dss_engine = dss.DSS
    Monitor = 0
    # Carrega o sistema
    dss_engine.Text.Command = "clear"
    dss_engine.Text.Command = "compile Run_IEEE34Mod1.dss"

    capacity_data = []

    Dias = int(365*9)
    #Dias = 4

    #Setup
    dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
    capacity = float(dss_engine.ActiveCircuit.ActiveCktElement.Properties("kWhrated").Val)
    capacity_i = capacity

    for D in range(Dias):

        #Desliga a bateria
        #dss_engine.Text.Command = 'Edit Storage.BESS844 enabled=no'

        dss_engine.Text.Command = "Edit Storage.bess844 dispmode=FOLLOW daily=curva_bateria_1"

        # Controle de carga e descarga
        dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
        carga = float(dss_engine.ActiveCircuit.ActiveCktElement.Properties("kWhstored").Val)

        #Troca de carga
        #Dispmode,Swich = estereze(carga,Dispmode,0.9,0.2,capacity)

        #Charg,Discg = Swich_logic(dss_engine,Swich,Dispmode,Idlig_logic,D,[Charg,Discg])

        # Resolve o caso
        dss_engine.Text.Command = "set number=24"
        #dss_engine.Text.Command = "set number=1"
        dss_engine.Text.Command = "Solve"

        #Pegar os valores de Tensão e corrente
        dss_engine.Circuits.SetActiveElement("Storage.bess844")
        I_medida = dss_engine.ActiveCircuit.ActiveCktElement.CurrentsMagAng[0]
        
        #Tensão
        dss_engine.Circuits.SetActiveBus("844")
        V_pu = dss_engine.ActiveCircuit.ActiveBus.puVmagAngle[0]

        #Modelo
        SOC = carga/capacity
        capacity = model.dakin_capacity(D,SOC,I_medida)*capacity_i
        capacity_old = capacity #Salva a capacity antes da degradação
        capacity_data.append(capacity)

        #Degradação
        Degradation(dss_engine,capacity,capacity_old)

        if capacity/capacity_i < 0.6:
            #break
            pass


        #Monitoramento
        dss_engine.Text.Command = "Export Meters EnergyMeters"
        # dss_engine.ActiveCircuit.SetActiveElement("Storage.bess844")
        # estado = dss_engine.ActiveCircuit.ActiveCktElement.Properties("State").Val
        # potencia_kw = dss_engine.ActiveCircuit.ActiveCktElement.Properties("kW").Val
        # enabled = dss_engine.ActiveCircuit.ActiveCktElement.Properties("enabled").Val
        # V_pu = dss_engine.ActiveCircuit.ActiveBus.puVmagAngle[0]
        # Monitor += 1
        # if Monitor > 365:
        #     print([V_pu,I_medida,capacity,potencia_kw,estado,D,carga])
        #     Monitor = 0

    #Plot_Battery(dss_engine,capacity_data)
    Dado_especificos(dss_engine)


#===================================
#   Artigo
#===================================
def plot_especifico(Data):
    plot_perdas = Data
    plt.rcParams['font.size'] = 35
    plt.figure(figsize=(10,6))
    plt.plot(range(len(plot_perdas)),plot_perdas,lw=10,marker='o')
    plt.xlabel("Dias")
    plt.ylabel("Perdas (kwh)")
    plt.grid(True)
    plt.show()


def Dado_especificos(dss_engine):
    """
    Imprime alguns especificos
    para o artigo
    """
    Plot_perdas = []
    #Dados armazenados a Cada Hora
    dss_engine.Text.Command = "Export monitors storage"
    df = pd.read_csv("ieee34-1_Mon_storage_1.csv", skipinitialspace=True)

    #Dados armazenados a Cada Dia
    os.remove("EnergyMeters.csv")
    os.rename("EnergyMeters", "EnergyMeters.csv")
    df2 = pd.read_csv("EnergyMeters.csv", skipinitialspace=True)

    horas_por_ano = 365 * 24  # 8760 horas
    Dias_por_ano = 365
    total_horas = len(df)
    num_anos = total_horas // horas_por_ano

    for ano in range(num_anos):
        inicio = ano * horas_por_ano
        fim = (ano + 1) * horas_por_ano
        dados_ano = df.iloc[inicio:fim]

        #Dados já estão acumulados (Pega só o final)
        inicio2 = ano*Dias_por_ano
        fim2 = (ano+1)*Dias_por_ano
        dados2 = df2.iloc[fim2-1]
        
        energia_descarga = dados_ano['kWOut'].sum()
        energia_carga = dados_ano['kWIn'].sum()
        Perdas_Bateria = dados_ano['kWTotalLosses'].sum()
        Perdas_sistema = dados2['Zone Losses kWh']
        Plot_perdas_aux = df2.iloc[inicio2:fim2]['Zone Losses kWh']
        #Plot_perdas.append(df2.iloc[fim2-1]['Zone Losses kWh'])
        #Plot_perdas.append((Plot_perdas_aux[-1:].values-Plot_perdas_aux[:1].values)[0])
        Plot_perdas.append(Perdas_Bateria)

        print(f"Ano {ano+1}:")
        print(f"  Energia descarregada: {energia_descarga:.0f} kWh")
        print(f"  Energia carregada: {energia_carga:.0f} kWh")
        print(f"  Perdas totais Bateria: {Perdas_Bateria:.0f} kWh")
        print(f"  Saldo: {energia_descarga - energia_carga:.0f} kWh")
        print(f"  Perdas do Sistema: {Perdas_sistema} kWh")
        print("--"*30)

    #plot_especifico(Plot_perdas)

#===================================
#   PLOT
#===================================

def Plot_Battery(dss_engine,capacity_data):
    """
    Plota os graficos de degradação
    """

    dss_engine.Text.Command = "Export monitors C1"
    dss_engine.Text.Command = "Export monitors storage"
    dss_engine.Text.Command = "Export monitors MainBus"

    #Grafico de Potencia
    # df = pd.read_csv("ieee34-1_Mon_c1_1.csv", skipinitialspace=True)

    # plt.plot(df["hour"], df["P1 (kW)"], label="P1 (kW)")
    # plt.plot(df["hour"], df["P2 (kW)"], label="P2 (kW)")
    # plt.plot(df["hour"], df["P3 (kW)"], label="P3 (kW)")

    # plt.xlabel("Hora")
    # plt.ylabel("Potência (kW)")
    # plt.title("P1, P2 e P3")
    # plt.grid(True)
    # plt.legend()
    # plt.show()

    #Grafico da bateria
    df = pd.read_csv("ieee34-1_Mon_storage_1.csv", skipinitialspace=True)
    plt.rcParams['font.size'] = 35
    plt.figure(figsize=(10,6))
    plt.plot(df["hour"], df["kWh"],lw=10)
    plt.xlabel("Tempo (Horas)")
    plt.ylabel("Carga (kWh)")
    plt.grid(True)
    plt.show()

    #Grafico do alimentador principal
    # df = pd.read_csv("ieee34-1_Mon_mainbus_1.csv", skipinitialspace=True)
    # plt.plot(df["hour"], df["P1 (kW)"], label="P1 (kW)")
    # plt.plot(df["hour"], df["P2 (kW)"], label="P2 (kW)")
    # plt.plot(df["hour"], df["P3 (kW)"], label="P3 (kW)")

    # plt.xlabel("Horas")
    # plt.ylabel("Potência (kW)")
    # plt.title("Alimentador Principal")
    # plt.grid(True)
    # plt.legend()
    # plt.show()

    #Grafico de degradação
    plt.figure(figsize=(10,6))
    plt.plot(range(len(capacity_data)),capacity_data,lw=10)
    plt.xlabel("Tempo (Dias)")
    plt.ylabel('Capacidade (kWh)')
    plt.title('Degradação da Bateria')
    plt.grid(True)
    plt.show()

    #Grafico Estado da Bateria
    # df = pd.read_csv("ieee34-1_Mon_storage_1.csv", skipinitialspace=True)
    # plt.figure(figsize=(10,6))
    # plt.plot(df["hour"],df['State'],label="1 = Chargin; -1 = Dischargin; 0 = Idling",lw=10)
    # plt.xlabel("Horas")
    # plt.ylabel('Estado de operação')
    # plt.grid(True)
    # plt.show()



#===================================
#   CONTROLES LOGICOS
#===================================

def estereze(carga,State,UB,LB,capacity):
    """
    """
    UB = capacity * UB
    LB = capacity * LB
    Swich = False

    if State: #Chargin
        if carga >= UB:
            State = False
            Swich = True

    else:
        if carga <= LB:
            State = True
            Swich = True

    return State,Swich

def Degradation(dss_engine,capacity,capacity_old):
    # Salva o percentual de carga ANTES de editar
    carga_atual_kWh = float(dss_engine.ActiveCircuit.ActiveCktElement.Properties("kWhstored").Val)
    percentual_carga = carga_atual_kWh / capacity_old

    # Edita a capacidade nominal
    dss_engine.Text.Command = f"Edit Storage.bess844 kWhrated={capacity}"

    # Restaura o mesmo percentual de carga
    nova_carga_kWh = percentual_carga * capacity
    dss_engine.Text.Command = f"Edit Storage.bess844 kWhstored={nova_carga_kWh}"

def Swich_logic(dss_engine,Swich,Dispmode,Idlig_logic,D,CD):

    Charg = CD[0]
    Discg = CD[1]

    if Swich:
        if Dispmode:
            dss_engine.Text.Command = "Edit Storage.bess844 State=Charging"
            Charg += 1
        else:
            dss_engine.Text.Command = "Edit Storage.bess844 State=Discharging"
            Discg -= 1
    
    if dss_engine.ActiveCircuit.ActiveCktElement.Properties("State").Val == 'Idling':
        if Dispmode:
            dss_engine.Text.Command = "Edit Storage.bess844 State=Charging"
        else:
            dss_engine.Text.Command = "Edit Storage.bess844 State=Discharging"

    # if D%10 > 3:
    #     dss_engine.Text.Command = "Edit Storage.bess844 State=Idling"
    #     Idlig_logic = True
    # elif Idlig_logic:
    #     Swich = True
    #     Idlig_logic = False

    return Charg,Discg