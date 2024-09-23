import os
from multiprocessing import freeze_support
import sys
import flet as ft
from PyPDF2 import PdfReader, PdfWriter
from dotenv import load_dotenv
from scrapper import baixar_arquivos
from ocr import gerar_pdf_nome, ocr_file, separar_arquivos_merge
from utils import verificar_caminho_plataforma, pegar_arquivos_pasta, limpar_pasta, criar_pasta_se_nao_existe
from regex import BUSCA_PADRAO, ANEXO_PADRAO, FINAL_PADRAO

def read_transform_file(pdf_file_path: str, pagina, row, lista, lista_com_anexos):
    pagina.remove(row)
    lista.controls.append(ft.Text(f"Analisando o diário: {pdf_file_path}", size=12))
    row.controls[0] = lista
    pagina.add(row)
    pdf_file_path = verificar_caminho_plataforma(pdf_file_path)
    reader = PdfReader(pdf_file_path)

    for page_num, page in enumerate(reader.pages):
        texto = ocr_file(page_num, pdf_file_path)
        lei_dec_ocorrencias = list(BUSCA_PADRAO.finditer(texto))   
        for i, match in enumerate(lei_dec_ocorrencias):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            if not FINAL_PADRAO.search(texto):
                proxima_pagina = page_num + 1

                while proxima_pagina < len(reader.pages):
                    proxima_pagina_texto = ocr_file(proxima_pagina, pdf_file_path)
                    writer.add_page(reader.pages[proxima_pagina])
                    proxima_pagina += 1

                    ocorrencias_com_anexos = []

                    if ANEXO_PADRAO.search(texto):
                        ocorrencias_com_anexos.append(
                            f"Necessário revisão no arquivo: {match.group()} possui anexo.")

                        pagina.remove(row)
                        aviso = f"Necessário revisão no arquivo: {match.group()} possui anexo."
                        
                        # Verifica se o aviso já existe
                        if not any(control.value == aviso for control in lista_com_anexos.controls):
                            lista_com_anexos.controls.append(ft.Text(aviso, color="green", size=10))

                        row.controls[1] = lista_com_anexos

                        pagina.add(row)

                    if FINAL_PADRAO.search(proxima_pagina_texto):
                        break

            output_folder = ""
            if sys.platform.startswith('linux'):
                output_folder = gerar_pdf_nome(match.group(), pdf_file_path.split("/")[1].split(".")[0])
            else:
                output_folder = gerar_pdf_nome(match.group(), pdf_file_path.split("\\")[1].split(".")[0])

            output_folder = verificar_caminho_plataforma(output_folder)
            if not os.path.exists(output_folder):
                with open(output_folder, 'wb') as output_pdf:
                    writer.write(output_pdf)
                    writer.close()
            else:
                existing_pdf = PdfReader(open(output_folder, 'rb'))
                writer2 = PdfWriter()
                for page in existing_pdf.pages:
                    writer2.add_page(page)
                for page in writer.pages:
                    writer2.add_page(page)
                with open(output_folder, 'wb') as output_pdf:
                    writer2.write(output_pdf)
                    writer2.close()
                writer.close()

            pagina.remove(row)
            lista.controls.append(ft.Text(f"{match.group()} encontrado!", color="green", size=10))
            row.controls[0] = lista
            pagina.add(row)
                
def gerar_arquivos_de_leis_e_decretos(pagina: ft.Page, diario_data: str):
    load_dotenv()
    
    separar_arquivos_merge("encontrados", diario_data)
    diarios = pegar_arquivos_pasta("diarios", diario_data)
    
    row = ft.Row()
    lista = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=100)
    lista_com_anexos: ft.ListView = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True, height=100)
    row.controls.append(lista)
    row.controls.append(lista_com_anexos)
    pagina.add(row)
    pr = ft.ProgressBar()
    pagina.add(pr)
    for pdf_file_path in diarios:
      read_transform_file(pdf_file_path, pagina, row, lista, lista_com_anexos)
    pagina.remove(row)


def main(page: ft.Page):
    
    def buscar(e):
        ano = int(anot.value)
        mes = int(mest.value)
        if not ano or not mes:
            page.add(ft.Text("Digite o ano e mês para buscar os diários oficiais."))
            return
        if int(ano) > 2024 or int(ano) < 2000:
            return
        if int(mes) > 12 or int(mes) < 1:
            return

        page.add(ft.Text(f"Buscando diários oficiais do ano {ano} e mês {mes}..."))
        limpar_pasta(["encontrados", "diarios", "image_output", "resultado"])
        criar_pasta_se_nao_existe(["encontrados", "diarios", "image_output", "resultado"])
        baixar_arquivos(ano, mes)
        gerar_arquivos_de_leis_e_decretos(page, f"{ano}-{mes:02d}")
        page.add(ft.Text("Pesquisa concluída com sucesso!"))

    page.title = "Sistema para extração e organização de leis e decretos"
    anot = ft.TextField(label="Ano", hint_text="Digite o ano: 2005", height=70, max_length=4,
                        input_filter=ft.NumbersOnlyInputFilter(), text_size=12)
    mest = ft.TextField(label="Mês", hint_text="Digite o mês: 1", max_length=2,
                        input_filter=ft.NumbersOnlyInputFilter(), text_size=12)

    page.add(ft.Column([
        ft.Text("Escolha o ano e mês, que iremos buscar os diários oficiais.", size=16),
        anot,
        mest,
        ft.CupertinoFilledButton(
            content=ft.Text("Buscar"),
            opacity_on_click=0.3,
            on_click=buscar,
            height=45,
            padding=10,
            width=100,
        ),
    ]))


if __name__ == "__main__":
    freeze_support()
    ft.app(target=main)
