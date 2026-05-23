
Я планирую написать программу, которая слушает мою миди клавиатуру и воспроизводит звуки в точности
какие фреймворки python предложишь, нужно наиболее убедительное звучание

***

Установка
```
if (Test-Path .venv\Scripts\python.exe) { .venv\Scripts\python.exe -m pip install -r requirements.txt } else { python -m pip install -r requirements.txt }
Collecting mido (from -r requirements.txt (line 2))
  Downloading mido-1.3.3-py3-none-any.whl.metadata (6.4 kB)
Collecting python-rtmidi (from -r requirements.txt (line 3))
  Downloading python_rtmidi-1.5.8-cp311-cp311-win_amd64.whl.metadata (7.5 kB)
Collecting pyfluidsynth (from -r requirements.txt (line 4))
  Downloading pyfluidsynth-1.3.4-py3-none-any.whl.metadata (7.5 kB)
Collecting packaging (from mido->-r requirements.txt (line 2))
  Using cached packaging-26.2-py3-none-any.whl.metadata (3.5 kB)
Collecting numpy (from pyfluidsynth->-r requirements.txt (line 4))
  Using cached numpy-2.4.6-cp311-cp311-win_amd64.whl.metadata (6.6 kB)
Downloading mido-1.3.3-py3-none-any.whl (54 kB)
Downloading python_rtmidi-1.5.8-cp311-cp311-win_amd64.whl (132 kB)
Downloading pyfluidsynth-1.3.4-py3-none-any.whl (22 kB)
Using cached numpy-2.4.6-cp311-cp311-win_amd64.whl (12.6 MB)
Using cached packaging-26.2-py3-none-any.whl (100 kB)
Installing collected packages: python-rtmidi, packaging, numpy, pyfluidsynth, mido
```

Проверка портов
```
if (Test-Path .venv\Scripts\python.exe) { .venv\Scripts\python.exe main.py --list-ports } else { python main.py --list-ports }

MIDI input ports:
  1. LKMK3 MIDI 0
  2. MIDIIN2 (LKMK3 MIDI) 1
  3. DJM-450 2

MIDI output ports:
  1. Microsoft GS Wavetable Synth 0
  2. LKMK3 MIDI 1
  3. MIDIOUT2 (LKMK3 MIDI) 2
  4. DJM-450 3
```

Консоль приложения
```
if (Test-Path .venv\Scripts\python.exe) { .venv\Scripts\python.exe main.py --help } else { python main.py --help }
usage: main.py [-h] [--engine {midi-out,fluidsynth}] [--list-ports] [--input-port INPUT_PORT] [--output-port OUTPUT_PORT]
               [--soundfont SOUNDFONT] [--channel CHANNEL] [--bank BANK] [--program PROGRAM] [--sample-rate SAMPLE_RATE]
               [--audio-driver AUDIO_DRIVER] [--buffer BUFFER] [--latency-target-ms LATENCY_TARGET_MS] [--verbose]

Real-time MIDI keyboard listener with two playback engines: DAW/VST via MIDI out or local FluidSynth.

options:
  -h, --help            show this help message and exit
  --engine {midi-out,fluidsynth}
                        Playback engine. Default is midi-out for DAW/VST quality.
  --list-ports          List MIDI ports and exit.
  --input-port INPUT_PORT
                        MIDI input port name. If omitted, first available input is used.
  --output-port OUTPUT_PORT
                        MIDI output port name for engine midi-out. If omitted, first output is used.
  --soundfont SOUNDFONT
                        Path to .sf2 file for engine fluidsynth.
  --channel CHANNEL     Default MIDI channel 0-15.
  --bank BANK           FluidSynth preset bank.
  --program PROGRAM     FluidSynth preset program.
  --sample-rate SAMPLE_RATE
                        Audio sample rate.
  --audio-driver AUDIO_DRIVER
                        FluidSynth audio driver (for example dsound, wasapi, asio).
  --buffer BUFFER       Target audio buffer in samples (informational). Recommended: 64-128.
  --latency-target-ms LATENCY_TARGET_MS
                        Target end-to-end latency in milliseconds (informational).
  --verbose             Print incoming MIDI messages.
```
