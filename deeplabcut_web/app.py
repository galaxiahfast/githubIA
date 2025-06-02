import threading
import tempfile
import os
from flask import Flask, request, render_template, jsonify
from subir_archivos_a_la_carpeta_temporal import guardar_archivos
import microservice_dlc

app = Flask(__name__)

carpeta_temp = tempfile.gettempdir()
RUTA_ESTADO = os.path.join(carpeta_temp, 'estado_dlc.txt')



from flask import send_file
import zipfile
import io




import json  # Mejor que usar eval

@app.route('/video_y_etiquetas')
def video_y_etiquetas():
    carpeta_videos = os.path.join('temp_uploads', 'videos')
    for archivo in os.listdir(carpeta_videos):
        if archivo.endswith('.json'):
            with open(os.path.join(carpeta_videos, archivo), 'r', encoding='utf-8') as f:
                datos = json.load(f)
                ruta_absoluta = datos['ruta_video']
                nombre_video = os.path.basename(ruta_absoluta)
                datos['ruta_video'] = f'/videos/{nombre_video}'
                return jsonify(datos)
    return jsonify({'error': 'No se encontraron etiquetas'}), 404





@app.route('/descargar_zip')
def descargar_zip():
    carpeta_videos = os.path.join('temp_uploads', 'videos')
    memoria_zip = io.BytesIO()

    with zipfile.ZipFile(memoria_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(carpeta_videos):
            for archivo in files:
                ruta_completa = os.path.join(root, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, carpeta_videos)
                zf.write(ruta_completa, ruta_relativa)

    memoria_zip.seek(0)
    return send_file(
        memoria_zip,
        mimetype='application/zip',
        as_attachment=True,
        download_name='resultados_videos.zip'
    )



@app.route('/estado')
def obtener_estado():
    try:
        with open(RUTA_ESTADO, 'r', encoding='utf-8') as f:
            mensaje = f.read()
    except FileNotFoundError:
        mensaje = "Esperando inicio de análisis"
    return jsonify({'mensaje': mensaje})

def ejecutar_analisis_dlc(base_dir):
    try:
        microservice_dlc.analizar_videos_dlc(base_dir)
    except Exception as e:
        error_msg = f"Error durante el análisis DLC: {str(e)}"
        print(error_msg)
        with open(RUTA_ESTADO, 'w', encoding='utf-8') as f:
            f.write(error_msg)

@app.route('/')
def index():
    return render_template('index.html')






from flask import send_from_directory

@app.route('/videos/<path:filename>')
def servir_video(filename):
    carpeta_videos = os.path.join('temp_uploads', 'videos')
    return send_from_directory(carpeta_videos, filename)








@app.route('/procesar', methods=['POST'])
def procesar():
    try:
        archivos_guardados, ruta_modelo = guardar_archivos(request)
        base_dir = 'temp_uploads'

        hilo = threading.Thread(target=ejecutar_analisis_dlc, args=(base_dir,))
        hilo.start()

        return f'Se guardaron {len(archivos_guardados)} archivos. Análisis en proceso'
    except Exception as e:
        return f'Error: {str(e)}', 400

if __name__ == '__main__':
    app.run(debug=True)