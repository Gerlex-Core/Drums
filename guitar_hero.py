import sys
import os
import shutil
import csv
import random

import pygame
import librosa
import numpy as np
from scipy.signal import butter, lfilter

LANE_KEYS = [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5]
LANE_LETTERS = ["V", "R", "A", "Z", "N"]
LETTER_TO_LANE = {"V": 0, "G": 0, "R": 1, "A": 2, "Y": 2, "Z": 3, "B": 3, "N": 4, "O": 4}
LANE_COLORS = [(0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 0, 255), (255, 128, 0)]
STRUM_KEYS = [pygame.K_UP, pygame.K_KP1, pygame.K_KP2]

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NOTE_SPEED = 300
HIT_WINDOW = 0.2

LEVELS_DIR = "levels"
CHART_FILE = "chart.txt"


class Note:
    def __init__(self, lanes, start, end=None):
        self.lanes = lanes
        self.start = start
        self.end = end if end is not None else start
        self.hit = False

    def rect(self, current_time, travel_time):
        y_start = (current_time - self.start + travel_time) * NOTE_SPEED
        y_end = (current_time - self.end + travel_time) * NOTE_SPEED
        return y_start, y_end


def bandpass_filter(data, sr, low, high):
    nyq = sr / 2
    b, a = butter(3, [low / nyq, high / nyq], btype="band")
    return lfilter(b, a, data)


def isolate_guitar(y, sr):
    y_harm, _ = librosa.effects.hpss(y)
    return bandpass_filter(y_harm, sr, 80, 1200)


def save_chart(folder, notes):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, CHART_FILE), "w", newline="") as f:
        writer = csv.writer(f)
        for n in notes:
            letters = "+".join(LANE_LETTERS[i] for i in n.lanes)
            if n.end == n.start:
                writer.writerow([letters, "simple", f"{n.start:.3f}"])
            else:
                writer.writerow([letters, "sostenido", f"{n.start:.3f}", f"{n.end:.3f}"])


def load_chart(chart_file):
    notes = []
    with open(chart_file, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            letters = row[0].split("+")
            lanes = [LETTER_TO_LANE[l.strip().upper()] for l in letters]
            typ = row[1].strip().lower()
            start = float(row[2])
            end = float(row[3]) if typ != "simple" and len(row) > 3 else start
            notes.append(Note(lanes, start, end))
    notes.sort(key=lambda n: n.start)
    return notes


def extract_notes(path):
    y, sr = librosa.load(path, mono=True)
    guitar = isolate_guitar(y, sr)
    hop_length = 512
    onset_frames = librosa.onset.onset_detect(y=guitar, sr=sr, hop_length=hop_length)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    pitches = librosa.yin(guitar, fmin=80, fmax=880, sr=sr, hop_length=hop_length)
    notes = []
    for t in onset_times:
        idx = int(t * sr / hop_length)
        if idx < len(pitches):
            f = pitches[idx]
            if np.isnan(f):
                lane = random.randint(0, 4)
            else:
                lane = int(np.clip((f - 80) / (880 - 80) * 5, 0, 4))
        else:
            lane = random.randint(0, 4)
        notes.append(Note([lane], float(t)))
    return notes


def create_auto(audio_path, folder):
    notes = extract_notes(audio_path)
    save_chart(folder, notes)
    dest_audio = os.path.join(folder, os.path.basename(audio_path))
    if not os.path.exists(dest_audio):
        shutil.copy(audio_path, dest_audio)


def create_manual(audio_path, folder):
    notes = []
    pending = {}

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    start_ticks = pygame.time.get_ticks()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in STRUM_KEYS:
                pressed = pygame.key.get_pressed()
                lanes = [i for i, k in enumerate(LANE_KEYS) if pressed[k]]
                for lane in lanes:
                    note = Note([lane], current_time)
                    pending[lane] = note
                    notes.append(note)
            elif event.type == pygame.KEYUP:
                if event.key in LANE_KEYS:
                    lane = LANE_KEYS.index(event.key)
                    if lane in pending:
                        pending[lane].end = current_time
                        del pending[lane]

        screen.fill((30, 30, 30))
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()

    save_chart(folder, notes)
    dest_audio = os.path.join(folder, os.path.basename(audio_path))
    if not os.path.exists(dest_audio):
        shutil.copy(audio_path, dest_audio)


def note_rect(note, current_time, travel_time):
    return note.rect(current_time, travel_time)


def play_level(folder):
    audio_path = None
    for f in os.listdir(folder):
        if f.lower().endswith((".wav", ".mp3", ".ogg")):
            audio_path = os.path.join(folder, f)
            break
    if not audio_path:
        print("No se encontró el audio del nivel")
        return

    chart_file = os.path.join(folder, CHART_FILE)
    if not os.path.exists(chart_file):
        print("No se encontró chart.txt en el nivel")
        return

    notes = load_chart(chart_file)

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    travel_time = (SCREEN_HEIGHT - 100) / NOTE_SPEED

    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
    start_ticks = pygame.time.get_ticks()

    score = 0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in STRUM_KEYS:
                pressed = pygame.key.get_pressed()
                lanes = [i for i, k in enumerate(LANE_KEYS) if pressed[k]]
                for note in notes:
                    if not note.hit and abs(note.start - current_time) <= HIT_WINDOW:
                        if set(note.lanes) == set(lanes):
                            note.hit = True
                            score += 1
                            break

        screen.fill((30, 30, 30))
        pygame.draw.line(screen, (255, 255, 255), (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 2)
        for i in range(5):
            x = 160 + i * 120
            pygame.draw.rect(screen, (50, 50, 50), (x - 20, 0, 40, SCREEN_HEIGHT))

        for note in notes:
            if note.hit:
                continue
            y_start, y_end = note_rect(note, current_time, travel_time)
            if y_start > SCREEN_HEIGHT:
                note.hit = True
                continue
            for lane in note.lanes:
                x = 160 + lane * 120
                if note.end > note.start and y_end >= 0:
                    height = y_start - y_end
                    pygame.draw.rect(screen, LANE_COLORS[lane], (x - 10, int(y_end), 20, int(height)))
                if y_start >= 0:
                    pygame.draw.circle(screen, LANE_COLORS[lane], (x, int(y_start)), 20)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        pygame.display.flip()

    pygame.quit()


def select_level():
    if not os.path.isdir(LEVELS_DIR):
        print("No hay niveles disponibles")
        sys.exit(1)
    levels = [d for d in os.listdir(LEVELS_DIR) if os.path.isdir(os.path.join(LEVELS_DIR, d))]
    if not levels:
        print("No hay niveles")
        sys.exit(1)
    for i, name in enumerate(levels, 1):
        print(f"{i}. {name}")
    choice = int(input("Selecciona nivel: ")) - 1
    return os.path.join(LEVELS_DIR, levels[choice])


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("1. Jugar")
        print("2. Crear automático")
        print("3. Crear manual")
        resp = input("> ").strip()
        mode = {"1": "play", "2": "auto", "3": "manual"}.get(resp, "play")

    if mode == "play":
        folder = sys.argv[2] if len(sys.argv) > 2 else select_level()
        play_level(folder)
    elif mode == "auto":
        if len(sys.argv) < 3:
            audio = input("Ruta del audio: ").strip()
        else:
            audio = sys.argv[2]
        name = os.path.splitext(os.path.basename(audio))[0]
        folder = os.path.join(LEVELS_DIR, name)
        create_auto(audio, folder)
        print(f"Nivel creado en {folder}")
    elif mode == "manual":
        if len(sys.argv) < 3:
            audio = input("Ruta del audio: ").strip()
        else:
            audio = sys.argv[2]
        name = os.path.splitext(os.path.basename(audio))[0]
        folder = os.path.join(LEVELS_DIR, name)
        create_manual(audio, folder)
        print(f"Nivel guardado en {folder}")
    else:
        print("Modo desconocido")


if __name__ == "__main__":
    main()
