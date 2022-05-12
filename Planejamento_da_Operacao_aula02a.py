from cvxopt.modeling import variable, solvers, op
from itertools import product
import numpy


def despacho2(VI, AFL, imprime):
    lista_uhe = []
    lista_ute = []

    usina = {
        "Nome": "UHE DO MARCATO",
        "VMAX": 100.,
        "VMIN": 20.,
        "PROD": 0.95,
        "ENGOL": 60.,
        "hist_afl": [
            [23, 14],
            [19, 14],
            [15, 11]
        ]
    }

    lista_uhe.append(usina)

    usina = {
        "Nome": "UHE DO VASCAO",
        "VMAX": 300.,
        "VMIN": 50.,
        "PROD": 0.85,
        "ENGOL": 100.,
    }

    usina = {
        "Nome": "GT_1",
        "CAPAC": 15.,
        "CUSTO": 10.
    }

    lista_ute.append(usina)

    usina = {
        "Nome": "GT_2",
        "CAPAC": 10.,
        "CUSTO": 25.
    }

    lista_ute.append(usina)

    d_gerais = {
        "CDEF": 500.,
        "CARGA": [50., 50., 50.],
        "Nr_disc": 3,
        "NR_Est": 3,
        "Nr_Cen": 2
    }

    sistema = {
        "DGer": d_gerais,
        "UHE": lista_uhe,
        "UTE": lista_ute
    }

    Num_UHE = len(sistema["UHE"])
    Num_UTE = len(sistema["UTE"])

    vf = variable(Num_UHE, "Volume Final na Usina")
    vt = variable(Num_UHE, "Volume Turbinado na Usina")
    vv = variable(Num_UHE, "Volume Vertido na Usina")
    gt = variable(Num_UTE, "Geração na Usina Térmica")
    deficit = variable(1, "Déficit de Energia no Sistema")

    # Construção da Função objetivo
    fob = 0

    for i, iusi in enumerate(sistema["UTE"]):
        fob += iusi["CUSTO"] * gt[i]

    fob += sistema["DGer"]["CDEF"] * deficit[0]

    for i, iusi in enumerate(sistema["UHE"]):
        fob += 0.01 * vv[i]

    # Definiões das Restrições
    restricoes = []

    # Balanço Hídrico
    for i, iusi in enumerate(sistema["UHE"]):
        restricoes.append(vf[i] == float(VI[i]) + float(AFL[i]) - vt[i] - vv[i])

    # Atendimento à Demanda
    AD = 0

    for i, usi in enumerate(sistema["UHE"]):
        AD += usi["PROD"] * vt[i]

    for i, usi in enumerate(sistema["UTE"]):
        AD += gt[i]

    AD += deficit[0]

    restricoes.append(AD == sistema["DGer"]["CARGA"][2])

    # Restrições de Canalização
    for i, iusi in enumerate(sistema["UHE"]):
        restricoes.append(vf[i] >= iusi["VMIN"])
        restricoes.append(vf[i] <= iusi["VMAX"])
        restricoes.append(vt[i] >= 0)
        restricoes.append(vt[i] <= iusi["ENGOL"])
        restricoes.append(vv[i] >= 0)

    for i, iusi in enumerate(sistema["UTE"]):
        restricoes.append(gt[i] >= 0)
        restricoes.append(gt[i] <= iusi["CAPAC"])

    restricoes.append(deficit[0] >= 0)

    problema = op(fob, restricoes)

    problema.solve('dense', 'glpk')

    Dger= {
        'Deficit': deficit[0].value(),
        'CMO': restricoes[Num_UHE].multiplier.value,
        "CustoTotal": fob.value()
    }

    lista_uhe = []
    for i, iusi in enumerate(sistema["UHE"]):
        resultado = {"vf": vf[i].value(),
                     "vt": vt[i].value(),
                     "vv": vv[i].value(),
                     "cma": restricoes[i].multiplier.value}
        lista_uhe.append(resultado)

    lista_ute = []
    for i, iusi in enumerate(sistema["UTE"]):
        resultado = {"gt": gt[i].value()}
        lista_ute.append(resultado)

    resultado = {"DGer": Dger,
                 "UHE": lista_uhe,
                 "UTE": lista_ute}

    if imprime:
        print("Custo Total:", fob.value())

        for i, iusi in enumerate(sistema["UHE"]):
            print(vf.name, i, "é", vf[i].value(), "hm3")
            print(vt.name, i, "é", vt[i].value(), "hm3")
            print(vv.name, i, "é", vv[i].value(), "hm3")

        for i, iusi in enumerate(sistema["UTE"]):
            print(gt.name, i, "é", gt[i].value(), "MWmed")

        print(deficit.name, i, "é", deficit[0].value(), "MWmed")

        for i, iusi in enumerate(sistema["UHE"]):
            print("O valor da agua na usina", i, "é", restricoes[i].multiplier.value)

        print("O Custo Marginal da operação é:", restricoes[Num_UHE].multiplier.value)

    return resultado

    passo = 100 / (sistema["DGer"]["Nr_disc"] - 1)

    discretizacoes = product(numpy.arange(0, 100 + passo, passo), repeat=Num_UHE)

    discretizacoes = list(discretizacoes)

    for iest in numpy.arange(sistema["DGer"]["NR_Est"], 0, -1):
        for discretizacao in discretizacoes:
            VI = []
            for i, iusi in enumerate(sistema["UHE"]):
                VI.append(iusi["VMIN"] + (iusi["VMAX"] - iusi["VMIN"]) * discretizacao[i] / 100)
            for icen in numpy.arange(0, sistema["DGer"]["Nr_Cen"]):
                AFL = []
                for i, iusi in enumerate(sistema["UHE"]):
                    AFL.append(iusi["hist_afl"][iest - 1][icen])


lista_uhe = []
lista_ute = []

usina = {
    "Nome": "UHE DO MARCATO",
    "VMAX": 100.,
    "VMIN": 20.,
    "PROD": 0.95,
    "ENGOL": 60.,
    "hist_afl": [
        [23, 14],
        [19, 14],
        [15, 11]
    ]
}

lista_uhe.append(usina)

usina = {
    "Nome": "UHE DO VASCAO",
    "VMAX": 300.,
    "VMIN": 50.,
    "PROD": 0.85,
    "ENGOL": 100.,
}

usina = {
    "Nome": "GT_1",
    "CAPAC": 15.,
    "CUSTO": 10.
}

lista_ute.append(usina)

usina = {
    "Nome": "GT_2",
    "CAPAC": 10.,
    "CUSTO": 25.
}

lista_ute.append(usina)

d_gerais = {
    "CDEF": 500.,
    "CARGA": [50., 50., 50.],
    "Nr_disc": 3,
    "NR_Est": 3,
    "Nr_Cen": 2
}

sistema = {
    "DGer": d_gerais,
    "UHE": lista_uhe,
    "UTE": lista_ute
}

Num_UHE = len(sistema["UHE"])
Num_UTE = len(sistema["UTE"])

vf = variable(Num_UHE, "Volume Final na Usina")
vt = variable(Num_UHE, "Volume Turbinado na Usina")
vv = variable(Num_UHE, "Volume Vertido na Usina")
gt = variable(Num_UTE, "Geração na Usina Térmica")
deficit = variable(1, "Déficit de Energia no Sistema")

# Construção da Função objetivo
fob = 0

for i, iusi in enumerate(sistema["UTE"]):
    fob += iusi["CUSTO"] * gt[i]

fob += sistema["DGer"]["CDEF"] * deficit[0]

for i, iusi in enumerate(sistema["UHE"]):
    fob += 0.01 * vv[i]

# Definiões das Restrições
restricoes = []

# Balanço Hídrico
for i, iusi in enumerate(sistema["UHE"]):
    restricoes.append(vf[i] == 100 + 60 - vt[i] - vv[i])

# Atendimento à Demanda
AD = 0

for i, usi in enumerate(sistema["UHE"]):
    AD += usi["PROD"] * vt[i]

for i, usi in enumerate(sistema["UTE"]):
    AD += gt[i]

AD += deficit[0]

restricoes.append(AD == sistema["DGer"]["CARGA"][2] + 1)

# Restrições de Canalização
for i, iusi in enumerate(sistema["UHE"]):
    restricoes.append(vf[i] >= iusi["VMIN"])
    restricoes.append(vf[i] <= iusi["VMAX"])
    restricoes.append(vt[i] >= 0)
    restricoes.append(vt[i] <= iusi["ENGOL"])
    restricoes.append(vv[i] >= 0)

for i, iusi in enumerate(sistema["UTE"]):
    restricoes.append(gt[i] >= 0)
    restricoes.append(gt[i] <= iusi["CAPAC"])

restricoes.append(deficit[0] >= 0)

problema = op(fob, restricoes)

problema.solve('dense', 'glpk')

print("Custo Total:", fob.value())

for i, iusi in enumerate(sistema["UHE"]):
    print(vf.name, i, "é", vf[i].value(), "hm3")
    print(vt.name, i, "é", vt[i].value(), "hm3")
    print(vv.name, i, "é", vv[i].value(), "hm3")

for i, iusi in enumerate(sistema["UTE"]):
    print(gt.name, i, "é", gt[i].value(), "MWmed")

print(deficit.name, i, "é", deficit[0].value(), "MWmed")

for i, iusi in enumerate(sistema["UHE"]):
    print("O valor da agua na usina", i, "é", restricoes[i].multiplier.value)

print("O Custo Marginal é", restricoes[Num_UHE].multiplier.value)

passo = 100 / (sistema["DGer"]["Nr_disc"] - 1)

discretizacoes = product(numpy.arange(0, 100 + passo, passo), repeat=Num_UHE)

discretizacoes = list(discretizacoes)

print(discretizacoes)

for iest in numpy.arange(sistema["DGer"]["NR_Est"], 0, -1):
    for discretizacao in discretizacoes:
        VI = []
        for i, iusi in enumerate(sistema["UHE"]):
            VI.append(iusi["VMIN"] + (iusi["VMAX"] - iusi["VMIN"]) * discretizacao[i] / 100)
        for icen in numpy.arange(0, sistema["DGer"]["Nr_Cen"]):
            AFL = []
            for i, iusi in enumerate(sistema["UHE"]):
                AFL.append(iusi["hist_afl"][iest - 1][icen])
            print(iest, discretizacao, VI, icen, AFL)
            despacho2(VI, AFL, imprime=False)









