const dropzoneModel = document.getElementById('dropzoneModel');
const fileInputModel = document.getElementById('fileInputModel');

const modelosValidos = [
    'knn',
    'svm',
    'random forest',
    'logistic regression',
    'decision tree',
    'naive bayes'
];

const modelosExtensionesValidas = ['.pkl', '.joblib'];
const textoOriginal = 'Suelta aquí tu modelo (knn, svm, random forest, logistic regression, decision tree o naive bayes)';

// === EVENTOS DE INTERACCIÓN ===

dropzoneModel.addEventListener('click', () => fileInputModel.click());

dropzoneModel.addEventListener('dragover', e => {
    e.preventDefault();
    dropzoneModel.classList.add('hover');
});

dropzoneModel.addEventListener('dragleave', () => {
    dropzoneModel.classList.remove('hover');
});

dropzoneModel.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzoneModel.classList.remove('hover');

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    if (files.length > 1) {
        mostrarAlerta('Solo se permite un archivo de modelo a la vez');
        return;
    }

    const file = files[0];
    const nombre = file.name.toLowerCase();

    const tieneExtensionValida = modelosExtensionesValidas.some(ext => nombre.endsWith(ext));
    if (!tieneExtensionValida) {
        mostrarAlerta('Archivo no válido. Solo .pkl o .joblib');
        return;
    }

    const dt = new DataTransfer();
    dt.items.add(file);
    fileInputModel.files = dt.files;

    dropzoneModel.innerText = '1 modelo seleccionado';
});

fileInputModel.addEventListener('change', () => {
    const files = Array.from(fileInputModel.files);
    if (files.length === 0) {
        dropzoneModel.innerText = textoOriginal;
        return;
    }

    if (files.length > 1) {
        mostrarAlerta('Solo se permite un archivo de modelo a la vez');
        fileInputModel.value = '';
        dropzoneModel.innerText = textoOriginal;
        return;
    }

    const file = files[0];
    const nombre = file.name.toLowerCase();

    const tieneExtensionValida = modelosExtensionesValidas.some(ext => nombre.endsWith(ext));
    if (!tieneExtensionValida) {
        mostrarAlerta('Archivo no válido. Solo .pkl o .joblib');
        fileInputModel.value = '';
        dropzoneModel.innerText = textoOriginal;
        return;
    }

    dropzoneModel.innerText = '1 modelo seleccionado';
});