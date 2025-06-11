# Drums

Este repositorio contiene un sencillo juego tipo *Guitar Hero* escrito en Python.

## Requisitos

- Python 3
- [Pygame](https://www.pygame.org/)
- [Librosa](https://librosa.org/)

Instala las dependencias con:

```bash
pip install pygame librosa
```

## Uso

Ejecuta el script indicando el archivo de audio (preferiblemente WAV) del que
quieres extraer las notas de guitarra:

```bash
python guitar_hero.py ruta/al/archivo.wav
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
