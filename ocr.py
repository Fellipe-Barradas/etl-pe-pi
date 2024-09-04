import os
import tempfile
from typing import List
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from PyPDF2 import PdfMerger, PdfReader
from pdf2image import convert_from_path
from utils import mes_extenso_por_numero, verificar_caminho_plataforma

# Realiza o OCR de um arquivo PDF retornando o texto extraído.
def ocr_file(page_num: int, pdf_file_path: str):
    file_name = f"img-{page_num}"
    try: 
        transform_to_image(pdf_file_path, file_name, page_num + 1)
    except FileNotFoundError:
        print("Poppler não encontrado, por favor instale o Poppler.") 
        return ""
    image_path = f"image_output\\{file_name}.jpg"
    image_path = verificar_caminho_plataforma(image_path)
    return ocr_image(image_path)

# Gera o nome do arquivo PDF a partir do decreto-lei e data.
def gerar_pdf_nome(dec_lei: str, data: str):
    dia = data.split("-")[2]
    mes = data.split("-")[1]
    mes_extenso = mes_extenso_por_numero(mes)
    ano = data.split("-")[0]
    numero_lei = dec_lei.split(" ")[2].replace(",", "")
    categoria_documento = dec_lei.split(" ")[0]
    diretorio = f"resultado\\{categoria_documento}\\{ano}\\{mes_extenso}"
    diretorio = verificar_caminho_plataforma(diretorio)
    if not os.path.isdir(diretorio):
        os.makedirs(diretorio)
    if "RESOLUÇÃO" in dec_lei:
        dec_lei = dec_lei.replace("/", "-")
    return f"{diretorio}\\{numero_lei} - {dec_lei} DE {dia} DE {mes_extenso.upper()} DE {ano}.pdf"

# Transforma um arquivo PDF em imagem.
def transform_to_image(file_path: str, file_name: str, page_num: int=0):
    poppler_path = os.getenv("POPPLER_PATH")
    
    if not os.path.exists(poppler_path):
        raise FileNotFoundError("Poppler não encontrado.")
    
    with tempfile.TemporaryDirectory():
        convert_from_path(
            pdf_path=file_path,
            dpi=650,
            jpegopt={'quality': 100},
            output_folder="image_output",
            output_file=file_name,
            first_page=page_num,
            poppler_path=poppler_path,
            single_file=True,
            fmt="JPEG",
        )

# Realiza o OCR de uma imagem retornando o texto extraído.
def ocr_image(file_path: str):
    subscription_key = os.getenv("SUBSCRIPTION_KEY")
    endpoint = os.getenv('ENDPOINT')
    if not subscription_key or not endpoint:
        raise ValueError("Por favor, configure a variável de ambiente SUBSCRIPTION_KEY e ENDPOINT.")
    
    client = ImageAnalysisClient(
        endpoint=endpoint,
        language="por",
        credential=AzureKeyCredential(subscription_key)
    )
    image_data = open(file_path, "rb").read()
    result = client.analyze(image_data, visual_features=[VisualFeatures.read])
    text = ""
    if result.read is not None:
        for line in result.read['blocks']:
            for t in line['lines']:
                text += t['text'] + " "
    return text

# Separa os arquivos PDF de um diário oficial em arquivos menores.
def separar_arquivos_merge(pasta: str, diario_data: str):
    arquivos = []
    for root, dirs, files in os.walk(pasta):
        for file in files:
            data = file.split("_")[1]
            if data not in [a["data"] for a in arquivos] and data.startswith(diario_data):
                arquivos.append({"data": data, "arquivos": []})
            for a in arquivos:
                if a["data"] == data and str(a["data"]).startswith(diario_data):
                    a["arquivos"].append(os.path.join(root, file))
    for data in arquivos:
        merge_pdfs(data["arquivos"], f"diarios\\{data['data']}.pdf")

# Realiza o merge de arquivos PDF.
def merge_pdfs(pdfs: List[str], output: str):
    merger = PdfMerger()
    for filename in pdfs:
        merger.append(PdfReader(open(filename, 'rb')))
    merger.write(output)
    merger.close()