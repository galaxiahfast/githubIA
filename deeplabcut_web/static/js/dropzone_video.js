const dropzoneVideo = document.getElementById('dropzoneVideo');
const fileInputVideo = document.getElementById('fileInputVideo');

const textoOriginalVideo = 'Suelta aquí uno o más videos (.mp4, .mov, .avi...)';

// === Interacción por clic ===
dropzoneVideo.addEventListener('click', () => fileInputVideo.click());

// === Drag & Drop ===
dropzoneVideo.addEventListener('dragover', e => {
    e.preventDefault();
    dropzoneVideo.classList.add('hover');
});

dropzoneVideo.addEventListener('dragleave', () => {
    dropzoneVideo.classList.remove('hover');
});

dropzoneVideo.addEventListener('drop', e => {
    e.preventDefault();
    dropzoneVideo.classList.remove('hover');

    const files = Array.from(e.dataTransfer.files);
    manejarArchivosVideo(files);
});

// === Selección manual desde diálogo ===
fileInputVideo.addEventListener('change', () => {
    const files = Array.from(fileInputVideo.files);
    manejarArchivosVideo(files);
});

// === Función común para validar y mostrar ===
function manejarArchivosVideo(files) {
    if (files.length === 0) return;

    const videosValidos = files.filter(file => file.type.startsWith('video/'));

    if (videosValidos.length !== files.length) {
        mostrarAlerta("Solo se permiten archivos de video (.mp4, .mov, .avi, etc.)");
        fileInputVideo.value = '';
        dropzoneVideo.innerText = textoOriginalVideo;
        return;
    }

    // Asignar archivos válidos al input
    const dt = new DataTransfer();
    videosValidos.forEach(file => dt.items.add(file));
    fileInputVideo.files = dt.files;

    // Mostrar resumen
    dropzoneVideo.innerText = `${videosValidos.length} video${videosValidos.length > 1 ? 's' : ''} seleccionado${videosValidos.length > 1 ? 's' : ''}`;
}