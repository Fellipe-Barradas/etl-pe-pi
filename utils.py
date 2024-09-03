import sys
import os

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

def verificar_caminho_plataforma(caminho):
    if sys.platform.startswith('linux'):
        return caminho.replace("\\", "/")
    return caminho

def pegar_arquivos_pasta(pasta, diario_data):
    arquivos = []
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.endswith(".pdf") and file.startswith(diario_data):
                arquivos.append(os.path.join(root, file))
    return arquivos
