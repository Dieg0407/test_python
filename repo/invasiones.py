import pandas as pd
import os

data = pd.read_csv('data/invasiones.csv' , sep=';', quotechar='"', encoding='utf8')


def find_by_dni(dni: str):
    return data.loc[data['DNI'] == dni]

def find_by_nombre(nombre: str):
    return  data.loc[data['POR CONFIRMAR 2018 - CONTRATO'] == nombre]