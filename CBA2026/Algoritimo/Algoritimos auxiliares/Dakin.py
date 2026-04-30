import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
import os
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression


R = 8.314  # J/(mol·K) - constante dos gases
T_kelvin = 298  # fixo

class Dakin():
    def __init__(self,data_DSS,limiar,Show = False):
        """
        data_DSS[0] => capacity (0 a 1)
        data_DSS[1] => Tempo em horas
        data_DSS[2] => Correntes em Amperes
        data_DSS[3] => Soc (0 a 1)
        limiar_corrente => pegar os 10% menor (pode variar)
        """
        BASE_DIR = Path(__file__).parent.parent
        self.Grafico_path = BASE_DIR/'Graficos'/'Dakin'
        os.makedirs(self.Grafico_path, exist_ok=True)
        self.Show = Show

        alpha = self.dakin_ajuste_alpha(data_DSS)[0]
        k = self.dakin_ajuste_k(data_DSS,alpha)
        cal_data, cic_data = self.Calibration_Setup(data_DSS,limiar,k)
        c, intercept = self.dakin_calibrar_c(cal_data)
        a = self.dakin_calibrar_a(cic_data,c,intercept)

        self.alpha = alpha
        self.c = c
        self.a = a
        self.constante = intercept
        

    def dakin_capacity(self,t_horas, soc, I_amperes):
        """
        """
        #t_dias = t_horas / 24
        t_dias = t_horas
        ln_k_cal = -self.c * soc / R + self.constante
        k_cal = np.exp(ln_k_cal)
        k_cyc = np.exp(self.a * abs(I_amperes))
        k_total = k_cal * k_cyc
        capacidade = np.exp(-k_total * (t_dias ** self.alpha))
        return capacidade

    def linear_fit(self,x, a, b):
        return a * x + b

    def dakin_ajuste_alpha(self,data_DSS):
        """
        Calibra a equação de Dakin
        data_DSS[0] => capacity
        data_DSS[1] => Tempo em horas
        """

        mask = data_DSS[0] < 0.99 # Evita log(1) = 0

        C = data_DSS[0][mask] #capacity
        t = np.array(data_DSS[1][mask]) / 24

        y = np.log(-np.log(C))
        x = np.log(t)
        plt.rcParams['font.size'] = 35
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, color='blue', s=50, label='Dados')

        params, covariance = curve_fit(self.linear_fit, x, y)
        alpha, b_intercept = params

        errors = np.sqrt(np.diag(covariance))
        erro_alpha = errors[0]

        x_line = np.linspace(min(x), max(x), 100)
        y_line = alpha * x_line + b_intercept

        print(f"α = {alpha:.4f} ± {erro_alpha:.4f}")

        plt.plot(x_line, y_line, 'r--', label=f'Reta (α = {alpha:.3f})')
        plt.xlabel('ln(tempo) [dias]')
        plt.ylabel('ln(-ln(C))')
        plt.title('Determinação do expoente α (Dakin)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        if self.Show: plt.show()
        plt.savefig(self.Grafico_path/'Dankin_alpha.png', dpi=300, bbox_inches='tight')
        plt.clf()

        return alpha, erro_alpha


    def dakin_ajuste_k(self,data_DSS,alpha):
        """
        Calibra a equação de Dakin
        data_DSS[0] => capacity (0 a 1)
        data_DSS[1] => Tempo em horas
        alpha => calculado da função dakin_ajuste_alpha()
        """
        mask = data_DSS[0] < 0.99 # Evita log(1) = 0

        C = np.array(data_DSS[0][mask])
        t_dias = np.array(data_DSS[1][mask]) / 24
        
        k = -np.log(C) / (t_dias ** alpha)
        
        return k

    def Calibration_Setup(self,data_DSS,limiar_corrente,k):
        """
        data_DSS[0] => capacity (0 a 1)
        data_DSS[1] => Tempo em horas
        data_DSS[2] => Correntes em Amperes
        data_DSS[3] => Soc (0 a 1)
        limiar_corrente => pegar os 10% menor (pode variar)
        k => Calculado em dakin_ajuste_k()
        """
        mask = data_DSS[0] < 0.99
        C = data_DSS[0][mask] #capacity
        t = np.array(data_DSS[1][mask]) / 24
        I = data_DSS[2][mask]
        soc = data_DSS[3][mask]

        mask_cal = abs(I) <= limiar_corrente   # I ≈ 0
        mask_cic = abs(I) >= limiar_corrente  # I > 0

        # Dados de calendar (I ≈ 0)
        cal_data = {
            'k': k[mask_cal],
            'soc': soc[mask_cal],
            't_dias': t[mask_cal],
            'C': C[mask_cal]
        }
        
        # Dados de ciclagem (I > 0)
        cic_data = {
            'k': k[mask_cic],
            'soc': soc[mask_cic],
            'I': abs(I[mask_cic]),  # usa valor absoluto
            't_dias': t[mask_cic],
            'C': C[mask_cic]
        }
        
        print(f"Pontos de calendar: {len(cal_data['k'])}")
        print(f"Pontos de ciclagem: {len(cic_data['k'])}")
        
        return cal_data, cic_data

    def dakin_calibrar_c(self,cal_data):
        """
        cal_data => Vem de Calibration_Setup()
        """
        if len(cal_data['k']) < 3:
            print("Sem dados suficientes de calendar. Usando valores padrão.")
            
            # Valores padrão (baseados na literatura e no artigo)
            c_padrao = 0          # J/(mol·K) - efeito típico do SOC
            intercept_padrao = -6.2  # valor típico (d/R - b/(R*T))
            
            return c_padrao, intercept_padrao

        k = np.array(cal_data['k'])
        soc = np.array(cal_data['soc'])

        y = np.log(k)
        x = soc/R

        # Regressão linear: y = inclinacao * x + intercept
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # A inclinação é -c
        c = -slope
        
        # Calcula R²
        r2 = r_value ** 2
        
        print(f"c = {c:.4f} J/(mol·K)")
        print(f"Constante = {intercept:.4f}")
        print(f"R² = {r2:.4f}")
        
        # Gráfico
        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, color='blue', s=50, label='Dados calendar')
        
        # Reta de ajuste
        x_line = np.linspace(min(x), max(x), 100)
        y_line = slope * x_line + intercept
        plt.plot(x_line, y_line, 'r--', label=f'Ajuste (c = {c:.3f})')
        
        plt.xlabel('SOC / R (K⁻¹)')
        plt.ylabel('ln(k)')
        plt.title('Calibração do parâmetro c (efeito do SOC)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(self.Grafico_path/'Dakin_calibracao_c.png', dpi=300, bbox_inches='tight')
        if self.Show: plt.show()
        plt.clf()
        
        return c, intercept

    def dakin_calibrar_a(self,cic_data, c, constante_calendar):
        """
        cic_data => Vem de Calibration_Setup()
        c => Vem de dakin_calibrar_c()
        constante_calendar => Vem de dakin_calibrar_c() [intercept]
        """

        k_total = np.array(cic_data['k'])
        soc = np.array(cic_data['soc'])
        I = np.array(cic_data['I']).reshape(-1, 1)
        
        ln_k_cal = -c * soc / R + constante_calendar
        k_cal = np.exp(ln_k_cal)
        
        y = np.log(k_total / k_cal)
        
        # Força passar pela origem (fit_intercept=False)
        reg = LinearRegression(fit_intercept=False)
        reg.fit(I, y)
        
        a = reg.coef_[0]
        r2 = reg.score(I, y)
        
        print(f"a = {a:.6f}")
        print(f"R² = {r2:.4f}")

        plt.figure(figsize=(8, 6))
        plt.scatter(I, y, color='green', s=50, label='Dados ciclagem')

        I_line = np.linspace(0, max(I), 100).reshape(-1, 1)
        y_line = reg.predict(I_line)
        plt.plot(I_line, y_line, 'r--', label=f'Ajuste (a = {a:.6f})')

        plt.xlabel('Corrente I (A)')
        plt.ylabel('ln(k_total / k_calendario)')
        plt.title('Calibração do parâmetro a (efeito da corrente)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(self.Grafico_path/'Dakin_calibracao_a.png', dpi=300, bbox_inches='tight')
        if self.Show: plt.show()
        plt.clf()
        
        return a