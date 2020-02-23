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
#baseline_date = '2020-02-23'

jobs = []
url_ofertas = []
url_ofertas2 = []
details = []

#Load history
history = pd.read_csv(r'indeed_{0}.csv'.format(baseline_date))
id_history = history.url_oferta

estados_list = pd.read_csv(r'mex_estados.csv', encoding = 'latin-1')
estados = estados_list['nom_ent']

#Identificar el # de ofertas activas en cada página
URL = 'https://www.indeed.com.mx/trabajo?q=&l=México'
#conducting a request of the stated URL above:
page = requests.get(URL, headers=headers)
#specifying a desired format of "page" using the html parser
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find(id = "searchCountPages").text
Ofertas_Activas = str(int(''.join(filter(str.isdigit, Ofertas_Activas))))[-6:]
print(str(Ofertas_Activas))


for estado in estados:
    for pages in range(0,950,50):
    #for pages in range(0,int((int(Ofertas_Activas)/items_perpage)+2),50):
#for pages in range(0,100,50):
        URL = 'https://www.indeed.com.mx/jobs?q=&l='+format(estado)+'&sort=date&filter=0&limit=50&start='
        URL = URL+format(pages)
        print(URL)
        #conducting a request of the stated URL above:
        page = requests.get(URL, headers=headers)
        #specifying a desired format of "page" using the html parser
        soup = BeautifulSoup(page.text, "html.parser")
        #Extracting job titles
        for div in soup.find_all(name="div", attrs={"class": "title"}):
            jobs.append(div.find(name="a").text.strip())      
            url_ofertas.append(div.find(name="a")['href'])    
    
# Query only new ofertas
ofertas_ = list(set(url_ofertas) - set(id_history))

#Fetching el contenido de cada oferta
detalle = {}

for line in ofertas_:
#for line in url_ofertas:
    detalle = {}
    detalle["url_ofertas2"] = line # para usar en merge de dataframes
    detalle["url_ofertas"] = 'https://www.indeed.com.mx'
    detalle["url_ofertas"] = detalle["url_ofertas"]+format(line)
    detalle["url_ofertas"] = detalle["url_ofertas"].replace("\t"," ")
    detalle["url_ofertas"] = urllib.parse.quote(detalle["url_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')

    #conducting a request of the stated URL above:
    print(detalle["url_ofertas"])
    page = requests.get(detalle["url_ofertas"], headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    #detalle["Sopa_de_queso"] = soup
    #Nombre del puesto y local (local)
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
    try:
        components = soup.find(class_ = 'jobsearch-jobDescriptionText')
    except:
        pass
    if components!= None:
        for element in components.find_all('div'):
            try:     
                temp = element.text.strip()
                a,b = temp.split(':')
                b = b.strip()
                detalle[text_to_unicode(a)] =text_to_unicode(b)
            except:
                pass
    try:
        detalle["descripcion"] = soup.find(id='jobDescriptionText').text.strip()
    except:
        pass
    
    details.append(detalle)
    
#Create and merge dataframes
            
data = pd.DataFrame(details, columns = ["puesto","localidad", "empresa", "data_online", "salario", "Género","Sexo",
                                        "Idiomas", "Salario neto mensual", "Tipo de contrato",  "Vigencia de la oferta",
                                        "Dias laborales", "url_ofertas2", "descripcion",
                                        "Estudios Solicitados", "Prestaciones", "Edad", "Competencias transversales"])

data.rename(columns = {'Género':'genero','Sexo':'sexo','Estudios Solicitados':'educacion_minima', 
                       'Vigencia de la oferta':'vigencia_oferta', 'Idiomas':'idiomas', 
                       'Dias laborales':'jornada', 'Salario':'salario', 'Salario neto mensual':'salario',
                       'Tipo de contrato':'tipo_de_contrato', 'url_ofertas2':'url_oferta',
                       'Edad':'edad', 'Prestaciones':'prestaciones'}, inplace = True)

data['date'] = date.today()
  
#data.to_csv(r'Indeed_{0}.csv'.format(date.today()))  

history.append(data, sort = True, ignore_index=True).to_csv(r'indeed_{0}.csv'.format(date.today()))
