import os
import pandas as pd
import numpy as np
import csv
import yaml
import time
import joblib
import json

from estado import escribir_estado

def calcular_angulo(punto1, punto2, punto3, withers, tail_set):
    """
    1. Calcula el vector desde punto2 hacia punto1 y punto3.  
    2. Obtiene el ángulo entre ambos vectores en radianes, luego convierte a grados.  
    3. Ajusta el ángulo según la posición relativa de 'withers' y 'tail_set'.  
    4. Retorna el ángulo en grados, normalizado entre 0 y 360.
    """
    v1 = np.array([punto1[0] - punto2[0], punto1[1] - punto2[1]])
    v2 = np.array([punto3[0] - punto2[0], punto3[1] - punto2[1]])

    angulo_rad = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
    angulo_grados = np.degrees(angulo_rad) % 360  

    if withers[0] > tail_set[0]:
        angulo_grados = 360 - angulo_grados

    return angulo_grados

def calcular_distancia(punto1, punto2):
    """
    1. Calcula la distancia euclidiana entre dos puntos (x, y).  
    2. Retorna la distancia como un valor escalar.
    """
    return np.linalg.norm(np.array(punto1) - np.array(punto2))

def calcular_angulos_distancias(coords):
    """
    1. Recibe diccionario coords: {parte: (x,y)} y calcula:  
    2. Ángulos según puntos indicados  
    3. Distancias entre pares definidos  
    4. Retorna lista de medidas
    """

    if "Withers" not in coords or "Tail_Set" not in coords:
        withers = tail_set = None
    else:
        withers = coords["Withers"]
        tail_set = coords["Tail_Set"]

    angulos_a_calcular = [
        ("Withers", "Tail_Set", "Tail_Tip"),
        ("Tail_Set", "Nose", "Withers"),
        ("Right_Front_Elbow", "Right_Front_Wrist", "Right_Front_Paw"),
        ("Left_Front_Elbow", "Left_Front_Wrist", "Left_Front_Paw"),
        ("Right_Back_Paw", "Right_Back_Wrist", "Right_Back_Elbow"),
        ("Left_Back_Paw", "Left_Back_Wrist", "Left_Back_Elbow")
    ]

    angulos_resultados = []
    for p1, p2, p3 in angulos_a_calcular:
        if p1 in coords and p2 in coords and p3 in coords and withers and tail_set:
            angulo = calcular_angulo(coords[p1], coords[p2], coords[p3], withers, tail_set)
            angulos_resultados.append(angulo)
        else:
            angulos_resultados.append(np.nan)

    pares_distancia = [
        ("Left_Front_Paw", "Left_Back_Paw"),
        ("Right_Front_Paw", "Right_Back_Paw")
    ]

    distancias_resultados = []
    for p1, p2 in pares_distancia:
        if p1 in coords and p2 in coords:
            distancia = calcular_distancia(coords[p1], coords[p2])
            distancias_resultados.append(distancia)
        else:
            distancias_resultados.append(np.nan)

    return angulos_resultados + distancias_resultados

def segmentos_postura(predicciones, fps=30):
    """
    Recibe lista o array de predicciones (1, 2 o 3) para cada frame.  
    Devuelve lista de segmentos con postura, tiempo de inicio y duración en segundos.  
    """

    etiquetas = {1: 'Acostado', 2: 'Parado en cuatro patas', 3: 'Parado en dos patas'}
    segmentos = []

    if len(predicciones) == 0:
        return segmentos

    postura_actual = predicciones[0]
    inicio = 0

    for i in range(1, len(predicciones)):
        if predicciones[i] != postura_actual:
            duracion = (i - inicio) / fps
            segmentos.append({
                'postura': etiquetas.get(postura_actual, 'Desconocida'),
                'inicio_seg': inicio / fps,
                'duracion_seg': duracion
            })
            postura_actual = predicciones[i]
            inicio = i

    # Añadir último segmento
    duracion = (len(predicciones) - inicio) / fps
    segmentos.append({
        'postura': etiquetas.get(postura_actual, 'Desconocida'),
        'inicio_seg': inicio / fps,
        'duracion_seg': duracion
    })

    return segmentos

def guardar_segmentos_en_json(nombre_csv, segmentos, ruta_video):
    """
    Guarda los segmentos de postura y la ruta absoluta del video en un archivo .json.
    """
    ruta_json = os.path.join('temp_uploads', 'videos', nombre_csv.replace('.csv', '_etiq_tiempo.json'))

    contenido = {
        "ruta_video": os.path.abspath(ruta_video),
        "segmentos": segmentos
    }

    with open(ruta_json, 'w', encoding='utf-8') as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=4)

def buscar_video_relacionado(ruta_carpeta_videos, nombre_csv):
    """
    Extrae el nombre del video a partir del nombre del CSV antes de 'DLC_',
    y busca el archivo correspondiente en la carpeta de videos.
    """
    import re

    # Extraer la parte antes de "DLC_"
    match = re.match(r'^(.+?)DLC_', nombre_csv)
    if not match:
        return None

    nombre_base_video = match.group(1)
    extensiones_video = ['.mp4', '.avi', '.mov', '.mkv']

    for archivo in os.listdir(ruta_carpeta_videos):
        nombre_sin_ext, ext = os.path.splitext(archivo)
        if ext.lower() in extensiones_video and nombre_sin_ext == nombre_base_video:
            return os.path.join(ruta_carpeta_videos, archivo)

    return None

def procesar_csv(csv_path, partes_cuerpo):
    """
    1. Lee CSV con columnas multiíndice  
    2. Extrae coordenadas (x, y) de las partes del cuerpo para cada fila  
    3. Calcula ángulos y distancias con las funciones definidas  
    4. Almacena resultados en lista  
    5. Convierte resultados en DataFrame  
    6. Carga modelo (.pkl o .joblib) desde temp_uploads/modelo  
    7. Obtiene predicciones usando el modelo y las imprime
    """
    escribir_estado("Inicio del cálculo de ángulos y distancias")
    time.sleep(3)

    df = pd.read_csv(csv_path, header=[0,1,2])
    df.columns = df.columns.droplevel(0)

    resultados_totales = []

    for _, fila in df.iterrows():
        coords = {}

        for parte in partes_cuerpo:
            try:
                x = fila[(parte, 'x')]
                y = fila[(parte, 'y')]
                coords[parte] = (x, y)
            except KeyError as e:
                raise KeyError(f'No se encontró la parte del cuerpo en el CSV: {parte} ({e})')
            except Exception as e:
                raise Exception(f'Error inesperado al procesar la parte: {parte} ({e})')

        medidas = calcular_angulos_distancias(coords)
        resultados_totales.append(medidas)

    escribir_estado("Cálculo finalizado, preparando DataFrame")
    time.sleep(3)

    columnas = [
        "Angulo_1", "Angulo_2", "Angulo_3", "Angulo_4", "Angulo_5", "Angulo_6",
        "Distancia_1", "Distancia_2"
    ]
    df_resultados = pd.DataFrame(resultados_totales, columns=columnas)

    escribir_estado("Buscando modelo para predicción")
    time.sleep(3)

    ruta_modelo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads', 'modelo')
    modelo_path = None
    for archivo in os.listdir(ruta_modelo_dir):
        if archivo.endswith('.pkl') or archivo.endswith('.joblib'):
            modelo_path = os.path.join(ruta_modelo_dir, archivo)
            break

    if modelo_path is None:
        raise FileNotFoundError("No se encontró un archivo .pkl o .joblib en 'temp_uploads/modelo'")

    escribir_estado(f"Cargando modelo: {os.path.basename(modelo_path)}")
    time.sleep(3)

    modelo = joblib.load(modelo_path)

    escribir_estado("Realizando predicciones con el modelo")
    time.sleep(3)

    predicciones = modelo.predict(df_resultados)

    segmentos = segmentos_postura(predicciones)
    nombre_csv = os.path.basename(csv_path)

    # Obtener carpeta videos
    carpeta_videos = os.path.dirname(csv_path)
    ruta_video = buscar_video_relacionado(carpeta_videos, nombre_csv)
    if ruta_video is None:
        ruta_video = "No se encontró video relacionado"

    guardar_segmentos_en_json(nombre_csv, segmentos, ruta_video)

    escribir_estado("Predicciones completadas")
    time.sleep(3)

    return df_resultados

def obtener_partes_cuerpo():
    """
    1. Establece ruta absoluta del archivo actual  
    2. Construye ruta a 'temp_uploads'  
    3. Busca 'config.yaml' dentro de subcarpetas  
    4. Lee archivo y extrae lista bajo clave 'bodyparts'  
    5. Retorna lista con partes del cuerpo
    """
    ruta_absoluta_proyecto = os.path.dirname(os.path.abspath(__file__))
    ruta_absoluta_carpeta_temporal = os.path.join(ruta_absoluta_proyecto, 'temp_uploads')

    ruta_config = None
    for root, _, files in os.walk(ruta_absoluta_carpeta_temporal):
        if 'config.yaml' in files:
            ruta_config = os.path.join(root, 'config.yaml')
            break

    if ruta_config is None:
        raise FileNotFoundError("No se encontró config.yaml en la carpeta 'temp_uploads'")

    with open(ruta_config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    partes = config.get('bodyparts')
    if not partes or not isinstance(partes, list):
        raise ValueError("No se encontraron partes del cuerpo en el archivo de configuración")

    return partes

def procesar_todos_los_csv():
    """
    1. Establece ruta absoluta del archivo actual  
    2. Construye ruta a 'temp_uploads/videos'  
    3. Obtiene partes del cuerpo del 'config.yaml'  
    4. Itera sobre archivos '.csv' en carpeta videos  
    5. Llama a 'procesar_csv' para cada archivo
    """

    escribir_estado("Inicio de procesamiento de todos los archivos CSV")
    time.sleep(5)
    
    ruta_absoluta_proyecto = os.path.dirname(os.path.abspath(__file__))
    videos_dir = os.path.join(ruta_absoluta_proyecto, 'temp_uploads', 'videos')
    partes_cuerpo = obtener_partes_cuerpo()

    for archivo in os.listdir(videos_dir):
        if archivo.endswith('.csv'):
            ruta_csv = os.path.join(videos_dir, archivo)
            procesar_csv(ruta_csv, partes_cuerpo)

    escribir_estado("Procesamiento de todos los archivos CSV completado")
    time.sleep(5)
