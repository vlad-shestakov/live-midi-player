# MIDI keyboard real-time player

Проект слушает MIDI-клавиатуру и воспроизводит звук в реальном времени.

Поддерживаются два движка:

- `midi-out` (рекомендуется): отправка MIDI в DAW/VST для лучшего качества звука.
- `fluidsynth`: автономный вариант через SoundFont (`.sf2`) внутри Python.

## Быстрый старт

1. Установка зависимостей:

```bat
install.bat
```

2. Активация окружения:

```bat
.venv\Scripts\activate
```

3. Настройка портов (основной сценарий):

```bat
configure_ports.bat
```

4. Запуск плеера с текущими сохраненными настройками:

```bat
python main.py
```

## Где хранятся выбранные порты

Текущие `input/output` сохраняются в файле:

- `midi_ports.json`

Приоритет выбора портов:

1. Явные CLI-параметры `--input-port` / `--output-port`
2. Значения из `midi_ports.json`
3. Первый доступный порт из системы (fallback)

## configure_ports.bat

### Интерактивное меню (основной кейс)

Запуск без параметров:

```bat
configure_ports.bat
```

В меню доступны действия:

- показать сохраненные настройки;
- показать текущие MIDI порты;
- изменить input/output;
- запуск `main.py`.

### Параметризованные команды

Показать сохраненные настройки:

```bat
configure_ports.bat show-config
```

Показать текущие доступные порты:

```bat
configure_ports.bat list-ports
```

Сохранить новый input/output:

```bat
configure_ports.bat set --input-port "LKMK3 MIDI 0" --output-port "Microsoft GS Wavetable Synth 0"
```

Поддерживается частичное обновление:

```bat
configure_ports.bat set --input-port "LKMK3 MIDI 0"
```

Запустить программу с дополнительными аргументами:

```bat
configure_ports.bat run --engine midi-out
```

## Команды main.py

Список портов:

```bat
python main.py --list-ports
```

Показать сохраненный конфиг:

```bat
python main.py --show-config
```

Сохранить порты в конфиг:

```bat
python main.py --set-config --input-port "LKMK3 MIDI 0" --output-port "Microsoft GS Wavetable Synth 0"
```

Запуск с лучшим качеством (через MIDI Out):

```bat
python main.py --engine midi-out
```

Пример для конкретных портов:

```bat
python main.py --engine midi-out --input-port "LKMK3 MIDI 0" --output-port "Microsoft GS Wavetable Synth 0"
```

Standalone через FluidSynth:

```bat
python main.py --engine fluidsynth --soundfont "D:\SoundFonts\piano.sf2" --audio-driver wasapi --sample-rate 48000 --buffer 64
```

## Проверка гипотезы: mido + python-rtmidi (live)

Цель проверки: убедиться, что смена инструмента (`program_change`) действительно применяется в живом потоке и слышимо меняет тембр на стороне внешнего синта/DAW.

1. Запусти слушатель в verbose-режиме:

```bat
python main.py --engine midi-out --verbose
```

2. В DAW/контроллере отправь в одном сеансе:
   - `program_change` для Piano (например, program `0`);
   - сыграй несколько нот;
   - `program_change` для Organ (например, program `16`);
   - снова сыграй несколько нот;
   - `program_change` для Strings (например, program `48`);
   - снова сыграй несколько нот.

3. Если устройство использует Bank Select, отправляй последовательность:
   - `CC0` (Bank MSB) -> `CC32` (Bank LSB) -> `ProgramChange`.

Ожидаемые признаки в консоли:
- строки `[instrument] ... cc0/cc32 ...` при смене банка;
- строка `[instrument] ... program=... bank=...` при смене программы;
- строки `[play] ... program=... bank=...` на входящих `note_on`, чтобы сопоставить игру с активным тембром.

Критерий успеха:
- логи фиксируют смену программы без ошибок;
- тембр слышимо меняется после `program_change`.

Важно: итоговый звук определяется внешним синтом/плагином (DAW/VST/устройство). `mido + python-rtmidi` только корректно передает MIDI-сообщения.

## Рекомендации по задержке

- Используй ASIO или WASAPI exclusive.
- Buffer: `64-128` samples.
- Sample rate: `48000` Hz.
- `Microsoft GS Wavetable Synth` часто дает заметную задержку; для более живого отклика лучше DAW/VST или tuned FluidSynth.
