const dropzoneZip = document.getElementById('dropzoneZip');
const fileInputZip = document.getElementById('fileInputZip');

const textoOriginalZip = 'Suelta aquí tu ZIP del proyecto DeepLabCut';

// === Interacción por clic ===
dropzoneZip.addEventListener('click', () => fileInputZip.click());

// === Drag & Drop ===
dropzoneZip.addEventListener('dragover', e => {
    e.preventDefault();
    dropzoneZip.classList.add('hover');
});

dropzoneZip.addEventListener('dragleave', () => {
    dropzoneZip.classList.remove('hover');
});

dropzoneZip.addEventListener('drop', async e => {
    e.preventDefault();
    dropzoneZip.classList.remove('hover');

    const files = Array.from(e.dataTransfer.files);

    if (files.length !== 1 || !files[0].name.toLowerCase().endsWith('.zip')) {
        mostrarAlerta('Solo se permite un archivo ZIP');
        return;
    }

    // Asignar archivo al input y mostrar resumen
    const dt = new DataTransfer();
    dt.items.add(files[0]);
    fileInputZip.files = dt.files;

    const conteo = await contarContenidoZip(files[0]);
    dropzoneZip.innerText = `ZIP contiene ${conteo.archivos} archivo(s) en ${conteo.carpetas} carpeta(s)`;
});

// === Selección manual desde diálogo ===
fileInputZip.addEventListener('change', async () => {
    const files = Array.from(fileInputZip.files);

    if (files.length !== 1 || !files[0].name.toLowerCase().endsWith('.zip')) {
        mostrarAlerta('Solo se permite un archivo ZIP');
        fileInputZip.value = '';
        dropzoneZip.innerText = textoOriginalZip;
        return;
    }

    const conteo = await contarContenidoZip(files[0]);
    dropzoneZip.innerText = `ZIP contiene ${conteo.archivos} archivo(s) en ${conteo.carpetas} carpeta(s)`;
});