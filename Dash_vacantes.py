# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 20:38:30 2020

@author: unily
"""

#           http://127.0.0.1:8050/

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly.offline import plot
import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#server = app.server

#Data
Data_test = pd.read_csv(r'data_dash.csv', encoding='utf-8')

Data_test['salarios'] = Data_test['salario'].str.extract('(\d*\.?\d+)')
Data_test['salarios'] = Data_test['salarios'].str.replace('.', '').astype(float)

#Transformando variable de edad
Data_test['edad'] = Data_test['edad'].str.extract('(\d{2}\sy\s\d{2})')
Data_test['edad_min'] = Data_test['edad'].astype(str).str[0:2]
Data_test['edad_min'] = pd.to_numeric(Data_test['edad_min'], errors='coerce')
Data_test['edad_max'] = Data_test['edad'].astype(str).str[-2:]
Data_test['edad_max'] = pd.to_numeric(Data_test['edad_max'], errors='coerce')
Data_test['edad'] = Data_test[['edad_min','edad_max']].mean(axis=1)

table = pd.pivot_table(Data_test, 
                     index = 'localidad',
                     values=['salarios', 'anios_de_experiencia', 'url_oferta', 'edad', 'educacion_minima', 'tamanio_empresa'],
                     aggfunc={'salarios': np.median, 'anios_de_experiencia': np.mean, 'url_oferta': pd.Series.nunique,
                              'edad': np.mean, 'educacion_minima': pd.Series.mode, 'tamanio_empresa': pd.Series.mode},
                     dropna=True)

anuncios_estado = Data_test.groupby(['localidad'])['url_oferta'].count()
anuncios_estado = anuncios_estado.nlargest(10).sort_values(ascending=False)

empresas = Data_test['empresa'].value_counts()
empresas = empresas.nlargest(30).sort_values(ascending=False)

table['Estados']= table.index
table = table.nlargest(10, 'url_oferta').sort_values('url_oferta', ascending=False)

table.rename(columns = {'anios_de_experiencia': 'Años de experiencia (en media)', 'edad':'Edad requerida (media)', 
                       'salarios': 'Mediana salarial','tamanio_empresa':'Tamaño de empresas (moda)',
                       'url_oferta':'Total de anuncios'}, inplace = True)

table['Años de experiencia (en media)']= table['Años de experiencia (en media)'].round(1)
table['Edad requerida (media)']= table['Edad requerida (media)'].round(0)

table = table.reindex(['Estados','Total de anuncios', 'Mediana salarial','Años de experiencia (en media)', 
                       'Edad requerida (media)','Tamaño de empresas (moda)'], axis=1)

words = empresas.index
lenth = len(words)
colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(30)]
weights = empresas.values

data = go.Scatter(x=[random.random() for i in range(30)],
                 y=random.choices(range(30), k=30),
                 mode='text',
                 text=words,
                 marker={'opacity': 0.3},
                 textfont={'size': weights,
                           'color': colors})
layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                    'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

fig = go.Figure(data=[data], layout=layout)
fig.update_layout(
    title={
        'text': "Principales empresas",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

#for estado in anuncios_estado['localidad']:
 #   anuncios_estado = anuncios_estado['url_oferta'].nlargest(10).sort_values(ascending=False)
    
app.layout = html.Div(children=[
    html.H1(children='México',
    style={'textAlign': 'center'
            }
    ),
    html.H3(children='Tablero-resumen de vacantes en línea',
    style={'textAlign': 'center'
            },
),
    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': i, 'value': i} for i in table.Estados],
            placeholder='Seleccione un Estado'),
            ],
            style={'width': '48%', 'display': 'inline-block',
                    'marginTop': '1em','marginBottom': '1em'}),
    html.Div([
        dcc.Dropdown(
            id='yaxis-column',
            options=[{'label': i, 'value': i} for i in Data_test.date.unique()],
            placeholder='Seleccione un Estado'),
            ],
             style={'width': '48%', 'display': 'inline-block',
                    'marginTop': '1em','marginBottom': '1em'}),
    
    html.Div([
    dcc.Graph(
        id='graph1',
        figure={
            'data': [{'x': anuncios_estado.index,  'y': anuncios_estado, 'type': 'bar', 'name': 'México'},
             ],
            'layout': {'title': 'Número de vacantes por Portal'}
            },
            style={'width': '48%', 'display': 'inline-block'}),
        
        dcc.Graph(id='graph2',figure = fig,
                  style={'width': '48%', 'display': 'inline-block'})
        ] ),

    html.H5(children='Resumen de principales variables por ciudad',
    style={'textAlign': 'left'
            }),

    dash_table.DataTable(
            style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
        },
    data=table.to_dict('records'),
        sort_action="native",
        filter_action='native',
        sort_mode="multi",
        columns=[{'id': c, 'name': c} for c in table.columns],
        style_table={'overflowX': 'scroll'},
        style_as_list_view=True,
        style_cell={'padding': '5px','textAlign': 'center',
                    },
        style_header={
            'fontWeight': 'bold',
            'backgroundColor': 'rgb(230, 230, 230)',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Estados'},
                    'textAlign': 'left',
                    'width': '170px'},
                 {'if': {'column_id': 'Años de experiencia (en media)'},
                   'width': '15px'},
                ],
                style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
    )
    ])
    

    
if __name__ == '__main__':
    app.run_server(debug=False) 
