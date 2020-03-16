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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Data
Data_test = pd.read_csv(r'computrabajo_2020-02-18.csv')
#Data_test = Data_test.loc[Data_test['País']=='México']

Data_test['salarios'] = Data_test['salario'].str.extract('(\d*\.?\d+)')
Data_test['salarios'] = Data_test['salarios'].str.replace('.', '').astype(float)

table = pd.pivot_table(Data_test, 
                     index = 'localidad',
                     values=['salarios', 'anios_de_experiencia', 'url_oferta', 'edad', 'educacion_minima', 'tamanio_empresa'],
                     aggfunc={'salarios': np.median, 'anios_de_experiencia': np.mean, 'url_oferta': pd.Series.nunique,
                              'edad': pd.Series.mode, 'educacion_minima': pd.Series.mode, 'tamanio_empresa': pd.Series.mode},
                     dropna=True)

anuncios_estado = Data_test.groupby(['localidad'])['url_oferta'].count()
anuncios_estado = anuncios_estado.nlargest(10).sort_values(ascending=False)

table['Estados']= table.index
table = table.nlargest(10, 'url_oferta').sort_values('url_oferta', ascending=False)

table.rename(columns = {'anios_de_experiencia': 'Años de experiencia (en media)', 'edad':'Rango de edad requerido (moda)', 
                       'salarios': 'Mediana salarial','tamanio_empresa':'Tamaño de empresas (moda)',
                       'url_oferta':'Total de anuncios'}, inplace = True)

table['Años de experiencia (en media)']= table['Años de experiencia (en media)'].round(2)

table = table.reindex(['Estados','Total de anuncios', 'Mediana salarial','Años de experiencia (en media)', 
                       'Rango de edad requerido (moda)','Tamaño de empresas (moda)'], axis=1)


#for estado in anuncios_estado['localidad']:
 #   anuncios_estado = anuncios_estado['url_oferta'].nlargest(10).sort_values(ascending=False)
    
app.layout = html.Div(children=[
    html.H1(children='México',
    style={'textAlign': 'center'
            }
    ),
    html.Div(children='Vacantes publicadas en portales de empleo',
    style={'textAlign': 'center'
            },
),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [{'x': anuncios_estado.index,  'y': anuncios_estado, 'type': 'bar', 'name': 'México',
                 },
             ],
            'layout': {'title': 'Número de vacantes por Estado'}
            },
            style={'width': '1000', 'display': 'inline-block'}),
        
        dcc.Graph(
        figure= {
                'data': [{'x': anuncios_estado.index,  'y': anuncios_estado, 'type': 'bar', 'name': 'México',
                         },
                         ],
        'layout': {'title': 'Número de vacantes por Estado'}
        }, 
        style={'width': '1000', 'display': 'inline-block'}),

    dash_table.DataTable(
            style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
        },
    data=table.to_dict('records'),
        sort_action="native",
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
# =============================================================================
#                  {'if': {'column_id': 'Mediana salarial'},
#                   'width': '20px'},
#                   {'if': {'column_id': 'Total de anuncios'},
#                   'width': '20px'},
#                    {'if': {'column_id': 'Años de experiencia (en media)'},
#                   'width': '10px'},
#                     {'if': {'column_id': 'Rango de edad requerido (moda)'},
#                   'width': '20px'},
#                     {'if': {'column_id': 'Tamaño de empresas (moda)'},
#                   'width': '20px'}
# =============================================================================
                ],
                style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ]
    )
    ])
    

"""
dcc.Input(id = 'input', value = '', type = 'text',
                  style={'width': '100%', 'display': 'inline-block'}),
        html.Div(id  = 'output'),
        
@app.callback(
        Output(component_id= 'output', component_property='children'),
        [Input(component_id= 'input', component_property='value')])

def update_value(input_data):
            return "Input: {}".format(input_data)
"""
    
if __name__ == '__main__':
    app.run_server(debug=False) 


