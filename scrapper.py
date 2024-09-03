from datetime import datetime, timedelta
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from dotenv import load_dotenv

"""
Função para baixar os arquivos do mês e ano selecionado diário oficial do Piauí
- ano: ano a ser pesquisado
- mes: mês a ser pesquisado
"""
def baixar_arquivos(ano: int, mes: int):
    load_dotenv()
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    url_base = "http://www.diariooficial.pi.gov.br/diario.php?dia="


    data_pesquisa = datetime(ano, mes, 1)

    while data_pesquisa < datetime(ano, mes+1, 1):
        url = f"{url_base}{data_pesquisa.strftime('%Y%m%d')}"
        driver.get(f"{url}")

        driver.maximize_window()
        links = driver.find_elements(By.XPATH, '//a[@class="texto_diario2"]')
        
        for link in links:
            
            if is_a_valid_link(link):
                link.click()
                link_url = link.get_attribute("href")
                time.sleep(2)
                response = requests.get(link_url)

                if response.status_code == 200:
                    save_pdf(response, link, data_pesquisa)
                else:
                    print(f"Erro ao baixar o arquivo: {link.text}.pdf, na data {data_pesquisa.strftime('%Y%m%d')}")

        data_pesquisa += timedelta(days=1)
        
# Função para verificar se o link é válido para download
def is_a_valid_link(link: webdriver.remote.webelement.WebElement):
    return "Lei" in link.text or "L." in link.text or "Diario Oficial" in link.text

# Função para salvar o arquivo pdf seguindo o formato: diario_ano-mes-dia_leis_pagina
def save_pdf(response: requests.Response, link,  data_pesquisa: datetime):
    pagina = link.text[1:9].replace(' ', '')
    arquivo_nome = f"diario_{data_pesquisa.strftime('%Y-%m-%d')}_leis_{pagina}"
    with open(f"encontrados\\{arquivo_nome}.pdf", "wb") as f:
        f.write(response.content)