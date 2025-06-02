document.addEventListener('DOMContentLoaded', () => {
    const btnAbrir = document.getElementById('chatBoton');
    const ventana = document.getElementById('chatVentana');
    const btnCerrar = document.getElementById('btnCerrarChat');
    const chatCuerpo = ventana.querySelector('.chat-cuerpo');

    const mensajes = [
        'Hola 👋 ¿En qué puedo ayudarte?',
        'Recuerda que la página puede analizar poses en animales automáticamente.',
        'Sube tus archivos y deja que la magia ocurra 🐾✨'
    ];

    const respuestasBoton = {
        esGeneralizado: 'Está diseñado para varios tipos de animales, pero funciona mejor con los que entrenamos.'
    };

    let timeoutIds = [];

    btnAbrir.addEventListener('click', () => {
        const estaVisible = !ventana.classList.contains('oculto');

        if (estaVisible) {
            ventana.classList.add('oculto');
            timeoutIds.forEach(id => clearTimeout(id));
            timeoutIds = [];
        } else {
            ventana.classList.remove('oculto');
            chatCuerpo.innerHTML = '';

            mensajes.forEach((msg, index) => {
                const delay = index * 1000;
                const timeoutId = setTimeout(() => {
                    const p = document.createElement('p');
                    p.classList.add('burbuja', 'asistente');
                    p.textContent = msg;
                    chatCuerpo.appendChild(p);
                    chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                }, delay);
                timeoutIds.push(timeoutId);
            });
        }
    });

    btnCerrar.addEventListener('click', () => {
        ventana.classList.add('oculto');
        timeoutIds.forEach(id => clearTimeout(id));
        timeoutIds = [];
    });

    ventana.querySelectorAll('.chat-btn').forEach(button => {
        button.addEventListener('click', () => {
            const key = button.getAttribute('data-key');

            // Mensaje del usuario
            const userMsg = document.createElement('p');
            userMsg.classList.add('burbuja', 'usuario');
            userMsg.textContent = button.textContent;
            chatCuerpo.appendChild(userMsg);
            chatCuerpo.scrollTop = chatCuerpo.scrollHeight;

            if (key === 'comoFunciona') {
                const respuestasDivididas = [
                    'Debes subir la carpeta del proyecto en ZIP de DeepLabCut con la que hayas entrenado tus modelos para la detección de puntos clave.',
                    'También debes subir un video o videos que quieras analizar, y que correspondan al animal o animales que tu modelo de DeepLabCut puede detectar.',
                    'Además, es necesario subir un modelo de machine learning que hayas entrenado para detectar poses en base a los puntos clave extraídos.'
                ];

                respuestasDivididas.forEach((msg, index) => {
                    setTimeout(() => {
                        const botMsg = document.createElement('p');
                        botMsg.classList.add('burbuja', 'asistente');
                        botMsg.textContent = msg;
                        chatCuerpo.appendChild(botMsg);
                        chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                    }, 700 * index);
                });
            } else if (key === 'paraQueSirve') {
                const respuestasDivididas = [
                    'Por el momento sirve para detectar tres posiciones en tres perros de distintas razas.',
                    'Solo acepta tres modelos específicos de DeepLabCut porque fue diseñado para una tesis.',
                    'Pero en el código se puede modificar y adaptar fácilmente a otros experimentos.'
                ];

                respuestasDivididas.forEach((msg, index) => {
                    setTimeout(() => {
                        const botMsg = document.createElement('p');
                        botMsg.classList.add('burbuja', 'asistente');
                        botMsg.textContent = msg;
                        chatCuerpo.appendChild(botMsg);
                        chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                    }, 700 * index);
                });
            } else if (key === 'esAutomatico') {
                const respuestasDivididas = [
                    'Sí es automático, la página está diseñada para detectar tres razas de perros en tres posiciones en videos.',
                    'Esto ayuda a no tener que analizar y generar videos etiquetados manualmente.',
                    'Luego, con el CSV generado, se calculan ángulos para pasarlos al modelo de machine learning,',
                    'que predice en qué posición está el perro, permitiendo crear etiquetas de tiempo para identificar las posiciones en el video.'
                ];

                respuestasDivididas.forEach((msg, index) => {
                    setTimeout(() => {
                        const botMsg = document.createElement('p');
                        botMsg.classList.add('burbuja', 'asistente');
                        botMsg.textContent = msg;
                        chatCuerpo.appendChild(botMsg);
                        chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                    }, 700 * index);
                });
            } else if (key === 'esGeneralizado') {
                const respuestasDivididas = [
                    'Por el momento no es generalizado para varias razas o animales.',
                    'Esta página se hizo para automatizar el análisis en perros.',
                    'El proceso de Deep Learning a Machine Learning requiere calcular ángulos específicos.',
                    'Si se cambia esa parte en el código, específicamente en el archivo csv_postprocessing.py,',
                    'se puede adaptar fácilmente a otros archivos de DeepLabCut para diferentes animales.'
                ];

                respuestasDivididas.forEach((msg, index) => {
                    setTimeout(() => {
                        const botMsg = document.createElement('p');
                        botMsg.classList.add('burbuja', 'asistente');
                        botMsg.textContent = msg;
                        chatCuerpo.appendChild(botMsg);
                        chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                    }, 700 * index);
                });
            } else {
                const botMsg = document.createElement('p');
                botMsg.classList.add('burbuja', 'asistente');
                botMsg.textContent = respuestasBoton[key] || 'No tengo una respuesta para eso.';
                setTimeout(() => {
                    chatCuerpo.appendChild(botMsg);
                    chatCuerpo.scrollTop = chatCuerpo.scrollHeight;
                }, 700);
            }
        });
    });
});