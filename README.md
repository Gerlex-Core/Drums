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

El juego cuenta con tres modos:

1. **Jugar** un nivel existente
2. **Crear** un nivel automáticamente a partir de un audio
3. **Crear manualmente** grabando las pulsaciones mientras suena la canción

Al ejecutar el script sin argumentos aparecerá un menú de texto para elegir
el modo y la canción. También puedes indicarlo desde la línea de comandos.

Para crear un nivel de forma automática o manual basta con indicar el archivo
de audio (preferiblemente WAV). Se generará una carpeta en `levels/<Nombre>`
con el audio y un archivo `chart.txt` donde se guardan las notas.

La sintaxis de `chart.txt` es una línea por nota con el siguiente formato:

```
<letra>,<tipo>,<inicio>[,<fin>]
```

Donde la **letra** puede ser `V` (verde), `R` (rojo), `A` (amarillo), `Z`
(azul) u `N` (naranja). El **tipo** es `simple` o `sostenido`; si es
`simple` sólo se especifica el instante de inicio, mientras que un
`sostenido` indica el tiempo de inicio y el de finalización.

Ejemplo:

```
V,simple,1.234
R+sostenido,0.500,2.000
```

```bash
# crear automáticamente un nivel
python guitar_hero.py auto mi_cancion.wav

# crear manualmente
python guitar_hero.py manual mi_cancion.wav

# jugar un nivel existente
python guitar_hero.py play levels/NombreDeLaCancion
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
`chart.txt`. Al ejecutar nuevamente el juego con esa carpeta se cargará el
nivel sin volver a analizar la pista.
