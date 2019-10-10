# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 22:26:32 2019

@author: ALVAROALT
"""
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from time import sleep
import csv
import datetime
import re
import itertools
from datetime import date

#countries = ['ni', 'gt', 'sv', 'hn']
countries = ['gt']
items_perpage = 100
for country in countries:
    #Identificar el # de ofertas activas en cada página-país en un momento dado
    URL = 'https://www.tecoloco.com.'+format(country)+'/empleos'
    #conducting a request of the stated URL above:
    page = requests.get(URL)
    #specifying a desired format of "page" using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
    soup = BeautifulSoup(page.text, "html.parser")
    Ofertas_Activas = int(soup.find(class_ = "ofertasactivas").text)
    print(country +' = ' + str(Ofertas_Activas))
    
#Parse todas las páginas y crea CSV con metadata de vacantes
#Definir las columnas de la metadata
jobs = []
emp = []
local = []
ID = []
ofertas = []
expira = []

for country in countries:
    URL = 'https://www.tecoloco.com.'+format(country)+'/empleos'
    print(URL)
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, "html.parser")
    Ofertas_Activas = int(soup.find(class_ = "ofertasactivas").text)
    for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
        URL = 'https://www.tecoloco.com.'+format(country)+'/empleos?Page='+format(pages)+'&PerPage='+format(items_perpage)
        print(URL)
        #conducting a request of the stated URL above:
        page = requests.get(URL)
        #specifying a desired format of "page" using the html parser
        soup = BeautifulSoup(page.text, "html.parser")
        #Extracting job titles
        for div in soup.find_all(name = "div",attrs = {"class":"job-result-title"}):
            jobs.append(div.find(name = "a").text)
        for div in soup.find_all(name = "div",attrs = {"class":"job-result-overview"}):
            emp.append(div.find("li").text)
            local.append(div.find(itemprop="jobLocation").text)
            expira.append(div.find(itemprop="datePosted").text)
            expira = re.findall(r'(\d+/\d+/\d+)',str(expira))
        for div in soup.find_all(name = "div",attrs = {"class":"job-result-cta result-page"}):
            ID.append(div.find("a", {"jobid": True}))
            ID = re.findall('[0-9]{6}',str(ID))
        for link in soup.findAll('a', href=True, text='Ver oferta'):
            ofertas.append(link['href'])
         #Fetching el contenido de cada oferta
        details = []
        #description = []
        for line in ofertas:
            URL_ofertas = 'https://www.tecoloco.com.'+format(country)+format(line)
            print(URL_ofertas+str(pages))
            #conducting a request of the stated URL above:
            page = requests.get(URL_ofertas)
            while page.status_code != 200:
                try: 
                    print ("Response not == to 200.")
                    page = requests.get(URL_ofertas)
                except:
                    sleep(300)
                    print("sleeping")
            #specifying a desired format of "page" using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
            soup = BeautifulSoup(page.text, "html.parser")
            #Extracting job vacancies descriptions
            table = soup.find('table', attrs={'class':'detalle-oferta'})
            description_aux = soup.find("p").text
            #description_aux = np.array(description).T.tolist()
            #description.append(list(description))
            table_rows = table.find_all('tr')
            for tr in table_rows:
                td = tr.find_all('td')
                row = [d.text.strip() for d in td]
                details.append(row)
                detailsdos = np.array(details).T.tolist()
                x = np.delete(detailsdos, (0), axis=0).tolist()
 
#Concatenando DFs, ver forma más efeciente en el futuro!
df = pd.DataFrame([jobs, emp, local, ID, ofertas, expira]).T
df2 = pd.DataFrame(x)
#df2 = np.reshape(df2.values,(Ofertas_Activas,12))
df2 = np.reshape(df2.values,(232,12))
df2 = pd.DataFrame(df2)
dfF = pd.concat([df, df2], axis=1)
dfF['Date'] = pd.to_datetime(date.today())
dfF.columns = ["Título", "Empleador", "Localidad", "ID", "Link_oferta", "Expira_fecha", "Area de la empresa", "Cargo", "Puestos vacantes", "Tipo de contrato", "Experiencia requerida", "Género", "Edad", "W_máximo", "W_mínimo", "Requiere_vehículo", "País", "Departamento", "Fecha de extracción"]
dfF.to_csv(r'Nicaragua.csv')

del ([jobs, emp, local, ID, ofertas, expira])

