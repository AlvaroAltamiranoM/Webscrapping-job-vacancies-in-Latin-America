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

Data_test['date'][0:500]='enero'
Data_test['date'][500:1000]='febrero'

Data_test['salarios'] = Data_test['salario'].str.extract('(\d*\.?\d+)')
Data_test['salarios'] = Data_test['salarios'].str.replace('.', '').astype(float)

#Transformando variable de edad
Data_test['edad'] = Data_test['edad'].str.extract('(\d{2}\sy\s\d{2})')
Data_test['edad_min'] = Data_test['edad'].astype(str).str[0:2]
Data_test['edad_min'] = pd.to_numeric(Data_test['edad_min'], errors='coerce')
Data_test['edad_max'] = Data_test['edad'].astype(str).str[-2:]
Data_test['edad_max'] = pd.to_numeric(Data_test['edad_max'], errors='coerce')
Data_test['edad'] = Data_test[['edad_min','edad_max']].mean(axis=1)

table = Data_test.groupby(['date','localidad']).size().reset_index().rename(columns={0:'conteo'})

table2 = pd.pivot_table(Data_test, 
                     index = ['localidad'],
                     values=['salarios', 'anios_de_experiencia', 'url_oferta', 'edad', 'educacion_minima', 'rama_de_actividad'],
                     aggfunc={'salarios': np.median, 'anios_de_experiencia': np.mean, 'url_oferta': pd.Series.nunique,
                              'edad': np.mean, 'educacion_minima': pd.Series.mode, 'rama_de_actividad': pd.Series.mode},
                     dropna=True)

anuncios_empresa = Data_test.groupby(['empresa','localidad', 'date']).size().reset_index().rename(columns={0:'conteo'})

table2.rename(columns = {'anios_de_experiencia': 'Años de experiencia (en media)', 'edad':'Edad requerida (media)', 
                       'salarios': 'Mediana salarial','rama_de_actividad':'Rama de actividad (moda)',
                       'url_oferta':'Total de anuncios'}, inplace = True)

table2['Años de experiencia (en media)']= table2['Años de experiencia (en media)'].round(1)
table2['Edad requerida (media)']= table2['Edad requerida (media)'].round(0)
table2['Mediana salarial']= table2['Mediana salarial'].round(0)

table_table = table2.reindex(['Estados','Total de anuncios', 'Mediana salarial','Años de experiencia (en media)', 
                       'Edad requerida (media)','Rama de actividad (moda)'], axis=1).sort_values(by='Total de anuncios',ascending=False)
table_table['Estados'] = table_table.index

words = anuncios_empresa.empresa
lenth = len(words)
colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(30)]
weights = anuncios_empresa.conteo

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
            options=[{'label': i, 'value': i} for i in table.localidad.unique()],
            placeholder='Seleccione un Estado',
            value = ['Ciudad de México DF','Jalisco', 'Puebla'],
            multi =True),
            ],
            style={'width': '48%', 'display': 'inline-block',
                    'marginTop': '1em','marginBottom': '1em'}),
    html.Div([
        dcc.Dropdown(
            id='yaxis-column',
            options=[{'label': i, 'value': i} for i in table.date.unique()],
            placeholder='Seleccione un mes',
            value = ['enero'],
            multi =True),
            ],
             style={'width': '48%', 'display': 'inline-block',
                    'marginTop': '1em','marginBottom': '1em'}),
    
    html.Div([
    dcc.Graph(id='graph1',
              style={'width': '48%', 'display': 'inline-block'}),
        
        dcc.Graph(id='graph2',
                  style={'width': '48%', 'display': 'inline-block'})
        ] ),

    html.H5(children='Resumen de principales variables por ciudad',
    style={'textAlign': 'left'
            }),

    dash_table.DataTable(
            style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
        },
    data=table_table.to_dict('records'),
        sort_action="native",
        filter_action='native',
        sort_mode="multi",
        columns=[{'id': c, 'name': c} for c in table_table.columns],
        style_table={'overflowX': 'scroll',
                     'maxHeight':'400px',
                     'overflowY':'scroll'},
        style_as_list_view=True,
        style_cell={'padding': '5px','textAlign': 'center',
                    },
        style_header={
            'fontWeight': 'bold',
            'backgroundColor': 'rgb(230, 230, 230)',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Ciudades'},
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

@app.callback(
    Output('graph1', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value')])

def update_graph(xaxis_column_name, year_value):
    #table_g = table.loc[table['localidad'].isin(xaxis_column_name)]
    if len(xaxis_column_name) > 0 and len(year_value) > 0:
        table_g = table.loc[table['localidad'].isin(xaxis_column_name) & table['date'].\
                            isin(year_value)].sort_values(by='conteo', ascending=False)
    
    return {
            'data': [dict(
            x=table_g['localidad'],
            y=table_g['conteo'],
            type='bar',
        )],
        'layout': dict(
            xaxis={
                'title': 'Estado',
                'yanchor': 'top'},
            yaxis={
                'title': 'Número'},
            title={
                'text': 'Vacantes en: <br>{}'.format(', '.join(xaxis_column_name)),
                'xanchor': 'auto',
                'y': 0.9})
        }

@app.callback(
    Output('graph2', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value')])
        
def update_graph2(xaxis_column_name, year_value):
    table3 = anuncios_empresa[anuncios_empresa['localidad'].isin(xaxis_column_name)]
    data = go.Scatter(
    x=[random.random() for i in range(30)],
    y=random.choices(range(30), k=30),
    mode='text',
    text=table3['empresa'][~(table3['empresa'].str.len() <4)].unique(),
    marker={'opacity': 0.3},
    textfont={'size': table3['conteo']*5,
   'color': colors})
 
    return {'data': [data],'layout' : go.Layout(xaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
                                                yaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
                                                title={'text': "Principales empresas",'y':0.9,'x':0.5, 'xanchor': 'center','yanchor': 'top'})
            }


if __name__ == '__main__':
    app.run_server(debug=False)

