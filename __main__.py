from repo import general, geraldine, invasiones, libres
import numpy as np
import pandas as pd
import re

# Saca los dnis / nombres siempre que estos no esten con el valor 'nan' que indica q no existe valor
def get_data(dataframe):
    errors = []
    dnis = []
    nombres = []

    for index, row in dataframe.iterrows():
        dni = str(row.get("DNI"))
        nombre = str(row.get('POR CONFIRMAR 2018 - CONTRATO'))
        if dni != 'nan' and dni != '-' and dni != 'PEND.':
            dnis.append(dni)
        elif nombre != 'nan':
            nombres.append(nombre)
        else:
            errors.append(list(row))
    
    return {"errores": errors, "dnis": dnis, "nombres": nombres}

# obtiene todos los campos distintos que existen en los 4 excels
def create_headers() -> list:
    general_headers = set(general.data)
    geraldine_headers = set(geraldine.data)
    invasiones_headers = set(invasiones.data)
    libres_headers = set(libres.data)

    # solo deja los q no se repiten
    final = general_headers | geraldine_headers
    final = final | invasiones_headers
    final = final | libres_headers 
    
    final.add("OBSERVACIONES_EXTRAS")

    return list(final)

# extrae los dnis/ nombres de cada data set, luego filtra los repetidos
def generate_data():
    gen = get_data(general.data)
    ger = get_data(geraldine.data)
    inv = get_data(invasiones.data)
    lib = get_data(libres.data)

    # solo deja los q no se repiten
    dnis = set(gen["dnis"]) | set(ger["dnis"])
    dnis = dnis | set(inv["dnis"])
    dnis = dnis | set(lib["dnis"])

    nombres = set(gen["nombres"]) | set(ger["nombres"])
    nombres = nombres | set(inv["nombres"])
    nombres = nombres | set(lib["nombres"])

    return {
        "dnis": list(dnis),
        "nombres": list(nombres),
        "errores_gen": gen["errores"],
        "errores_ger": ger["errores"],
        "errores_inv": inv["errores"],
        "errores_lib": lib["errores"]
    }

def is_number_regex(s):
    """ Returns True is string is a number. """
    if re.match("^\d+?\.\d+?$", s) is None:
        return s.isdigit()
    return True


def analizar_reg(reg, obs, data_frame, headers, nombre):

    if len(data_frame) > 0:
        row = data_frame.iloc[0]

        if len(reg) == 0:
            obs = f"El valor inicial se obtuvo de {nombre}. "
            for idx, header in enumerate(headers):
                value = str(row.get(header)).strip()

                if value != 'nan' and value != 'None':
                    reg.append(value)
                else:
                    reg.append("")
        else:
            for idx, header in enumerate(headers):
                value = str(row.get(header))

                t_value = float(value) if is_number_regex(value) else value
                t_reg = float(reg[idx]) if is_number_regex(reg[idx]) else reg[idx]
                
                if value != 'nan' and value != 'None':
                    if t_value != t_reg and reg[idx] != "":
                        obs += f"El valor del header {header} entre el original [{reg[idx]}] y {nombre} [{value}] son diferentes. "   
    
    return obs

def main():
    headers = create_headers()
    data = generate_data()

    print(f"""
        # dnis: {len(data["dnis"])}
        # nombres: {len(data["nombres"])}
        # errores en general: {len(data["errores_gen"])}
        # errores en geraldine: {len(data["errores_ger"])}
        # errores en invasion: {len(data["errores_inv"])}
        # errores en libre: {len(data["errores_lib"])}
    """)

    dnis = data["dnis"]

    info = []
    no_procesados = []

    for dni in dnis:
        res_general = general.find_by_dni(dni)
        res_geraldine = geraldine.find_by_dni(dni)
        res_invasiones = invasiones.find_by_dni(dni)
        res_libres = libres.find_by_dni(dni)

        if len(res_general) > 1 or len(res_geraldine) > 1 or len(res_invasiones) > 1 or len(res_libres) > 1:
            message = f"""
        No se puede trabajar el siguiente dni porque existe mas de 1 registro en 1 o mas data sets:
        DNI: {dni}
        general: {len(res_general)}
        geraldine: {len(res_geraldine)}
        invasiones: {len(res_invasiones)}
        libres: {len(res_libres)}
            """
            print(message)
            no_procesados.append([dni, message])

        else:
            obs = ""
            reg = []

            obs = analizar_reg(reg, obs, res_general,headers, 'general')
            obs = analizar_reg(reg, obs, res_geraldine,headers, 'geraldine')
            obs = analizar_reg(reg, obs, res_invasiones,headers, 'invasiones')
            obs = analizar_reg(reg, obs, res_libres,headers, 'libres')

            reg[len(headers) - 1] = obs
            info.append(reg)


    nombres = data["nombres"]
    for nombre in nombres:
        res_general = general.find_by_nombre(nombre)
        res_geraldine = geraldine.find_by_nombre(nombre)
        res_invasiones = invasiones.find_by_nombre(nombre)
        res_libres = libres.find_by_nombre(nombre)

        if len(res_general) > 1 or len(res_geraldine) > 1 or len(res_invasiones) > 1 or len(res_libres) > 1:
            message = f"""
        No se puede trabajar el siguiente nombre porque existe mas de 1 registro en 1 o mas data sets:
        Nombre: {nombre}
        general: {len(res_general)}
        geraldine: {len(res_geraldine)}
        invasiones: {len(res_invasiones)}
        libres: {len(res_libres)}
            """
            print(message)
            no_procesados.append([nombre, message])
        else:
            obs = ""
            reg = []

            obs = analizar_reg(reg, obs, res_general,headers, 'general')
            obs = analizar_reg(reg, obs, res_geraldine,headers, 'geraldine')
            obs = analizar_reg(reg, obs, res_invasiones,headers, 'invasiones')
            obs = analizar_reg(reg, obs, res_libres,headers, 'libres')

            reg[len(headers) - 1] = obs
            info.append(reg)

    #print (info)
    final = pd.DataFrame(info, columns = headers)
    final.to_csv("out/procesado_final.csv", sep=";", index=False)
    
    errores_general = pd.DataFrame(data["errores_gen"], columns = list(general.data))
    errores_general.to_csv("out/errores_general.csv", sep=";", index=False)

    errores_geraldine = pd.DataFrame(data["errores_ger"], columns = list(geraldine.data))
    errores_geraldine.to_csv("out/errores_geraldine.csv", sep=";", index=False)

    errores_invasiones = pd.DataFrame(data["errores_inv"], columns = list(invasiones.data))
    errores_invasiones.to_csv("out/errores_invasiones.csv", sep=";", index=False)

    errores_libres = pd.DataFrame(data["errores_lib"], columns = list(libres.data))
    errores_libres.to_csv("out/errores_libres.csv", sep=";", index=False)

    sin_procesar = pd.DataFrame(no_procesados, columns= ["DNI O NOMBRE", "MENSAJE"])
    sin_procesar.to_csv("out/sin_procesar.csv", sep=";", index=False)

if __name__ == '__main__':
    main()