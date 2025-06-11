# Drums

Este repositorio contiene un sencillo juego tipo *Guitar Hero* escrito en Python.

## Requisitos

- Python 3
- [Pygame](https://www.pygame.org/)
- [Librosa](https://librosa.org/)

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el script indicando un archivo de audio (preferiblemente WAV) o una
carpeta de nivel previamente generada. Si pasas un archivo el programa
creará la carpeta con las notas extraídas de la guitarra:

```bash
python guitar_hero.py ruta/al/archivo.wav
# o bien
python guitar_hero.py levels/NombreDeLaCancion
```

Las teclas para jugar son:

- **F1**: verde
- **F2**: rojo
- **F3**: amarillo
- **F4**: azul
- **F5**: naranja

El programa analiza la pista para detectar los ataques (onsets) y asignar
cada nota a uno de los cinco colores según su frecuencia aproximada.
Cuando la nota alcance la barra inferior, presiona la tecla correspondiente
para sumar puntos.

Cada canción se guarda en `levels/<Nombre>` con el audio y un archivo
`notes.csv`. Al ejecutar nuevamente el juego con esa carpeta se cargará el
nivel sin volver a analizar la pista.
