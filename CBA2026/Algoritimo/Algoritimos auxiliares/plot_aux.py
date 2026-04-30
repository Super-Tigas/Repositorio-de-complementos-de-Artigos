#====================
#Color handler
def ggrad_av(num_cores):
    """Gera lista de cores do azul ao vermelho"""
    cores = []
    for i in range(num_cores):
        progresso = i / (num_cores - 1)
        if progresso < 0.5:
            fase = progresso * 2  
            b = int(220 - (fase * 100))  # 220 a 120 (nunca 255 nem 0)
            g = int(80 + (fase * 100))   # 80 a 180
            r = int(30 + (fase * 20))    # 30 a 50
        else:
            fase = (progresso - 0.5) * 2  
            r = int(100 + (fase * 150))   # 100 a 250 (nunca 255)
            g = int(180 - (fase * 100))   # 180 a 80
            b = int(120 - (fase * 100))   # 120 a 20 
        # Converter para hexadecimal
        cor_hex = f'#{r:02X}{g:02X}{b:02X}'
        cores.append(cor_hex)
    
    return cores
