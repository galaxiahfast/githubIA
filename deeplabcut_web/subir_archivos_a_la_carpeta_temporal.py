import os
import shutil
from werkzeug.utils import secure_filename
import zipfile
from io import BytesIO

TEMP_UPLOADS_DIR = 'temp_uploads'

def limpiar_carpeta_temp():
    if os.path.exists(TEMP_UPLOADS_DIR):
        shutil.rmtree(TEMP_UPLOADS_DIR)
    os.makedirs(TEMP_UPLOADS_DIR)

def guardar_archivos(request):
    """
    Valida que se reciba un único archivo ZIP en 'archivos',
    además de videos y modelo.
    Limpia la carpeta temporal, descomprime el ZIP respetando estructura,
    guarda videos y modelo en carpetas separadas.
    
    Retorna lista de rutas guardadas y ruta del modelo.
    """
    archivos = request.files.getlist('archivos')
    videos = request.files.getlist('videos')
    modelo = request.files.get('modelo')

    # Validaciones estrictas
    if len(archivos) != 1 or not archivos[0].filename.lower().endswith('.zip'):
        raise ValueError("Debe enviarse un único archivo ZIP en 'archivos'.")
    if not videos or len(videos) == 0:
        raise ValueError("No se recibieron videos.")
    if not modelo or modelo.filename == '':
        raise ValueError("No se recibió archivo de modelo.")

    limpiar_carpeta_temp()
    archivos_guardados = []

    # Procesar ZIP
    archivo_zip = archivos[0]
    with zipfile.ZipFile(BytesIO(archivo_zip.read())) as zip_ref:
        for zip_info in zip_ref.infolist():
            if not zip_info.is_dir():
                nombre_seguro = secure_filename(os.path.basename(zip_info.filename))
                carpeta_relativa = os.path.dirname(zip_info.filename)
                ruta_guardar = os.path.join(TEMP_UPLOADS_DIR, carpeta_relativa)
                os.makedirs(ruta_guardar, exist_ok=True)
                ruta_completa = os.path.join(ruta_guardar, nombre_seguro)
                with zip_ref.open(zip_info) as source, open(ruta_completa, "wb") as target:
                    shutil.copyfileobj(source, target)
                archivos_guardados.append(ruta_completa)

    # Guardar videos (todos en temp_uploads/videos/)
    videos_dir = os.path.join(TEMP_UPLOADS_DIR, 'videos')
    os.makedirs(videos_dir, exist_ok=True)
    for file in videos:
        filename = secure_filename(file.filename)
        ruta_completa = os.path.join(videos_dir, filename)
        file.save(ruta_completa)
        archivos_guardados.append(ruta_completa)

    # Guardar modelo (en temp_uploads/modelo/)
    modelo_dir = os.path.join(TEMP_UPLOADS_DIR, 'modelo')
    os.makedirs(modelo_dir, exist_ok=True)
    filename = secure_filename(modelo.filename)
    ruta_completa_modelo = os.path.join(modelo_dir, filename)
    modelo.save(ruta_completa_modelo)

    return archivos_guardados, ruta_completa_modelo
