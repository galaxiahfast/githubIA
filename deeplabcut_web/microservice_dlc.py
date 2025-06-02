import os
import deeplabcut
import yaml
import time
import tempfile



from csv_postprocessing import procesar_todos_los_csv
from estado import escribir_estado



def obtener_ruta_yaml(base_dir):
    for root, dirs, files in os.walk(base_dir):
        if 'config.yaml' in files:
            return os.path.join(root, 'config.yaml')
    raise FileNotFoundError("No se encontró config.yaml en el proyecto")

def actualizar_project_path_yaml(config_path, nueva_ruta):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config['project_path'] = nueva_ruta
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

def analizar_videos_dlc(base_dir):
    carpeta_proyecto = os.path.dirname(obtener_ruta_yaml(base_dir))
    config_path = os.path.join(carpeta_proyecto, 'config.yaml')

    actualizar_project_path_yaml(config_path, os.path.abspath(carpeta_proyecto))

    videos_dir = os.path.abspath(os.path.join(base_dir, 'videos'))
    videos = [os.path.join(videos_dir, f) for f in os.listdir(videos_dir)
              if f.lower().endswith(('.mp4', '.avi', '.mov'))]

    if not videos:
        raise ValueError("No se encontraron videos para analizar")

    escribir_estado("Importación de datos")
    time.sleep(5)

    escribir_estado("Analizando videos con DeepLabCut")
    deeplabcut.analyze_videos(config_path, videos, save_as_csv=True)
    time.sleep(5)

    escribir_estado("Generando videos etiquetados")
    deeplabcut.create_labeled_video(config_path, videos, trailpoints=5, draw_skeleton=True)
    time.sleep(5)

    escribir_estado("Ejecutando postprocesamiento")
    procesar_todos_los_csv()

    escribir_estado("Análisis completado")
    return os.path.join(carpeta_proyecto, 'videos')