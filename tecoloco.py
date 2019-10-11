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

headers = {
    'authority': 'www.tecoloco.com.gt',
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

#countries = ['ni', 'gt', 'sv', 'hn']
countries = ['gt']
items_perpage = 100
for country in countries:
    #Identificar el # de ofertas activas en cada página-país en un momento dado
    URL = 'https://www.tecoloco.com.'+format(country)+'/empleos'
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
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
details = []

for country in countries:
    URL = 'https://www.tecoloco.com.'+format(country)+'/empleos'
    print(URL)
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    Ofertas_Activas = int(soup.find(class_ = "ofertasactivas").text)
    for pages in range(1,int((Ofertas_Activas/items_perpage)+2)):
        URL = 'https://www.tecoloco.com.'+format(country)+'/empleos?Page='+\
                format(pages)+'&PerPage='+format(items_perpage)
        print(URL)
        #conducting a request of the stated URL above:
        page = requests.get(URL, headers=headers)
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
        for line in ofertas:
            URL_ofertas = 'https://www.tecoloco.com.'+format(country)+format(line)
            print(URL_ofertas+str(pages))
            #conducting a request of the stated URL above:
            page = requests.get(URL_ofertas, headers=headers)
            while page.status_code != 200:
                try:
                    print ("Response not == to 200.")
                    page = requests.get(URL_ofertas, headers=headers)
                except:
                    sleep(300)
                    print("sleeping")
            #specifying a desired format of "page" using the html parser - this
            # allows python to read the various components of the page, rather
            # than treating it as one long string.
            soup = BeautifulSoup(page.text, "html.parser")
            #Extracting job vacancies descriptions
            table = soup.find('table', attrs={'class':'detalle-oferta'})
            description_aux = soup.find("p").text
            #description_aux = np.array(description).T.tolist()
            #description.append(list(description))
            table_rows = table.find_all('tr')
            detalle = {}
            for tr in table_rows:
                td = tr.find_all('td')
                detalle['ofertas'] = line
                detalle[td[0].text.strip()]=td[1].text.strip()
            details.append(detalle)
    details = pd.DataFrame.from_records(details)

    #Concatenate & export DFs
    df = pd.DataFrame(list(zip(jobs, emp, local, ID, ofertas, expira)),
            columns=["jobs", "emp", "local","ID", "ofertas","expira"])
    data = df.merge(details, how="left",on="ofertas" ,indicator=True)
    data['Date'] = date.today()
    data.to_csv(r'tecoloco_{0}.csv'.format(country))
