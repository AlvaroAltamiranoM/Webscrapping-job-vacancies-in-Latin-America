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
    'authority': 'www.empregos.com.br',
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

country = ['bra']
items_perpage = 20

jobs = []
URL_ofertas = []
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

jobs = []
URL_ofertas = []
#for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
for pages in range(1,2):
    URL = URL+'?Page='+format(pages)
    print(URL)
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser
    soup = BeautifulSoup(page.text, "html.parser")
    #Extracting job urls
    for link in soup.findAll(class_="vagaTitle js_vacancyTitle", href=True):
        URL_ofertas.append(link['href'])

    #Fetching el contenido de cada oferta
    details = []
    for line in URL_ofertas:
        detalle = {}
        detalle["URL_ofertas"] = 'https://www.infojobs.com.br/empregos.aspx'
        detalle["URL_ofertas"] = detalle["URL_ofertas"]
        detalle["URL_ofertas"] = detalle["URL_ofertas"].replace("\t"," ")
        detalle["URL_ofertas"] = urllib.parse.quote(detalle["URL_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')
        #conducting a request of the stated URL above:
        page = requests.get(detalle["URL_ofertas"], headers=headers, verify=False)
        soup = BeautifulSoup(page.text, "html.parser")
        #detalle["Sopa_de_queso"] = soup
        ctl00_phMasterPage_cVacancySummary_litVacancyTitle
        try:
            aux = soup.find(class_="cm-8 box detalle_oferta box_image").find("h1").text
            detalle["Puesto"] = re.sub("\r|\n|\s\s+",'',aux)
        except:
            pass
        #Nombre del puesto y local (departamento)
        try:
            detalle["Departamento"] = soup.select("div.cm-8.breadcrumb > ol > li:nth-of-type(2) > a")[0].get_text(strip=True)
        except:
            pass
        try:
            detalle["Empleador"] = soup.find(id = 'urlverofertas').text.strip()
        except:
            pass
        tipos_box = ["box box_r", "boxWhite ocultar_mvl p30"]
        for t in tipos_box:
            try:
                box = soup.find(name="section", class_ = format(t)).find_all("li")
            except:
                pass
        for element in box:
            try:
                if country=='cl' or country=='ar' or country=='mx' or country=='co':
                    a = element.find_all("p")[1].text.replace(' +',' ').strip()
                    detalle[element.find(class_ = "fw_b fs15 mt10").text] = text_to_unicode(a)                  
                else:
                    a = element.find("p").text.replace(' +',' ').strip()
                    detalle[element.find("h3").text] = text_to_unicode(a)
            except:
                pass
        tipos2 = ["cm-12 box_i bWord", "cm-12 box_i", "boxWhite fl w_100 detail_of mb20 bWord"]
        for t in tipos2:
            try:
                if country=='cl' or country=='ar' or country=='mx' or country=='co':
                    a = soup.find(name="section", class_ =format(t)).find_all("li")[0].text.\
                    replace('\nDescripción\r\n ', '').strip()
                else:
                    a = soup.find(name="div", class_ =format(t)).find_all("li")[0].text.\
                    replace('\nDescripción\r\n ', '').strip()
                detalle["descripcion"] = text_to_unicode(a)
            except:
                pass
        for t in tipos2:
            try:
                if country=='cl' or country=='ar' or country=='mx' or country=='co':
                    components = soup.find(name = "section",class_ = format(t))
                else:
                    components = soup.find(name = "div",class_ = format(t))
                for element in components.find_all("li"):
                    try:
                        if element.find("h3") != None:
                            pass
                        else:
                            a, b = element.text.split(":")
                            detalle[text_to_unicode(a)] =text_to_unicode(b)
                    except:
                        pass
            except:
                pass
        details.append(detalle)

    #Create and merge dataframes
    df = pd.DataFrame(list(zip(jobs,URL_ofertas)), columns=["puesto2", "url_oferta"])

    data = pd.DataFrame(details, columns = ["Anos de experiencia", "Cantidad de vacantes", "Departamento", 
                                            "Disponibilidad de cambio de residencia","Disponibilidad de viajar",
                                            "Educacion minima", "Empleador", "Fecha de contratacion",
                                            "Idiomas", "Jornada", "Licencias de conducir", "Puesto", "Salario",
                                            "Tipo de contrato", "URL_ofertas", "descripcion"])

    data.rename(columns = {'Anos de experiencia':'anios_de_experiencia', 'Cantidad de Vacantes':'cantidad_de_vacantes', 
                           'Departamento':'departamento', 'Disponibilidad de Cambio de Residencia':'cambio_de_residencia',
                           'Disponibilidad de Viajar':'disponibilidad_viajes', 'Educacion Minima':'educacion_minima', 
                           'Empleador':'empresa', 'Fecha de Contratacion':'fecha_de_contratacion', 'Idiomas':'idiomas', 
                           'Jornada':'jornada', 'Licencias de conducir':'licencia_conducir', 'Puesto':'puesto', 'Salario':'salario',
                           'Tipo de contrato':'tipo_de_cotrato', 'URL_ofertas':'url_oferta', 'descripcion':'descripcion'}, inplace = True)
    #data = data.drop(columns = ['puesto','Localización'])
    data['puesto'] = df['puesto2']
    data['date'] = date.today()
    data['pais'] = country
    data.to_csv(r'computrabajo_{0}_{1}.csv'.format(country, date.today()))
    

    
    
