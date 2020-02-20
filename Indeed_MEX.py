# -*- coding: utf-8 -*-
"""
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
from ingest.utils import *

headers = {
    'authority': 'www.indeed.com.mx',
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

items_perpage = 50
#baseline_date = '2020-02-12'

jobs = []
URL_ofertas = []
URL_ofertas2 = []
details = []

#Load history
#history = pd.read_csv(r'computrabajo_{0}.csv'.format(baseline_date))
#id_history = history.url_oferta

municipios = pd.read_csv(r'mex_municipios.csv', encoding = 'latin-1')
munis = ([municipios['nom_mun']+', '+municipios['nom_abr']])

#Identificar el # de ofertas activas en cada página
URL = 'https://www.indeed.com.mx/trabajo?q=&l=México'
#conducting a request of the stated URL above:
page = requests.get(URL, headers=headers)
#specifying a desired format of "page" using the html parser
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find(id = "searchCountPages").text
Ofertas_Activas = str(int(''.join(filter(str.isdigit, Ofertas_Activas))))[-6:]
print(str(Ofertas_Activas))


for muni in munis[0][:2]:
    for pages in range(0,100,50):
    #for pages in range(0,int((int(Ofertas_Activas)/items_perpage)+2),50):
#for pages in range(0,100,50):
        URL = 'https://www.indeed.com.mx/jobs?q=&l='+format(muni)+'&sort=date&filter=0&limit=50&start='
        URL = URL+format(pages)
        print(URL)
        #conducting a request of the stated URL above:
        page = requests.get(URL, headers=headers)
        #specifying a desired format of "page" using the html parser
        soup = BeautifulSoup(page.text, "html.parser")
        #Extracting job titles
        for div in soup.find_all(name="div", attrs={"class": "title"}):
            jobs.append(div.find(name="a").text.strip())      
            URL_ofertas.append(div.find(name="a")['href'])    
    
    """"
        for div in soup.find_all(name="div", attrs={"class": "result-link-bar"}):
            data_online.append(div.find(class_="date ").text.strip())
        for div in soup.find_all(name="span", attrs={"class": "company"}):
            Empleador.append(div.text.strip())
    """
    
# Query only new ofertas
#ofertas_ = list(set(URL_ofertas) - set(id_history))

#Fetching el contenido de cada oferta
detalle = {}

#for line in ofertas_:
for line in URL_ofertas:
    detalle = {}
    detalle["URL_ofertas2"] = line # para usar en merge de dataframes
    detalle["URL_ofertas"] = 'https://www.indeed.com.mx'
    detalle["URL_ofertas"] = detalle["URL_ofertas"]+format(line)+'&sort=date'
    detalle["URL_ofertas"] = detalle["URL_ofertas"].replace("\t"," ")
    detalle["URL_ofertas"] = urllib.parse.quote(detalle["URL_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')

    #conducting a request of the stated URL above:
    print(detalle["URL_ofertas"])
    page = requests.get(detalle["URL_ofertas"], headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    #detalle["Sopa_de_queso"] = soup
    #Nombre del puesto y local (departamento)
    try:
        aux = soup.find(class_="icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title").text.strip()
        detalle["puesto"] = re.sub("\r|\n|\s\s+",'',aux)
    except:
        pass
    try:
        detalle["localidad"] = soup.find(class_="jobsearch-JobMetadataHeader-iconLabel").text.strip()
    except:
        pass
    try:
        detalle["empresa"] = soup.find(class_ = 'icl-u-lg-mr--sm icl-u-xs-mr--xs').text.strip()
    except:
        pass
    try:
        detalle["data_online"] = soup.find(class_ = 'jobsearch-JobMetadataFooter').text.strip()
        detalle["data_online"] = detalle["data_online"].split("-")
        detalle["data_online"] = detalle["data_online"][1].strip()
    except:
        pass
    
    components = soup.find(class_ = 'jobsearch-jobDescriptionText')
    for element in components.find_all('div'):
        try:     
            temp = element.text.strip()
            a,b = temp.split(':')
            detalle[text_to_unicode(a)] =text_to_unicode(b)
        except:
            pass

    
    details.append(detalle)
  

    tipos_box = ["boxWhite ocultar_mvl p30"]
    for t in tipos_box:
        try:
            box = soup.find(name="section", class_ = format(t)).find_all("li")
        except:
            pass
    for element in box:
        try:
            a = element.find_all("p")[1].text.replace(' +',' ').strip()
            detalle[element.find(class_ = "fw_b fs15 mt10").text] = text_to_unicode(a)                  
        except:
            pass
    tipos2 = ["cm-12 box_i bWord", "cm-12 box_i", "boxWhite fl w_100 detail_of mb20 bWord"]
    for t in tipos2:
        try:
            a = soup.find(name="section", class_ =format(t)).find_all("li")[0].text.\
            replace('\nDescripción\r\n ', '').strip()
        except:
            pass
    for t in tipos2:
        try:
            components = soup.find(name = "section",class_ = format(t))
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
    #CAMPOS DE LA EMPRESA, RAMA DE ACTIVIDAD Y TAMANYO
    detalle["URL_ofertas-empresa"] = detalle["URL_ofertas"]+'-empresa'
    page = requests.get(detalle["URL_ofertas-empresa"], headers=headers)        
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        detalle["rama_de_actividad"] = soup.find(class_ = 'rComp mt10').find_all("span")[3].text.strip()
    except:
        pass
    try:
        detalle["tamanio_empresa"] = soup.find(class_ = 'rComp mt10').find_all("span")[5].text.strip()
    except:
        pass
    
    details.append(detalle)


#Create and merge dataframes

df = pd.DataFrame(list(zip(jobs, URL_ofertas)), 
                  columns=["puesto2", "url_oferta"])

data = pd.DataFrame(details, columns = ["Puesto","Anos de experiencia", "Cantidad de vacantes", "Departamento", 
                                        "Disponibilidad de cambio de residencia","Disponibilidad de viajar",
                                        "Educacion minima", "Empleador", "Fecha de contratacion",
                                        "Idiomas", "Jornada", "Licencias de conducir",  "Salario",
                                        "Tipo de contrato", "URL_ofertas2", "descripcion", "rama_de_actividad",
                                        "tamanio_empresa", "Edad", "Sexo", "Posiciones a cubrir", "Genero"])

data.rename(columns = {'Anos de experiencia':'anios_de_experiencia', 'Cantidad de vacantes':'cantidad_de_vacantes', 
                       'Departamento':'departamento', 'Disponibilidad de cambio de residencia':'cambio_de_residencia',
                       'Disponibilidad de viajar':'disponibilidad_viajes', 'Educacion minima':'educacion_minima', 
                       'Empleador':'empresa', 'Fecha de contratacion':'fecha_de_contratacion', 'Idiomas':'idiomas', 
                       'Jornada':'jornada', 'Licencias de conducir':'licencia_conducir', 'Puesto':'puesto', 'Salario':'salario',
                       'Tipo de contrato':'tipo_de_contrato', 'URL_ofertas2':'url_oferta', 'descripcion':'descripcion',
                       'Edad':'edad', 'Sexo': 'sexo', 'Genero':'genero'}, inplace = True)

data['puesto'] = df['puesto2'] 
    
data['date'] = date.today()

data = data.merge(df, how="left", on="url_oferta", indicator=True)
data = data.drop(columns = ['puesto2'])
  
#data.to_csv(r'computrabajo_{0}.csv'.format(date.today()))  

#history.append(data, sort = True, ignore_index=True).to_csv(r'indeed_{0}.csv'.format(date.today()))

