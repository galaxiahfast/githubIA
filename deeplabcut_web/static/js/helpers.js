function mostrarAlerta(mensaje) {
    const alerta = document.createElement('div');
    alerta.className = 'alerta';
    alerta.innerText = mensaje;
    document.body.appendChild(alerta);
    setTimeout(() => alerta.remove(), 3000);
}

async function contarContenidoZip(file) {
    const zip = await JSZip.loadAsync(file);
    let archivos = 0;
    const carpetas = new Set();

    Object.keys(zip.files).forEach((filename) => {
        const obj = zip.files[filename];
        if (!obj.dir) archivos++;
        const partes = filename.split('/');
        if (partes.length > 1) carpetas.add(partes.slice(0, -1).join('/'));
    });

    return { archivos, carpetas: carpetas.size };
}

function leerDirectorioRecursivo(entry) {
    return new Promise((resolve) => {
        const archivos = [];

        function leer(entry, path = '') {
            return new Promise((res) => {
                if (entry.isFile) {
                    entry.file((file) => {
                        file.relativePath = path + file.name;
                        archivos.push(file);
                        res();
                    });
                } else if (entry.isDirectory) {
                    const dirReader = entry.createReader();
                    dirReader.readEntries(async (entries) => {
                        for (const subEntry of entries) {
                            await leer(subEntry, path + entry.name + '/');
                        }
                        res();
                    });
                }
            });
        }

        leer(entry).then(() => resolve(archivos));
    });
}

function limpiarTodo() {
    const fileInputZip = document.getElementById('fileInputZip');
    const fileInputVideo = document.getElementById('fileInputVideo');
    const fileInputModel = document.getElementById('fileInputModel');

    const dropzoneZip = document.getElementById('dropzoneZip');
    const dropzoneVideo = document.getElementById('dropzoneVideo');
    const dropzoneModel = document.getElementById('dropzoneModel');

    fileInputZip.value = '';
    fileInputVideo.value = '';
    fileInputModel.value = '';

    dropzoneZip.innerText = 'Suelta aquí tu carpeta o ZIP';
    dropzoneVideo.innerText = 'Suelta aquí uno o más videos (.mp4, .mov, .avi...)';
    dropzoneModel.innerText = 'Suelta aquí tu modelo (knn, svm, random forest, logistic regression, decision tree o naive bayes)';
}

let intervaloEstado;

function iniciarPollingEstado() {
    intervaloEstado = setInterval(async () => {
        try {
            const res = await fetch('/estado');
            if (res.ok) {
                const data = await res.json();
                const mensajeCarga = document.getElementById('mensajeCarga');

                if (mensajeCarga && data.mensaje) {
                    mensajeCarga.innerText = data.mensaje;

                    if (data.mensaje.toLowerCase().includes('error')) {
                        detenerPollingEstado();
                        mostrarAlertaError(data.mensaje);
                    }

                    if (data.mensaje.toLowerCase().includes('completado')) {
                        detenerPollingEstado();
                        mostrarMensajeFinal();
                    }
                }
            }
        } catch (error) {
            console.error('Error al obtener estado:', error);
        }
    }, 2000);
}

async function mostrarMensajeFinal() {
    try {
        const res = await fetch('/video_y_etiquetas');
        if (!res.ok) throw new Error('No se pudo obtener el video con etiquetas');
        const data = await res.json();

        // Convierte backslashes en slash para evitar problemas en URL
        const videoUrl = data.ruta_video.replace(/\\/g, '/');
        const segmentos = data.segmentos;

        const form = document.getElementById('uploadForm');
        form.innerHTML = `
            <div class="video-container" style="max-width: 640px; margin: auto;">
                <video id="videoAnalizado" controls width="100%" style="display: block; margin-bottom: 8px;">
                    <source src="${videoUrl}" type="video/mp4">
                    Tu navegador no soporta el video.
                </video>
                <div id="barraEtiquetas" style="position: relative; height: 20px; background: #ddd; border-radius: 4px; overflow: hidden;"></div>
                <button onclick="location.reload()" style="margin-top: 10px;">Regresar</button>
            </div>
        `;

        const video = document.getElementById('videoAnalizado');
        const barra = document.getElementById('barraEtiquetas');

        video.onloadedmetadata = () => {
            const duracion = video.duration || 1;
            barra.innerHTML = '';

            const coloresPostura = {
                'Acostado': '#1f77b4',
                'Parado en cuatro patas': '#ff7f0e',
                'Parado en dos patas': '#2ca02c',
                'Desconocida': '#d62728'
            };

            segmentos.forEach(seg => {
                const inicio = (seg.inicio_seg / duracion) * 100;
                const ancho = (seg.duracion_seg / duracion) * 100;

                const div = document.createElement('div');
                div.style.position = 'absolute';
                div.style.left = `${inicio}%`;
                div.style.width = `${ancho}%`;
                div.style.height = '100%';

                // Color según postura
                div.style.backgroundColor = coloresPostura[seg.postura] || '#cccccc';
                div.title = seg.postura;

                barra.appendChild(div);
            });
        };

    } catch (error) {
        console.error('Error al mostrar video:', error);
        mostrarAlertaError('Error al cargar el video con etiquetas');
    }
}

function mostrarAlertaError(mensaje) {
    const alerta = document.createElement('div');
    alerta.className = 'alerta error';
    alerta.innerText = mensaje;
    document.body.appendChild(alerta);

    setTimeout(() => {
        location.reload();
    }, 10000);
}

function detenerPollingEstado() {
    clearInterval(intervaloEstado);
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const fileInputZip = document.getElementById('fileInputZip');
    const fileInputVideo = document.getElementById('fileInputVideo');
    const fileInputModel = document.getElementById('fileInputModel');
    const btnLimpiar = document.getElementById('btnLimpiar');

    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', limpiarTodo);
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (
            fileInputZip.files.length !== 1 ||
            fileInputVideo.files.length === 0 ||
            fileInputModel.files.length !== 1
        ) {
            mostrarAlerta('Por favor, completa los tres campos: ZIP, videos y modelo');
            return;
        }

        const formData = new FormData(form);

        try {
            const respuesta = await fetch('/procesar', {
                method: 'POST',
                body: formData
            });

            if (respuesta.ok) {
                mostrarAlerta('Datos enviados correctamente');
                form.innerHTML = `
                    <div class="spinner">
                        <div class="lds-ring">
                            <div></div><div></div><div></div><div></div>
                        </div>
                        <p id="mensajeCarga" class="mensaje-carga">Importación de datos</p>
                    </div>
                `;
                iniciarPollingEstado();
            } else {
                mostrarAlerta('Error al enviar los datos');
            }
        } catch (error) {
            console.error(error);
            mostrarAlerta('Error de conexión');
        }
    });
});

