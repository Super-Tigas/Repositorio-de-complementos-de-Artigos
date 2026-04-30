import matplotlib.pyplot as plt

Perdas_C = [34559,27597, 19085, 14482, 10143, 8453, 5666, 5571, 5571, 5571]
Perdas_S = [34559, 34579, 34579, 34579, 34579, 34579, 34579, 34579, 34579,34559]
plt.rcParams['font.size'] = 35
plt.figure(figsize=(10,6))
plt.plot(range(len(Perdas_C)),Perdas_C,lw=10,marker='o',label="Com degradação")
plt.plot(range(len(Perdas_S)),Perdas_S,lw=10,marker='o',label="Sem degradação")
plt.xlabel("Tempo (Anos)")
plt.ylabel("Perdas (kWh)")
plt.legend()
#plt.ylim(4000, 100000)
plt.grid(True)
plt.show()