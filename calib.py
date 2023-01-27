import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

#classe para armazenar uma instancia de medida realizada, contém valor e resolucao
class Measurement:
    def __init__(self, val, res):
        self.val = val
        self.res = res
    def __repr__(self):
        return f"Measurement({self.val},{self.res})"

#classe para criar o equipamento que sera utilizado no processo de calibraçao
class Equipment:
    name = "default"
    def __init__(self, name: str, *args: Measurement):
        self.measurements = []
        self.name = name
        for item in args:
            self.measurements.append(item)
    def show_info(self):
        i = 1
        for el in self.measurements:
            print(i, ". val = ", el.val, " res = ", el.res, sep='')
            i += 1

#classe para criar o equipamento padrao, herdando da classe Equipment
#possui como atributos extras pct e dig que se referem à incerteza expressada no manual do eq. padrao
class Standard(Equipment):
    def __init__(self, name: str, pct: float, dig: int, *args: Measurement):
        self.pct = pct
        self.dig = dig
        super().__init__(name, *args)

class Calibration:
    lim_teste = 10
    def __init__(self, std : Standard, tobecal : Equipment, lim_test = 10):
        self.std = std
        self.tobecal = tobecal
        self.lim_teste = lim_test
        self.show()
        self.results = self.calc()

    def __repr__(self):
        return f"Calibration({self.std}, {self.tobecal})"

    #mostra o nome dos equipamentos utilizados no processo de calibracao atual e os valores medidos por cada um, inclusive a resolução
    def show(self):
        print("Standard: ", self.std.name, " -> Uncertainty = ", self.std.pct, "% +- ", self.std.dig, "D", sep='')
        self.std.show_info()
        print()
        print("To be calibrated: ", self.tobecal.name, sep='')
        self.tobecal.show_info()
        print()
    
    # brute force dos valores para os quais determinado conjunto de medidas é aprovado no teste de conformidade
    def calc(self):
        res = []
        pct_teste = np.arange(0, self.lim_teste + .1, .1) # armazena os percentuais de erro que serao testados
        lastd = 11
        for pct_erro in pct_teste: # para cada percentual de erro
            for digito in range(11): # somado com cada digito de 0...10
                aprovado = 0
                for num_medida in range(len(self.std.measurements)):
                    tbc_val = self.tobecal.measurements[num_medida].val
                    tbc_res = self.tobecal.measurements[num_medida].res
                    std_val = self.std.measurements[num_medida].val
                    std_res = self.std.measurements[num_medida].res
    
                    
                    deltaC = tbc_res                     # resolucao do equipamento custom = deltaC da formula de calibracao
                    u_deltaC = deltaC / (2 * sqrt(3))    # u(deltaC) da formula de incerteza da calibracao é metade da resolucao dividido por sqrt(3)

                    deltaP = (self.std.pct / 100.) * std_val + self.std.dig * std_res  # incerteza da medicao do equip. padrao, fornecido pelo manual
                    u_deltaP = deltaP / sqrt(3)                             # incerteza equipamento padrao tipo B

                    uc = sqrt(u_deltaP ** 2 + u_deltaC ** 2)        # incerteza combinada
                    uexp = uc * 1.65                                # incerteza expandida!

                    erro_max = (pct_erro / 100.) * tbc_val + digito * tbc_res   # precisao do equipamento a ser calibrado
                    erro = abs(std_val - tbc_val)                          # erro entre o valor medido pelo EC (custom) e pelo EP
                    duvida_min = erro_max - uexp                           # limite inferior da zona de duvida
                    duvida_max = erro_max + uexp                           # limite superior da zona de duvida
                    
                    if erro < duvida_min:
                        aprovado += 1
                if aprovado == 3:
                    if digito < lastd:
                        res.append((pct_erro, digito))
                        lastd = digito
                    break
        return res

    #função para imprimir grafico de algum dos testes de conformidade
    #escolher o idx do vetor resultante com o parametro idx, as faixas utilizadas
    #se deve ou nao gerar aquivo de imagem, o nome do arquivo e a qualidade
    def graph(self, idx=-1, faixas=[10, 50, 95], to_save=False, filename="default", quality=100):
        _, ax = plt.subplots(1, 3, figsize=(15, 5))

        for num_medida in range(len(self.std.measurements)):
            tbc_val = self.tobecal.measurements[num_medida].val
            tbc_res = self.tobecal.measurements[num_medida].res
            std_val = self.std.measurements[num_medida].val
            std_res = self.std.measurements[num_medida].res
            
            deltaC = tbc_res                     # resolucao do equipamento custom = deltaC da formula de calibracao
            u_deltaC = deltaC / (2 * sqrt(3))               # u(deltaC) da formula de incerteza da calibracao é metade da resolucao dividido por sqrt(3)

            deltaP = (self.std.pct / 100.) * std_val + self.std.dig * std_res  # incerteza da medicao do equip. padrao, fornecido pelo manual
            u_deltaP = deltaP / sqrt(3)                             # incerteza equipamento padrao tipo B

            uc = sqrt(u_deltaP ** 2 + u_deltaC ** 2)        # incerteza combinada
            uexp = uc * 1.65                                # incerteza expandida!

            erro_max = (self.results[idx][0] / 100.) * tbc_val + self.results[idx][1] * tbc_res   # precisao do equipamento a ser calibrado
            erro = abs(std_val - tbc_val)                          # erro entre o valor medido pelo EC (custom) e pelo EP
            duvida_min = erro_max - uexp                                      # limite inferior da zona de duvida
            duvida_max = erro_max + uexp                                      # limite superior da zona de duvida
            ax[num_medida].scatter(erro, 0, color = 'b')
            ax[num_medida].plot([duvida_min, erro_max, duvida_max], [0, .2, 0], c='k', ls='dotted', label='_nolegend_')
            ax[num_medida].set_xlim([-duvida_max / 3.5, max(duvida_max * 1.5, erro * 1.1)])
            ax[num_medida].axvline(erro_max, .05, .95, ls = 'dotted', c='k',label='_nolegend_')
            ax[num_medida].set_title("Medida " + str(num_medida + 1) + " (" + str(faixas[num_medida]) + "% da faixa)")
            ax[num_medida].get_yaxis().set_visible(False)
            xtick_val = [round(k, 2) for k in [duvida_min, erro_max, duvida_max]]
            ax[num_medida].set_xticks(xtick_val)
            pt = ax[num_medida].get_xlim()
            ptdiff = pt[1] - pt[0]
            ax[num_medida].axhline(0, 0, (duvida_min-pt[0])/ptdiff, c='g')
            ax[num_medida].axhline(0, (duvida_min-pt[0])/ptdiff+.001, (duvida_max-pt[0])/ptdiff, c='#FFE900')
            ax[num_medida].axhline(0, (duvida_max-pt[0])/ptdiff + .001, 1, c='r')
            ax[num_medida].legend(['Erro', 'Aprovacao', 'Duvida', 'Rejeicao'], loc='best')
        if to_save:
            plt.savefig(filename+".png", dpi=quality)
        plt.show()
    
    #funcao que exibe para quais valores de inctz determinado equipamento a ser calibrado é aprovado
    #dado o conjunto de medidas fornecido e os paramentros (pct de erro e dig) do equipamento padrao 
    def values(self):
        print("Approved for:")
        for el in self.results:
            print(round(el[0], 2), "% +- ", el[1], "D", sep='')