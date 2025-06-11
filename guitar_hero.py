import sys
import random
import os
import pygame
import librosa
import numpy as np

LANE_KEYS = [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5]
LANE_COLORS = [(0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 0, 255), (255, 128, 0)]
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NOTE_SPEED = 300  # pixels per second
HIT_WINDOW = 0.2   # seconds allowed for a hit

class Note:
    def __init__(self, lane, time):
        self.lane = lane
        self.time = time
        self.hit = False

    def pos(self, current_time, travel_time):
        y = (current_time - self.time + travel_time) * NOTE_SPEED
        return 160 + self.lane * 120, y


def extract_notes(path):
    y, sr = librosa.load(path, mono=True)
    hop_length = 512
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    pitches = librosa.yin(y, fmin=80, fmax=880, sr=sr, hop_length=hop_length)
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
        notes.append(Note(lane, float(t)))
    return notes


def main():
    if len(sys.argv) < 2:
        print("Usage: python guitar_hero.py path/to/song.wav")
        return
    song_path = sys.argv[1]
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    notes = extract_notes(song_path)
    travel_time = (SCREEN_HEIGHT - 100) / NOTE_SPEED

    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    start_ticks = pygame.time.get_ticks()

    font = pygame.font.Font(None, 36)
    score = 0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in LANE_KEYS:
                    lane = LANE_KEYS.index(event.key)
                    for note in notes:
                        if note.lane == lane and not note.hit:
                            if abs(note.time - current_time) <= HIT_WINDOW:
                                note.hit = True
                                score += 1
                                break

        screen.fill((30, 30, 30))
        pygame.draw.line(screen, (255, 255, 255), (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 2)
        for i in range(5):
            x = 160 + i * 120
            pygame.draw.rect(screen, (50,50,50), (x-20,0,40,SCREEN_HEIGHT))

        for note in notes:
            if note.hit:
                continue
            x, y = note.pos(current_time, travel_time)
            if y > SCREEN_HEIGHT:
                note.hit = True
                continue
            if y >= 0:
                pygame.draw.circle(screen, LANE_COLORS[note.lane], (x, int(y)), 20)

        score_text = font.render(f"Score: {score}", True, (255,255,255))
        screen.blit(score_text, (10,10))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
