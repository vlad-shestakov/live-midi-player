import time
import winsound


# Пример использования
# winsound.Beep(1000, 500)  # Частота 1000 Гц, длительность 500 мс


"""  Ре, Ми, До, До, Со (второй До звучит на октаву ниже).
 Длительность: Мелодия звучит с точным ритмическим рисунком.
 В музыкальной нотации Джона Уильямса первые три ноты (Ре, Ми, До)
 равны четвертям (относительно быстрый темп),
 четвертая нота (До) — восьмая,
 а завершающий тон (Со) — половинная нота.
"""

# Базовые частоты нот 4-й октавы (стандарт A4 = 440 Гц)
BASE_FREQS = {
    "C": 261.63,
    "C#": 277.18,
    "D": 293.66,
    "D#": 311.13,
    "E": 329.63,
    "F": 349.23,
    "F#": 369.99,
    "G": 392.00,
    "G#": 415.30,
    "A": 440.00,
    "A#": 466.16,
    "B": 493.88,
}


def get_frequency(note: str, octave: int = 4) -> float:
    """Рассчитывает точную частоту ноты с учётом октавы."""
    if note not in BASE_FREQS:
        raise ValueError(f"Неизвестная нота: {note}. Доступны: {list(BASE_FREQS.keys())}")
    # Каждая октава удваивает (вверх) или делит на 2 (вниз) частоту
    return BASE_FREQS[note] * (2 ** (octave - 4))


# ================= НАСТРОЙКИ (КОЭФФИЦИЕНТЫ) =================
TEMPO_BPM = 96  # Темп в ударах в минуту. 96 BPM близок к оригиналу фильма
OCTAVE_SHIFT = -1  # Глобальный сдвиг октав (+1 выше, -1 ниже)
DURATION_COEFF = 2.0  # Коэффициент удлинения/укорочения всех нот (1.0 = норма)
PAUSE_COEFF = 0.1  # Коэффициент паузы между нотами (0.0 = легато, >0.2 = стаккато)

# Последовательность: (Название_ноты, Октава, Множитель_длительности)
# 1.0 = четверть, 0.5 = восьмая. Ритм: ♩ ♩ ♪ ♪ ♩
CLOSE_ENCOUNTERS_SEQUENCE = [
    ("D", 4, 1.0),  # Ре
    ("E", 4, 1.0),  # Ми
    ("C", 4, 0.5),  # До (восьмая)
    ("C", 3, 0.5),  # До (на октаву ниже, восьмая)
    ("G", 4, 1.0),  # Соль
]


def play_motif(
    sequence,
    tempo_bpm=TEMPO_BPM,
    octave_shift=OCTAVE_SHIFT,
    duration_coeff=DURATION_COEFF,
    pause_coeff=PAUSE_COEFF,
):
    """Воспроизводит музыкальную последовательность через winsound.Beep."""
    # Длительность одной четверти в миллисекундах с учётом коэффициентов
    quarter_ms = (60000 / tempo_bpm) * duration_coeff

    for note, octave, mult in sequence:
        freq = get_frequency(note, octave + octave_shift)
        duration_ms = int(mult * quarter_ms)

        # Отладочный вывод (можно убрать)
        print(f"▶ {note}{octave + octave_shift:<2} | {freq:6.2f} Гц | {duration_ms:>4} мс")

        # winsound.Beep принимает частоту (int) и длительность в мс (int)
        winsound.Beep(int(freq), duration_ms)

        # Пауза между нотами для чёткой артикуляции
        pause_sec = (mult * quarter_ms / 1000) * pause_coeff
        time.sleep(pause_sec)


def main():
    print("🎬 Воспроизведение темы из «Близких контактов третьей степени» (1977)")
    print("💡 Нажмите Ctrl+C для остановки\n")
    try:
        play_motif(CLOSE_ENCOUNTERS_SEQUENCE)
        print("\n✅ Фраза успешно воспроизведена.")
    except KeyboardInterrupt:
        print("\n⛔ Воспроизведение прервано пользователем.")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
