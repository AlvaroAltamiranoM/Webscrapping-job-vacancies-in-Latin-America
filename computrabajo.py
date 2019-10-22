# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 22:29:27 2019

@author: ALVAROALT
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from time import sleep
import re
from datetime import date

headers = {
    'authority': 'www.computrabajo.com',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'sec-fetch-site': 'none',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,es-MX;q=0.8,es;q=0.7'
}

#countries = ['hn', 'ni', 'pa', 'do', 'gt']
countries = ['hn']
for country in countries:
    #Identificar el # de ofertas activas en cada página-país en un momento dado
    URL = 'https://www.computrabajo.com.'+format(country)+'/ofertas-de-trabajo/'
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser    soup = BeautifulSoup(page.text, "html.parser")
    soup = BeautifulSoup(page.text, "html.parser")
    Ofertas_Activas = soup.find(class_ = "breadtitle_mvl").text
    Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
    print(country +' = ' + str(Ofertas_Activas))


#Parse todas las páginas y crea CSV con metadata de vacantes
#Definir las columnas de la metadata
# =============================================================================
# for country in countries:
#     jobs = []
#     emp = []
#     ID = []
#     ofertas = []
#     expira = []
#     details = []
#     URL = 'https://www.computrabajo.com.'+format(country)+'/ofertas-de-trabajo/'
#     print(URL)
# =============================================================================
items_perpage = 20

jobs = []
ofertas = []


URL = 'https://www.computrabajo.com.'+format(country)+'/ofertas-de-trabajo/'
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find(class_ = "breadtitle_mvl").text
Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
    
for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
    URL = 'https://www.computrabajo.com.'+format(country)+'/ofertas-de-trabajo/?p='+format(pages)
    print(URL)
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser
    soup = BeautifulSoup(page.text, "html.parser")
    #Extracting job titles
    tipos = ["bRS bClick ", "bRS bClick oD", "bRS bClick oU", "bRS bClick oD oU"]
    for t in tipos:
        for div in soup.find_all(name = 'div',attrs = {'class':format(t)}):
            jobs.append(div.find(class_='js-o-link').text)
    for link in soup.findAll(class_="js-o-link", href=True):
        ofertas.append(link['href'])

#Fetching el contenido de cada oferta
emp = []
local = []
for line in ofertas:
    URL_ofertas = 'https://www.computrabajo.com.'+format(country)+format(line)
    print(URL_ofertas)
    #conducting a request of the stated URL above:
    page = requests.get(URL_ofertas, headers=headers)
# =============================================================================
#     while page.status_code != 200:
#         try:
#             sleep(5)
#             print("sleeping")
#             page = requests.get(URL_ofertas, headers=headers)
#             print ("Response not == to 200.")
#         except Exception as e:
#             print(e) 
# =============================================================================
#specifying a desired format of "page" using the html parser
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        emp.append(soup.find(id = 'urlverofertas').text.strip())
    except Exception as e: 
        emp.append("")
        print(e)
    try:
        local.append(soup.select("div.cm-8.breadcrumb > ol > li:nth-of-type(2) > a")[0].get_text(strip=True))
    except Exception as e: 
        local.append("")
        print(e)

















