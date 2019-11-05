# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 22:29:27 2019

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

#countries = ['ni']
countries = ['ni', 'hn', 'pa', 'do', 'gt', 'co', 'mx', 'ar', 'pe', 'cl', 'ec', 'uy', 'py', 'bo']
items_perpage = 20

for country in countries:
    jobs = []
    URL_ofertas = []
    #Identificar el # de ofertas activas en cada página-país en un momento dado
    URL = 'https://www.computrabajo.com.'+format(country)+'/ofertas-de-trabajo/'
    #conducting a request of the stated URL above:
    page = requests.get(URL, headers=headers)
    #specifying a desired format of "page" using the html parser    soup = BeautifulSoup(page.text, "html.parser")
    soup = BeautifulSoup(page.text, "html.parser")
    Ofertas_Activas = soup.find(class_ = "breadtitle_mvl").text
    Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
    print(country +' = ' + str(Ofertas_Activas))

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
            URL_ofertas.append(link['href'])

    #Fetching el contenido de cada oferta
    details = []

    for line in URL_ofertas:
        detalle = {}
        detalle["URL_ofertas"] = 'https://www.computrabajo.com.'+format(country)+format(line)
        detalle["URL_ofertas"] = detalle["URL_ofertas"].replace("\t"," ")
        detalle["URL_ofertas"] = urllib.parse.quote(detalle["URL_ofertas"], safe="%/:=&?~#+!$,;'@()*[]", encoding = 'utf-8')
        #conducting a request of the stated URL above:
        page = requests.get(detalle["URL_ofertas"], headers=headers)
        while page.status_code != 200:
            try:
                print ("Response not == to 200.")
                page = requests.get(detalle["URL_ofertas"], headers=headers)
            except:
                sleep(300)
            print("sleeping")
        soup = BeautifulSoup(page.text, "html.parser")
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
        try:
            box = soup.find(name="section", class_ = 'box box_r').find_all("li")
        except:
            pass
        for element in box:
            try:
                a = element.find("p").text.replace(' +',' ').strip()
                detalle[element.find("h3").text] = text_to_unicode(a)
            except:
                pass
        tipos2 = ["cm-12 box_i bWord", "cm-12 box_i"]
        for t in tipos2:
            try:
                a = soup.find(name="div", class_ =
                              format(t)).find_all("li")[0].text.\
                    replace('\nDescripción\r\n ', '').strip()
                detalle["descripcion"] = text_to_unicode(a)
            except:
                pass
        for t in tipos2:
            try:
                components = soup.find(name = "div",class_ = 'cm-12 box_i bWord')
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
    data = pd.DataFrame.from_records(details)
    data = data.drop(columns = ['Empresa','Localización'])
    
    data['Date'] = date.today()
    data.to_csv(r'computrabajo_{0}_{1}.csv'.format(country, date.today()))

