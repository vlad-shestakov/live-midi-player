# MIDI keyboard real-time player

This project listens to a MIDI keyboard and plays sound in real time with two engines:

- `midi-out` (recommended): routes MIDI to your DAW/VST host for best sound quality.
- `fluidsynth`: standalone playback via SoundFont (`.sf2`) inside Python.

## Setup

1. Create virtual environment and install dependencies:
   - `install.bat`
2. Activate environment:
   - `.venv\Scripts\activate`

## List MIDI ports

```bash
python main.py --list-ports
```

## Run with best quality (DAW/VST workflow)

Use a virtual MIDI cable and open that port in your DAW (Reaper, Cantabile, etc.) with a high quality VST instrument.

```bash
python main.py --engine midi-out --input-port "YOUR_KEYBOARD_PORT" --output-port "YOUR_DAW_MIDI_IN"
```

## Run standalone with FluidSynth

```bash
python main.py --engine fluidsynth --input-port "YOUR_KEYBOARD_PORT" --soundfont "D:\SoundFonts\piano.sf2"
```

Optional FluidSynth tuning:

```bash
python main.py --engine fluidsynth --input-port "YOUR_KEYBOARD_PORT" --soundfont "D:\SoundFonts\piano.sf2" --audio-driver wasapi --sample-rate 48000 --buffer 64
```

## Low-latency targets

- Driver: ASIO or WASAPI exclusive mode.
- Buffer: `64-128` samples.
- Sample rate: `48000` Hz.
- Keep extra processing in the MIDI loop minimal.

## MVP data flow

`MIDI keyboard -> python-rtmidi/mido input -> message handling -> selected engine -> audio output`
