# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 20:38:30 2020

@author: unily
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash()

#Data
Data_test = pd.read_csv(r'tecoloco_gt_2019-12-07.csv')
Data_test = Data_test.loc[Data_test['País']=='Guatemala']

Data_test.groupby('departamento')['cantidad_de_vacantes'].\
agg(MySum='sum', MyCount='count')

vacantes_depar = Data_test.groupby('departamento')['cantidad_de_vacantes'].sum()
vacantes_depar = vacantes_depar.nlargest(10).sort_values(ascending=False)

app.layout = html.Div(children=[
    html.H1(children='Guatemala'),

    html.Div(children='''
        Vacantes del mes de Diciembre de 2019.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': vacantes_depar.index,  'y': vacantes_depar, 'type': 'bar', 'name': 'El Salvador',
                 },
             ],
            'layout': {
                'title': 'Número de vacantes por Estado'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=False)

