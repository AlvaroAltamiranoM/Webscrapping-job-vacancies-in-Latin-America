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
import utils

headers = {
    'authority': 'www.computrabajo.com.mx',
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


items_perpage = 20
baseline_date = '2019-12-22'

jobs = []
URL_ofertas = []
URL_ofertas2 = []
data_online = []
details = []
#Load history
#history = pd.read_csv(r'computrabajo_{0}.csv'.format(baseline_date))
#id_history = history.url_oferta

#Identificar el # de ofertas activas en cada página-país en un momento dado
URL = 'https://www.computrabajo.com.mx/ofertas-de-trabajo/'
#conducting a request of the stated URL above:
page = requests.get(URL, headers=headers)
#specifying a desired format of "page" using the html parser    soup = BeautifulSoup(page.text, "html.parser")
soup = BeautifulSoup(page.text, "html.parser")
Ofertas_Activas = soup.find(class_ = "breadtitle_mvl").text
Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
print(str(Ofertas_Activas))

#for pages in range(12,13):
for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
    URL = 'https://www.computrabajo.com.mx/ofertas-de-trabajo/'
    URL = URL+'?p='+format(pages)
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
            URL_ofertas.append(div.find(class_='js-o-link')['href'])
            data_online.append(div.find(class_ = "dO").text.strip())
            
# Query only new ofertas
#ofertas_ = list(set(URL_ofertas) - set(id_history))

#Fetching el contenido de cada oferta
#for line in ofertas_:
#for line in URL_ofertas:
    detalle = {}
for line in URL_ofertas:
    detalle = {}
    detalle["URL_ofertas"] = 'https://www.computrabajo.com.mx/ofertas-de-trabajo/'
    detalle["URL_ofertas"] = detalle["URL_ofertas"]+format(line)
    detalle["URL_ofertas"] = detalle["URL_ofertas"].replace("\t"," ")
    detalle["URL_ofertas"] = urllib.parse.quote(detalle["URL_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')
    
    detalle["URL_ofertas2"] = re.findall(r"[^.]ofertas[^.]*",detalle["URL_ofertas"])
    detalle["URL_ofertas2"] = ', '.join(detalle["URL_ofertas2"])
    
    #conducting a request of the stated URL above:
    page = requests.get(detalle["URL_ofertas"], headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    #detalle["Sopa_de_queso"] = soup
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

df = pd.DataFrame(list(zip(jobs, URL_ofertas, data_online)), 
                  columns=["puesto2", "url_oferta", "fecha_online"])

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
  
data.to_csv(r'computrabajo_{0}.csv'.format(date.today()))  

#history.append(data, sort = True, ignore_index=True).to_csv(r'computrabajo_{0}_{1}.csv'.format(country, date.today()))
