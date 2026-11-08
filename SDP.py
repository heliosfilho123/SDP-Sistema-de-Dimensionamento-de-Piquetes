# ============================================================
# SDP - SISTEMA DE DIMENSIONAMENTO DE PIQUETES
# Versao integrada inicial
# Regiao de referencia: Cerrado brasileiro
# Foco: gado leiteiro
#
# ATENCAO:
# - O banco cientifico contem um experimento local da EPAMIG.
# - A tabela de consumo de vacas em lactacao e preliminar.
# - O programa NAO estima hectares necessarios sem dados
#   validados de consumo total e forragem aproveitavel.
# ============================================================

import math


# ------------------------------------------------------------
# 1. BANCO CIENTIFICO DE FORRAGEIRAS
# ------------------------------------------------------------

EXPERIMENTOS_FORRAGEIRAS = [
    {
        "id": "EPAMIG_2004",
        "instituicao": "EPAMIG",
        "regiao": "Cerrado - Prudente de Morais/MG",
        "periodo_experimental": "Agosto/2002 a Marco/2003",
        "solo": "Latossolo Vermelho-Amarelo, textura argilosa",
        "sistemas": ["Irrigado", "Sequeiro"],
        "manejo": {
            "frequencia_corte_dias": "35 a 42",
            "nitrogenio_manutencao_kg_ha": 200,
            "observacao": (
                "Adubacao de plantio e manutencao; "
                "irrigacao por aspersao integral na seca "
                "e suplementar nas aguas."
            )
        },
        "resultados": [
            {"cultivar": "Pioneiro", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Irrigado",
             "valor": 9319, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Pioneiro", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Sequeiro",
             "valor": 4077, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Tanzânia", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Irrigado",
             "valor": 5807, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Tanzânia", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Sequeiro",
             "valor": 1333, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Marandu", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Irrigado",
             "valor": 3921, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Marandu", "epoca": "Seca",
             "periodo": "Agosto a Outubro/2002", "sistema": "Sequeiro",
             "valor": 976, "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Pioneiro", "epoca": "Aguas",
             "periodo": "Novembro/2002 a Marco/2003",
             "sistema": "Media entre sistemas", "valor": 17767,
             "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Tanzânia", "epoca": "Aguas",
             "periodo": "Novembro/2002 a Marco/2003",
             "sistema": "Media entre sistemas", "valor": 12684,
             "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
            {"cultivar": "Marandu", "epoca": "Aguas",
             "periodo": "Novembro/2002 a Marco/2003",
             "sistema": "Media entre sistemas", "valor": 12553,
             "unidade": "kg MS/ha",
             "tipo": "Producao acumulada no periodo"},
        ],
        "observacoes": [
            "Nas aguas, os valores sao medias por cultivar entre sistemas.",
            "Resultados locais; nao representam produtividade universal.",
            "Producao experimental nao equivale a forragem consumivel."
        ],
        "fonte": "Viana et al. (2004)",
        "status": "Referencia experimental cadastrada",
        "apto_para_calculo_direto": False
    }
]


def validar_banco():
    erros = []
    for exp in EXPERIMENTOS_FORRAGEIRAS:
        if not exp.get("id") or not exp.get("fonte"):
            erros.append("Experimento sem identificacao ou fonte.")
        for resultado in exp.get("resultados", []):
            if resultado.get("valor", 0) <= 0:
                erros.append(f"Valor invalido em {exp.get('id')}.")
    return erros


def consultar_banco():
    print("\n========== BANCO CIENTIFICO ==========")
    for exp in EXPERIMENTOS_FORRAGEIRAS:
        print(f"\n{exp['id']} | {exp['regiao']}")
        print(f"Periodo: {exp['periodo_experimental']}")
        print(f"Solo: {exp['solo']}")
        print(f"Fonte: {exp['fonte']}")
        for r in exp["resultados"]:
            print(
                f"- {r['cultivar']} | {r['epoca']} | {r['sistema']}: "
                f"{r['valor']} {r['unidade']} ({r['periodo']})"
            )
        print("Observacao: dados experimentais, nao usados isoladamente "
              "para recomendar hectares.")


# ------------------------------------------------------------
# 2. REFERENCIA PRELIMINAR DE CONSUMO
# Valores percentuais de PV para vacas em lactacao.
# Confirmar a tabela e sua fonte antes de uso zootecnico.
# ------------------------------------------------------------

TABELA_CONSUMO = {
    10: [2.7, 2.4, 2.2, 2.0, 1.9],
    15: [3.2, 2.8, 2.6, 2.3, 2.2],
    20: [3.6, 3.2, 2.9, 2.6, 2.4],
    25: [4.0, 3.5, 3.2, 2.9, 2.7],
    30: [4.4, 3.9, 3.5, 3.2, 2.9],
    35: [5.0, 4.2, 3.7, 3.4, 3.1],
    40: [5.5, 4.6, 4.0, 3.6, 3.3]
}
PESOS_REFERENCIA = [400, 500, 600, 700, 800]

ALIMENTOS_REFERENCIA = {
    "silagem de milho": 30.92,
    "silagem de sorgo": 30.82,
    "silagem de cana": 25.85,
    "silagem de capim-elefante": 26.81
}

CATEGORIAS = [
    "Vacas em lactacao",
    "Vacas secas",
    "Novilhas de 1 a 2 anos",
    "Novilhas acima de 2 anos",
    "Bezerras ate 1 ano"
]

FORRAGEIRAS = [
    "Marandu", "Pioneiro", "Tanzânia", "Mombaça", "Tifton 85",
    "Basilisk", "Coastcross", "Colonião", "Tobiatã",
    "Grama-estrela", "Outro", "Nao sei informar"
]


# ------------------------------------------------------------
# 3. FUNCOES DE ENTRADA
# ------------------------------------------------------------

def ler_texto(pergunta, permitir_vazio=False):
    while True:
        valor = input(pergunta).strip()
        if valor or permitir_vazio:
            return valor
        print("Essa informacao nao pode ficar vazia.")


def ler_numero(pergunta, minimo=0, permitir_zero=True):
    while True:
        try:
            valor = float(input(pergunta).replace(",", "."))
            if valor < minimo or (not permitir_zero and valor == 0):
                print(f"Informe um valor valido (minimo: {minimo}).")
                continue
            return valor
        except ValueError:
            print("Digite um numero valido. Exemplo: 12 ou 12,5.")


def ler_inteiro(pergunta, minimo=0):
    while True:
        try:
            valor = int(input(pergunta))
            if valor < minimo:
                print(f"Informe um numero igual ou maior que {minimo}.")
                continue
            return valor
        except ValueError:
            print("Digite um numero inteiro valido.")


def escolher_opcao(pergunta, opcoes):
    while True:
        print(f"\n{pergunta}")
        for i, opcao in enumerate(opcoes, 1):
            print(f"{i} - {opcao}")
        escolha = ler_inteiro("Escolha: ", 1)
        if 1 <= escolha <= len(opcoes):
            return opcoes[escolha - 1]
        print("Opcao invalida.")


def perguntar_sim_nao(pergunta):
    return escolher_opcao(pergunta, ["Sim", "Nao", "Nao sei informar"])


# ------------------------------------------------------------
# 4. CADASTRO DO PRODUTOR E DA PROPRIEDADE
# ------------------------------------------------------------

def cadastrar_propriedade():
    print("\n========== PROPRIEDADE ==========")
    produtor = ler_texto("Nome do produtor: ", permitir_vazio=True)
    propriedade = ler_texto("Nome da propriedade: ", permitir_vazio=True)
    municipio = ler_texto("Municipio/UF: ", permitir_vazio=True)
    return {
        "produtor": produtor,
        "propriedade": propriedade,
        "municipio": municipio
    }


# ------------------------------------------------------------
# 5. CADASTRO DO REBANHO
# ------------------------------------------------------------

def cadastrar_rebanho():
    print("\n========== CADASTRO DO REBANHO ==========")
    rebanho = {}

    for categoria in CATEGORIAS:
        print(f"\n--- {categoria} ---")
        quantidade = ler_inteiro("Quantos animais dessa categoria? ", 0)
        if quantidade == 0:
            continue

        peso = ler_numero("Peso aproximado de cada animal (kg): ", 1,
                          permitir_zero=False)
        dados = {"quantidade": quantidade, "peso_medio": peso}

        if categoria == "Vacas em lactacao":
            dados["leite_dia"] = ler_numero(
                "Producao media de leite por vaca (litros/dia): ", 0
            )
        rebanho[categoria] = dados

    return rebanho


# ------------------------------------------------------------
# 6. CADASTRO DA ALIMENTACAO
# ------------------------------------------------------------

def cadastrar_alimentacao(rebanho):
    print("\n========== ALIMENTACAO FORNECIDA ==========")
    alimentacao = {}

    for categoria in rebanho:
        print(f"\nAlimentos fornecidos para: {categoria}")
        alimentacao[categoria] = []

        while True:
            nome = ler_texto(
                "Nome do alimento (ou FIM para encerrar): "
            )
            if nome.casefold() == "fim":
                break

            quantidade = ler_numero(
                "Kg fornecidos por animal por dia (como oferecido): ", 0
            )

            chave = nome.casefold()
            if chave in ALIMENTOS_REFERENCIA:
                percentual_ms = ALIMENTOS_REFERENCIA[chave]
                print(
                    f"Usando valor de referencia de {percentual_ms:.2f}% "
                    "de materia seca. Pode variar conforme o alimento."
                )
            else:
                percentual_ms = ler_numero(
                    "Teor de materia seca em % (0 se nao souber): ", 0
                )
                if percentual_ms > 100:
                    print("O percentual nao pode ser maior que 100.")
                    continue

            alimentacao[categoria].append({
                "nome": nome,
                "kg_por_animal": quantidade,
                "percentual_ms": percentual_ms
            })

    return alimentacao


def calcular_suplementacao(rebanho, alimentacao):
    resultados = {}

    for categoria, alimentos in alimentacao.items():
        n_animais = rebanho[categoria]["quantidade"]
        total_ms_animal = 0.0
        total_ms_grupo = 0.0
        itens = []

        for alimento in alimentos:
            percentual = alimento["percentual_ms"]
            if percentual <= 0:
                itens.append({
                    "nome": alimento["nome"],
                    "kg_por_animal": alimento["kg_por_animal"],
                    "ms_conhecida": False
                })
                continue

            ms_animal = alimento["kg_por_animal"] * percentual / 100
            ms_grupo = ms_animal * n_animais
            total_ms_animal += ms_animal
            total_ms_grupo += ms_grupo
            itens.append({
                "nome": alimento["nome"],
                "kg_por_animal": alimento["kg_por_animal"],
                "percentual_ms": percentual,
                "ms_animal": ms_animal,
                "ms_grupo": ms_grupo,
                "ms_conhecida": True
            })

        resultados[categoria] = {
            "itens": itens,
            "ms_animal": total_ms_animal,
            "ms_grupo": total_ms_grupo
        }

    return resultados


# ------------------------------------------------------------
# 7. ESTIMATIVA PRELIMINAR PARA VACAS EM LACTACAO
# ------------------------------------------------------------

def interpolar(x, x1, x2, y1, y2):
    if x1 == x2:
        return y1
    return y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)


def estimar_consumo_vaca(peso, leite):
    if not (400 <= peso <= 800 and 10 <= leite <= 40):
        return None

    pesos = PESOS_REFERENCIA
    producoes = sorted(TABELA_CONSUMO)

    p1 = next((pesos[i] for i in range(len(pesos)-1)
               if pesos[i] <= peso <= pesos[i+1]), None)
    if p1 is None:
        return None
    p2 = pesos[pesos.index(p1) + 1]

    l1 = next((producoes[i] for i in range(len(producoes)-1)
               if producoes[i] <= leite <= producoes[i+1]), None)
    if l1 is None:
        return None
    l2 = producoes[producoes.index(l1) + 1]

    i1, i2 = pesos.index(p1), pesos.index(p2)
    c_p1 = interpolar(leite, l1, l2,
                      TABELA_CONSUMO[l1][i1],
                      TABELA_CONSUMO[l2][i1])
    c_p2 = interpolar(leite, l1, l2,
                      TABELA_CONSUMO[l1][i2],
                      TABELA_CONSUMO[l2][i2])
    return interpolar(peso, p1, p2, c_p1, c_p2)


def calcular_demanda_vacas(rebanho):
    categoria = "Vacas em lactacao"
    if categoria not in rebanho:
        return None

    dados = rebanho[categoria]
    percentual = estimar_consumo_vaca(
        dados["peso_medio"], dados["leite_dia"]
    )
    if percentual is None:
        return None

    consumo_animal = dados["peso_medio"] * percentual / 100
    return {
        "percentual_pv": percentual,
        "consumo_animal": consumo_animal,
        "consumo_grupo": consumo_animal * dados["quantidade"],
        "status": "Estimativa preliminar; confirmar referencia tecnica"
    }


# ------------------------------------------------------------
# 8. CADASTRO DA PASTAGEM
# ------------------------------------------------------------

def cadastrar_pastagem():
    print("\n========== PASTAGEM ==========")
    capim = escolher_opcao("Qual capim existe na propriedade?", FORRAGEIRAS)
    if capim == "Outro":
        capim = ler_texto("Qual capim? ")

    epoca = escolher_opcao(
        "Em qual periodo deseja avaliar a pastagem?",
        ["Aguas", "Seca", "Ano inteiro", "Nao sei informar"]
    )
    irrigacao = perguntar_sim_nao("A pastagem recebe irrigacao?")
    adubacao = perguntar_sim_nao("A pastagem recebe adubacao?")
    condicao = escolher_opcao(
        "Como esta o pasto atualmente?",
        [
            "Baixo e com falhas",
            "Quantidade razoavel de capim",
            "Bem formado e com bastante capim",
            "Nao sei informar"
        ]
    )
    area = ler_numero(
        "Quantos hectares de pastagem possui? (0 se nao souber): ", 0
    )

    return {
        "capim": capim,
        "epoca": epoca,
        "irrigacao": irrigacao,
        "adubacao": adubacao,
        "condicao": condicao,
        "area_ha": area
    }


# ------------------------------------------------------------
# 9. DIMENSIONAMENTO INICIAL DOS PIQUETES
# ------------------------------------------------------------

def dimensionar_piquetes(pastagem):
    print("\n========== DIVISAO DOS PIQUETES ==========")
    sabe_ocupacao = perguntar_sim_nao(
        "Voce sabe quantos dias os animais ficam em cada piquete?"
    )
    if sabe_ocupacao != "Sim":
        return None

    ocupacao = ler_numero(
        "Quantos dias os animais ficam em cada piquete? ",
        0, permitir_zero=False
    )

    sabe_descanso = perguntar_sim_nao(
        "Voce sabe quantos dias o capim precisa para se recuperar?"
    )
    if sabe_descanso != "Sim":
        return None

    descanso = ler_numero(
        "Quantos dias o capim descansa entre pastejos? ",
        0, permitir_zero=False
    )

    numero = math.ceil(descanso / ocupacao + 1)

    resultado = {
        "ocupacao_dias": ocupacao,
        "descanso_dias": descanso,
        "numero_piquetes": numero,
        "area_total_ha": pastagem["area_ha"]
    }

    if pastagem["area_ha"] > 0:
        resultado["area_media_piquete_ha"] = (
            pastagem["area_ha"] / numero
        )

    return resultado


# ------------------------------------------------------------
# 10. RELATORIO
# ------------------------------------------------------------

def gerar_relatorio(propriedade, rebanho, alimentacao,
                    suplementacao, demanda, pastagem, piquetes):

    print("\n" + "=" * 58)
    print("                 RELATORIO SDP")
    print("=" * 58)

    print("\nPROPRIEDADE")
    print("Produtor:", propriedade["produtor"] or "Nao informado")
    print("Propriedade:", propriedade["propriedade"] or "Nao informado")
    print("Municipio/UF:", propriedade["municipio"] or "Nao informado")

    total_animais = sum(d["quantidade"] for d in rebanho.values())
    print(f"\nREBANHO: {total_animais} animais")
    for categoria, dados in rebanho.items():
        print(
            f"- {categoria}: {dados['quantidade']} animais; "
            f"peso medio {dados['peso_medio']:.1f} kg"
        )
        if "leite_dia" in dados:
            print(f"  Leite: {dados['leite_dia']:.1f} L/vaca/dia")

    print("\nSUPLEMENTACAO")
    for categoria, dados in suplementacao.items():
        print(f"\n{categoria}:")
        for item in dados["itens"]:
            if item["ms_conhecida"]:
                print(
                    f"- {item['nome']}: {item['kg_por_animal']:.2f} kg "
                    f"oferecidos/animal/dia; "
                    f"{item['ms_animal']:.2f} kg MS/animal/dia"
                )
            else:
                print(
                    f"- {item['nome']}: quantidade registrada, "
                    "mas conversao para materia seca pendente."
                )
        print(
            f"Materia seca conhecida do grupo: "
            f"{dados['ms_grupo']:.2f} kg/dia"
        )

    print("\nDEMANDA ALIMENTAR")
    if demanda:
        print(
            f"Vacas em lactacao: {demanda['consumo_animal']:.2f} "
            "kg MS/vaca/dia (estimativa preliminar)."
        )
        print(
            f"Grupo: {demanda['consumo_grupo']:.2f} kg MS/dia."
        )
        print("ATENCAO:", demanda["status"])
    else:
        print(
            "Consumo de vacas em lactacao nao estimado: "
            "faixa de peso/producao fora da tabela ou grupo ausente."
        )
    print(
        "Consumo das vacas secas, novilhas e bezerras ainda nao "
        "foi calculado por modelo validado."
    )

    print("\nPASTAGEM")
    print("Capim:", pastagem["capim"])
    print("Periodo:", pastagem["epoca"])
    print("Irrigacao:", pastagem["irrigacao"])
    print("Adubacao:", pastagem["adubacao"])
    print("Condicao visual:", pastagem["condicao"])
    if pastagem["area_ha"] > 0:
        print(f"Area existente: {pastagem['area_ha']:.2f} ha")
    else:
        print("Area existente: nao informada")

    print("\nPIQUETES")
    if piquetes:
        print(f"Numero calculado: {piquetes['numero_piquetes']}")
        print(f"Ocupacao: {piquetes['ocupacao_dias']} dia(s)")
        print(f"Descanso informado: {piquetes['descanso_dias']} dia(s)")
        if "area_media_piquete_ha" in piquetes:
            print(
                "Area media por piquete dentro da area cadastrada: "
                f"{piquetes['area_media_piquete_ha']:.2f} ha"
            )
        else:
            print("Area por piquete: indisponivel; area total nao informada.")
    else:
        print(
            "Numero de piquetes nao calculado: faltam os dias "
            "de ocupacao e/ou descanso."
        )

    print("\nLIMITACOES E PROXIMOS AJUSTES")
    print(
        "1. O SDP ainda nao calcula hectares necessarios para sustentar "
        "todo o rebanho."
    )
    print(
        "2. A producao experimental do banco nao foi convertida em "
        "forragem efetivamente consumivel."
    )
    print(
        "3. A tabela de consumo de vacas em lactacao e preliminar; "
        "validar fonte e adequacao antes de uso tecnico."
    )
    print(
        "4. Teores de materia seca de alimentos sao referencias "
        "aproximadas, salvo quando informados por analise."
    )
    print(
        "5. A formula de piquetes considera descanso e ocupacao "
        "informados; o manejo deve ser validado para a forrageira."
    )
    print("=" * 58)


# ------------------------------------------------------------
# 11. PROGRAMA PRINCIPAL
# ------------------------------------------------------------

def main():
    print("\n" + "=" * 58)
    print(" SDP - SISTEMA DE DIMENSIONAMENTO DE PIQUETES")
    print(" Versao integrada inicial | Gado leiteiro | Cerrado")
    print("=" * 58)

    erros = validar_banco()
    if erros:
        print("\nProblemas no banco cientifico:")
        for erro in erros:
            print("-", erro)
        return

    propriedade = cadastrar_propriedade()
    rebanho = cadastrar_rebanho()

    if not rebanho:
        print("\nNenhum animal cadastrado. Encerrando.")
        return

    alimentacao = cadastrar_alimentacao(rebanho)
    suplementacao = calcular_suplementacao(rebanho, alimentacao)
    demanda = calcular_demanda_vacas(rebanho)
    pastagem = cadastrar_pastagem()
    piquetes = dimensionar_piquetes(pastagem)

    gerar_relatorio(
        propriedade, rebanho, alimentacao,
        suplementacao, demanda, pastagem, piquetes
    )

    print("\nConsulta ao banco cientifico:")
    consultar = perguntar_sim_nao(
        "Deseja visualizar os experimentos cadastrados?"
    )
    if consultar == "Sim":
        consultar_banco()

    print("\nCadastro concluido. Obrigado por utilizar o SDP!")


if __name__ == "__main__":
    main()
