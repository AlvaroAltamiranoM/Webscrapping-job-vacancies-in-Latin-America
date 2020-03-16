# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 20:30:18 2020

@author: ALVAROALT
"""
!pip install geopandas
!python -m pip install --upgrade pip

!pip install fiona

import geopandas
import shapely
import shapefile
import plotly
from plotly.figure_factory._county_choropleth import create_choropleth
import numpy as np
import pandas as pd

df_sample = pd.read_csv(r'mex_fips.csv', encoding='latin-1')
data = pd.read_csv(r'computrabajo_2020-02-18.csv')

data['salarios'] = data['salario'].str.extract('(\d*\.?\d+)')
data['salarios'] = data['salarios'].str.replace('.', '').astype(float)

table = pd.pivot_table(data, 
                     index = 'localidad',
                     values=['salarios', 'anios_de_experiencia', 'url_oferta', 'edad', 'educacion_minima', 'tamanio_empresa'],
                     aggfunc={'salarios': np.median, 'anios_de_experiencia': np.mean, 'url_oferta': pd.Series.nunique,
                              'edad': pd.Series.mode, 'educacion_minima': pd.Series.mode, 'tamanio_empresa': pd.Series.mode},
                     dropna=True)

table['State']= table.index

df_sample = df_sample.merge(table, how="left", on="State", indicator=True)


df_sample['FIPS'] = df_sample['FIPS'].apply(lambda x: str(x).zfill(2))

colorscale = ["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",
              "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9",
              "#08519c","#0b4083","#08306b"]
endpts = list(np.linspace(1, 12, len(colorscale) - 1))
fips = df_sample['FIPS'].tolist()
values = df_sample['url_oferta'].tolist()

fig = create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='USA by Unemployment %',
    legend_title='% unemployed'
)

fig.layout.template = None
fig.show()