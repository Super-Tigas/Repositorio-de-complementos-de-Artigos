import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Os dois mapas
mapa1 = ['#1E50DC', '#1E52D9', '#1F55D6', '#1F58D3', '#205BD0', '#205ECD', '#2161CA', '#2264C7', '#2267C4', '#236AC1', '#236DBE', '#2470BB', '#2573B8', '#2576B5', '#2679B2', '#267CAF', '#277FAC', '#2882A9', '#2885A6', '#2988A3', '#298BA0', '#2A8E9D', '#2B919A', '#2B9497', '#2C9794', '#2C9A91', '#2D9D8E', '#2EA08B', '#2EA388', '#2FA685', '#2FA982', '#30AC7F', '#31AF7C', '#31B279', '#66B276', '#6AAF73', '#6FAC70', '#73A96D', '#78A66A', '#7CA367', '#81A064', '#859D61', '#8A9A5E', '#8E975B', '#939458', '#979155', '#9B8E52', '#A08B4F', '#A4884C', '#A98549', '#AD8246', '#B27F43', '#B67C40', '#BB793D', '#BF763A', '#C47337', '#C87034', '#CD6D31', '#D16A2E', '#D6672B', '#DA6428', '#DF6125', '#E35E22', '#E85B1F', '#EC581C', '#F15519', '#F55216', '#FA5014']

mapa2 = ['#1E50DC', '#1E53D8', '#1F56D5', '#1F59D2', '#205CCF', '#215FCC', '#2162C9', '#2265C6', '#2268C3', '#236BC0', '#246EBD', '#2471BA', '#2574B7', '#2577B4', '#267AB1', '#277DAE', '#2780AB', '#2883A8', '#2886A5', '#2989A2', '#2A8C9F', '#2A8F9C', '#2B9299', '#2B9596', '#2C9893', '#2D9B90', '#2D9E8D', '#2EA18A', '#2EA487', '#2FA784', '#30AA81', '#30AD7E', '#31B07B', '#64B478', '#68B074', '#6DAD71', '#71AA6E', '#76A76B', '#7AA468', '#7FA165', '#839E62', '#889B5F', '#8C985C', '#919559', '#969256', '#9A8F53', '#9F8C50', '#A3894D', '#A8864A', '#AC8347', '#B18044', '#B57D41', '#BA7A3E', '#BE773B', '#C37438', '#C87135', '#CC6E32', '#D16B2F', '#D5682C', '#DA6529', '#DE6226', '#E35F23', '#E75C20', '#EC591D', '#F0561A', '#F55317', '#FA5014']

# Visualizar diferenças
fig, axes = plt.subplots(2, 1, figsize=(12, 4))

for idx, (mapa, titulo) in enumerate([(mapa1, 'Mapa 1'), (mapa2, 'Mapa 2')]):
    ax = axes[idx]
    
    for i, cor in enumerate(mapa):
        rect = patches.Rectangle((i, 0), 1, 1, facecolor=cor, edgecolor='black', linewidth=0.5)
        ax.add_patch(rect)
        
        # Destacar onde são diferentes (comparando com o outro mapa)
        if idx == 1 and i < len(mapa1) and i < len(mapa2):
            if mapa1[i] != mapa2[i]:
                # Marcar com X vermelho onde há diferença
                ax.text(i + 0.5, 0.5, 'X', ha='center', va='center', 
                       color='red', fontweight='bold', fontsize=8)
    
    ax.set_xlim(0, len(mapa))
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{titulo} - {len(mapa)} cores', fontsize=10, pad=5)

plt.tight_layout()
plt.show()

# Contar diferenças
diferencas = []
for i in range(min(len(mapa1), len(mapa2))):
    if mapa1[i] != mapa2[i]:
        diferencas.append((i, mapa1[i], mapa2[i]))

print(f"Total de cores: Mapa 1 = {len(mapa1)}, Mapa 2 = {len(mapa2)}")
print(f"Número de cores diferentes: {len(diferencas)}")
print("\nAlgumas diferenças:")
for i, cor1, cor2 in diferencas[:10]:  # Mostrar só as 10 primeiras
    print(f"Posição {i:2d}: {cor1} ≠ {cor2}")