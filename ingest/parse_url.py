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


class GetUrls:
    def __init__(self):
        self.URL = 'https://www.computrabajo.com.mx/ofertas-de-trabajo/'
        self.pipeline = 'computrabajo'
        self.items_perpage = 20
        self.baseline_date = '2019-12-22'
        self.crawl_time = str(date.today())
        self.headers = {
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

    def parse_active(self):
        """
        Identificar el # de ofertas activas en México en un momento dado
        """
        #conducting a request of the stated URL above:
        page = requests.get(self.URL, headers=self.headers)
        #specifying a desired format of "page" using the html parser
        soup = BeautifulSoup(page.text, "html.parser")
        Ofertas_Activas = soup.find(class_="breadtitle_mvl").text
        Ofertas_Activas = int(''.join(filter(str.isdigit, Ofertas_Activas)))
        print(str(Ofertas_Activas))
        ofertas = []
        for pages in range(1, int((Ofertas_Activas / self.items_perpage) + 2)):
            URL = 'https://www.computrabajo.com.mx/ofertas-de-trabajo/'
            URL = URL + '?p=' + format(pages)
            print(URL)
            #conducting a request of the stated URL above:
            page = requests.get(URL, headers=self.headers)
            #specifying a desired format of "page" using the html parser
            soup = BeautifulSoup(page.text, "html.parser")
            #Extracting job titles
            tipos = ["bRS bClick ", "bRS bClick oD", "bRS bClick oU", "bRS bClick oD oU"]
            for t in tipos:
                for div in soup.find_all(name='div', attrs={'class': format(t)}):
                    oferta = {}
                    oferta["jobs"] = div.find(class_='js-o-link').text
                    oferta["URL_ofertas"] = div.find(class_='js-o-link')['href']
                    oferta["data_online"] = div.find(class_="dO").text.strip()
                    ofertas.append(oferta)
            data = pd.DataFrame(ofertas)
            data["active"] = True
            data["crawl_time"] = self.crawl_time
            # store raw
            data.to_csv(r'raw_{0}_{1}.csv'.format(self.pipeline, self.crawl_time))
            # update active
            data.to_csv(r'raw_{0}_active.csv'.format(self.pipeline))
        return data

    def compare_db(self, old, data):
        nuevos_activos, inactivos = utils.update_inactive(old, data)
        db_inactivos = old[old['URL_ofertas'].isin(inactivos)]
        db_inactivos["death"] = self.crawl_time
        db_inactivos.to_csv("inactivos.csv")
        new = data[data['URL_ofertas'].isin(nuevos_activos)]
        return new

    def update_inactive(self, old, new):
        """
        Obtener nuevas y actualizar inactivas
        """
        # Query only new ofertas
        activos_old = old.URL_ofertas
        # de las nuevas quitar las ya analizadas
        activos_new = new.URL_ofertas
        nuevos_activos = [item for item in activos_new if item not in activos_old]
        inactivos = [item for item in activos_old if item not in activos_new]
        return (nuevos_activos, inactivos)

compu_trabajo = GetUrls()
data = compu_trabajo.parse_active()
old = pd.read_csv("raw_computrabajo_active.csv")
parse = compu_trabajo.compare_db(old, data)
