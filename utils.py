import sys
from typing import List
import os

# Função que retorna o mês por extenso a partir do número do mês.

def mes_extenso_por_numero(mes: str):
    if mes == "01":
        return "Janeiro"
    elif mes == "02":
        return "Fevereiro"
    elif mes == "03":
        return "Março"
    elif mes == "04":
        return "Abril"
    elif mes == "05":
        return "Maio"
    elif mes == "06":
        return "Junho"
    elif mes == "07":
        return "Julho"
    elif mes == "08":
        return "Agosto"
    elif mes == "09":
        return "Setembro"
    elif mes == "10":
        return "Outubro"
    elif mes == "11":
        return "Novembro"
    elif mes == "12":
        return "Dezembro"

# Função que verifica o caminho da plataforma para substituir as barras.
def verificar_caminho_plataforma(caminho):
    if sys.platform.startswith('linux'):
        return caminho.replace("\\", "/")
    return caminho

# Função que pega os arquivos de uma pasta
def pegar_arquivos_pasta(pasta: str, diario_data: str) -> List[str]:
    arquivos = []
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith(".pdf") and file.startswith(diario_data):
                arquivos.append(os.path.join(root, file))
    return arquivos

def criar_pasta_se_nao_existe(pasta: str):
    if not os.path.isdir(pasta):
        os.makedirs(pasta)