# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 22:07:47 2019
@author: ALVAROALT & rsanchezavalos
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from time import sleep
import re
from datetime import date
import urllib
from utils import *

headers = {
    'authority': 'https://www.infojobs.com.br/',
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

URL_ofertas = []
country = ('bra')
#Identificar el # de ofertas activas en cada página en un momento dado
URL = 'https://www.infojobs.com.br/empregos.aspx'
#conducting a request of the stated URL above:
page = requests.get(URL, headers=headers)
#specifying a desired format of "page" using the html parser    soup = BeautifulSoup(page.text, "html.parser")
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find(class_ = "num").text
Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
print(Ofertas_Activas)
items_perpage = 16

data_online = []
URL_ofertas = []
details = []

baseline_date = '2019-12-14'
history = pd.read_csv(r'infojobs_{0}_{1}.csv'.format(country, baseline_date))
id_history = history.url_oferta

for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
#for pages in range(16,17):
    URL = 'https://www.infojobs.com.br/empregos.aspx?Page='+format(pages)
    print(URL)
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser
    soup = BeautifulSoup(page.text, "html.parser")
    #Extracting job urls
    for link in soup.findAll(class_="vagaTitle js_vacancyTitle", href=True):
        URL_ofertas.append(link['href'])
    for p in soup.find_all(name="p", attrs={"class": "location2"}):
        data_online.append(p.find(name="span").text.strip())

# Query only new ofertas
ofertas_ = list(set(URL_ofertas) - set(id_history))

#Fetching el contenido de cada oferta
for line in ofertas_:
#for line in URL_ofertas:
    detalle = {}
    detalle["URL_ofertas"] = line    
    detalle["URL_ofertas"] = detalle["URL_ofertas"].replace("\t"," ")
    detalle["URL_ofertas"] = urllib.parse.quote(detalle["URL_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')
    #conducting a request of the stated URL above:
    page = requests.get(detalle["URL_ofertas"], headers=headers, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    #Variables del box derecho (principales variables)
    tipos_box = ["advisor-card advisor-vacancy-content advisor-vacancy-summary"]
    for t in tipos_box:
        try:
            box = soup.find(name="div", class_ = format(t)).find_all("li")
        except:
            pass
    for element in box:
        try:
            a = element.find("span").text.replace(' +',' ').strip()
            detalle[element.find("strong").text] = text_to_unicode(a)
        except:
            pass
    try:
        detalle["Empleador"] = soup.find(id = 'ctl00_phMasterPage_cVacancySummary_aCompany').text.strip()
    except:
        pass
    try:
        detalle["Educacion minima"] = soup.find(id = 'ctl00_phMasterPage_cVacancyManager_cVacancyRequeriments_liMinimunStudies').\
        text.replace('Escolaridade Mínima: ',' ').strip()
    except:
        pass
    try:
        detalle["Idiomas"] = soup.find(id = 'ctl00_phMasterPage_cVacancyManager_cVacancyRequeriments_liLanguage').\
        text.replace(' +',' ').strip()
    except:
        pass
    try:
        detalle["Licencias de conducir"] = soup.find(id = 'ctl00_phMasterPage_cVacancyManager_cVacancyRequeriments_liDrive').\
        text.replace('Habilitação para dirigir ',' ').strip()
        detalle["Licencias de conducir"] = 1
    except:
        pass
    try:
        detalle["Vehículo"] = soup.find(id = 'ctl00_phMasterPage_cVacancyManager_cVacancyRequeriments_liCar').\
        text.strip()
    except:
        pass
    #Variables del box izquierdo (descripcion de la vacantes)
    tipos2 = ["descriptionItems"]
    for t in tipos2:
        try:
            components = soup.find(name = "ol", class_ = format(t))
            for element in components.find_all("li"):
                try:
                    a, b = element.text.split(":")
                    detalle[text_to_unicode(a)] =text_to_unicode(b)
                except:
                    pass
        except:
            pass
    try:
        detalle["descripcion"] = soup.select("#ctl00_phMasterPage_divVacancy > div.advisor-vacancy-content > ol")[0].\
        get_text(strip=True).replace('Área e especialização profissional:', '')
    except:
        pass    

    details.append(detalle)

#Creacion de dataframes y export a CSVs
df = pd.DataFrame(list(zip(data_online, URL_ofertas)),
        columns=["fecha_online", "url_oferta"])

data = pd.DataFrame(details, columns = ["Area e especializacao profissional", "Numero de vagas", "Localidade", 
                                        "Nivel hierarquico","Educacion minima", "Empleador", "Idiomas", 
                                        "Jornada", "Título da vaga", "Salário", "Tipo de contrato", 
                                        "URL_ofertas", "pais", "Licencias de conducir", 'Vehículo', 'descripcion'])
    
data.rename(columns = {'Area e especializacao profissional': 'especialidad', 'Numero de vagas':'cantidad_de_vacantes', 
                       'Nivel hierarquico': 'jerarquia', 'Localidade':'departamento','Educacion Minima':'educacion_minima',
                       'Empleador':'empresa', 'Idiomas':'idiomas','Jornada':'jornada', 'Título da vaga':'puesto', 
                       'Salário':'salario', 'Tipo de contrato':'tipo_de_contrato', 'URL_ofertas':'url_oferta',
                       'Licencias de conducir':'licencia_conducir', 'Vehículo': 'vehiculo', 'descripcion':'descripcion'}, inplace = True)

data = df.merge(data, how="left", on="url_oferta", indicator=True)

data['date'] = date.today()
data['pais'] = country
#data.to_csv(r'infojobs_{0}_{1}.csv'.format(country, date.today()))

history.append(data).to_csv(r'infojobs_{0}_{1}.csv'.format(country, date.today()))

    
    
   
