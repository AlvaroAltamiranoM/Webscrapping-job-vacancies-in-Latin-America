# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:22:13 2020

@author: ALVAROALT
"""

import pandas as pd

#Data
rescate = pd.read_csv(r'Indeed_2020-02-23.csv')[['url_oferta', 'descripcion']]

#rescate = data2[['url_oferta', 'descripcion']]
#Recuperando variables a partir de la descripción de la vacante
    #Salarios
rescate['salario'] = rescate['descripcion'].str.extract('(Salario:\s\$.*\d+,\d+)')
rescate['salario'] = rescate['salario'].str.extract('(\d+,\d+)')
rescate['salario'] = rescate['salario'].str.replace(',', '').astype(float)
rescate['salario'].describe()

    #Edad
rescate['edad'] = rescate['descripcion'].str.extract('(Edad:\s.*\d+.a.\d+)')
rescate['edad'] = rescate['edad'].str.replace('Edad: ', '')
rescate['edad_min'] = rescate['edad'].astype(str).str[0:2]
rescate['edad_min'] = pd.to_numeric(rescate['edad_min'], errors='coerce')
rescate['edad_max'] = rescate['edad'].astype(str).str[-2:]
rescate['edad_max'] = pd.to_numeric(rescate['edad_max'], errors='coerce')
rescate['edad'] = rescate[['edad_min','edad_max']].mean(axis=1)
rescate[['edad_min','edad_max']].describe()
    
    #Experiencia
rescate['anios_de_experiencia'] = rescate['descripcion'].str.extract('(Experiencia:.*\d+)')
rescate['anios_de_experiencia'] = rescate['anios_de_experiencia'].str.extract('(\d{1,2})')
rescate['anios_de_experiencia'] = pd.to_numeric(rescate['anios_de_experiencia'], errors='coerce')
rescate['anios_de_experiencia'].describe()
 
    #Educación
rescate['educacion_minima'] = rescate['descripcion'].str.extract("(Educación:.*?\s\w+)")
rescate['educacion_minima'] = rescate['educacion_minima'].str.replace('Educación:', '')
rescate['educacion_minima'] = rescate['educacion_minima'].str.replace('(', '')
rescate['educacion_minima'].describe()

    #Tipo de puesto
rescate['tipo_de_contrato'] = rescate['descripcion'].str.extract("(Tipo de puesto:\s\w+\s\w+)")
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Tipo de puesto: ', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Salario', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Tipo', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Idioma', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Educación', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Experiencia', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Disponibilidad', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace(' de ', '')
rescate['tipo_de_contrato'] = rescate['tipo_de_contrato'].str.replace('Ubicación', '')

    #Sexo
rescate['genero'] = rescate['descripcion'].str.extract("(Sexo:.*?\s\w+)")
rescate['genero'] = rescate['genero'].str.replace('Sexo:', '').str.strip()
rescate['genero']= rescate['genero'].str.lower()
rescate['genero'] = rescate['genero'].str.replace('h', 'hombre')
rescate['genero'] = rescate['genero'].str.replace('m', 'mujer')
rescate['genero'] = rescate['descripcion'].str.\
extract(r'(indefinido\b|ambos\b|indistinto\b|hombre\b|mujer\b|feminino\b|masculino\b|hombres\b|mujeres\b|indiferente\b)')
    
    #Idiomas
rescate['idiomas'] = rescate['descripcion'].str.extract("(Idioma:.*?\s\w+)")
rescate['idiomas'] = rescate['idiomas'].str.replace('Idioma:', '').str.strip()
rescate['idiomas']= rescate['idiomas'].str.lower()
rescate['idiomas'] = rescate['descripcion'].str.\
extract(r'(inglés\b|ingles\b|español\b|spanish\b|english\b|francés\b|frances\b|portugués\b|portugues\b|frech\b|portuguese\b|german\b)')



