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
    'authority': 'www.bumeran.com.mx',
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


items_perpage = 30
#baseline_date = '2020-02-16'

jobs = []
url_oferta = []
url_oferta2 = []
data_online = []
details = []
#Load history
history = pd.read_csv(r'bumeran_{0}.csv'.format(baseline_date))
id_history = history.url_oferta

#Identificar el # de ofertas activas en cada página-país en un momento dado
URL = 'https://www.bumeran.com.mx/empleos-mexico/'
#conducting a request of the stated URL above:
page = requests.get(URL, headers=headers)
#specifying a desired format of "page" using the html parser    soup = BeautifulSoup(page.text, "html.parser")
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find("strong").text
Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
print(str(Ofertas_Activas))

#for pages in range(1,2):
for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
    URL = 'https://www.bumeran.com.mx/empleos-pagina-'
    URL = URL+format(pages)
    print(URL)
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser
    soup = BeautifulSoup(page.text, "html.parser")
    #Extracting job titles
    for div in soup.find_all(name = 'div',attrs = {'class': 'col-sm-9 col-md-10 col-xs-9 wrapper'}):
        jobs.append(div.find('h2').text)
        url_oferta.append(div.find()['href'])
        
        
# Query only new ofertas
ofertas_ = list(set(url_oferta) - set(id_history))

#Fetching el contenido de cada oferta
detalle = {}
for line in ofertas_:
#for line in url_oferta:
    detalle = {}
    detalle["url_oferta2"] = line # para usar en merge de dataframes
    detalle["url_oferta"] = 'https://www.bumeran.com.mx/'
    detalle["url_oferta"] = detalle["url_oferta"]+format(line)
    detalle["url_oferta"] = detalle["url_oferta"].replace("\t"," ")
    detalle["url_oferta"] = urllib.parse.quote(detalle["url_oferta"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')
    
    #conducting a request of the stated URL above:
    print(detalle["url_oferta"])
    page = requests.get(detalle["url_oferta"], headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    #detalle["Sopa_de_queso"] = soup
    box = soup.find(name="div", class_ = 'aviso_specs').find_all("h2")
    detalle["localidad"] = box[1].text.strip()
    detalle["fecha_online"] = box[3].text.strip()
    detalle["salario"] = box[5].text.strip()
    detalle["tipo_de_contrato"] = box[7].text.strip()
    detalle["rama_de_actividad"] = box[9].text.strip()
    #Empresa
    try:
        detalle["empresa"] = soup.find(id = 'empresa').text.strip()
    except:
        pass   
    try:
        a = soup.find(name="div", class_ = 'aviso_description').text.strip()
        detalle["descripcion"] = re.sub(r'.*(El contenido de este aviso).*','',a)
    except:
        pass
    
    details.append(detalle)

#Create and merge dataframes
df = pd.DataFrame(list(zip(jobs, url_oferta)), 
                  columns=["puesto2", "url_oferta"])

data = pd.DataFrame(details, columns = ["puesto","localidad","empresa", "fecha_online", "salario",
                                        "tipo_de_contrato", "url_oferta2", "descripcion", "rama_de_actividad"])

data.rename(columns = {'url_oferta2':'url_oferta'}, inplace = True)

data['puesto'] = df['puesto2'] 
    
data['date'] = date.today()

#data = data.merge(df, how="left", on="url_oferta", indicator=True)
#data = data.drop(columns = ['puesto2'])
  
#data.to_csv(r'bumeran_{0}.csv'.format(date.today()))  

history.append(data, sort = True, ignore_index=True).to_csv(r'bumeran_{0}.csv'.format(date.today()))
