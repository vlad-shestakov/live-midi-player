from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Iterable, Optional

import mido


class AudioEngine:
    def note_on(self, note: int, velocity: int, channel: int) -> None:
        raise NotImplementedError

    def note_off(self, note: int, velocity: int, channel: int) -> None:
        raise NotImplementedError

    def control_change(self, control: int, value: int, channel: int) -> None:
        raise NotImplementedError

    def pitch_bend(self, pitch: int, channel: int) -> None:
        raise NotImplementedError

    def program_change(self, program: int, channel: int) -> None:
        raise NotImplementedError

    def forward_message(self, msg: mido.Message) -> None:
        return None

    def close(self) -> None:
        return None


class MidiOutEngine(AudioEngine):
    def __init__(self, output_port_name: str):
        self._output = mido.open_output(output_port_name)

    def note_on(self, note: int, velocity: int, channel: int) -> None:
        self._output.send(
            mido.Message("note_on", note=note, velocity=velocity, channel=channel)
        )

    def note_off(self, note: int, velocity: int, channel: int) -> None:
        self._output.send(
            mido.Message("note_off", note=note, velocity=velocity, channel=channel)
        )

    def control_change(self, control: int, value: int, channel: int) -> None:
        self._output.send(
            mido.Message(
                "control_change",
                control=control,
                value=value,
                channel=channel,
            )
        )

    def pitch_bend(self, pitch: int, channel: int) -> None:
        self._output.send(mido.Message("pitchwheel", pitch=pitch, channel=channel))

    def program_change(self, program: int, channel: int) -> None:
        self._output.send(
            mido.Message("program_change", program=program, channel=channel)
        )

    def forward_message(self, msg: mido.Message) -> None:
        self._output.send(msg)

    def close(self) -> None:
        self._output.close()


class FluidSynthEngine(AudioEngine):
    def __init__(
        self,
        soundfont_path: str,
        channel: int,
        bank: int,
        program: int,
        sample_rate: int,
        audio_driver: Optional[str],
    ):
        try:
            import fluidsynth
        except ImportError as exc:
            raise RuntimeError(
                "Engine 'fluidsynth' requires package 'pyfluidsynth'. "
                "Install dependencies from requirements.txt."
            ) from exc

        self._synth = fluidsynth.Synth(samplerate=sample_rate)
        if audio_driver:
            self._synth.start(driver=audio_driver)
        else:
            self._synth.start()

        self._sfid = self._synth.sfload(soundfont_path)
        self._synth.program_select(channel, self._sfid, bank, program)

    def note_on(self, note: int, velocity: int, channel: int) -> None:
        self._synth.noteon(channel, note, velocity)

    def note_off(self, note: int, velocity: int, channel: int) -> None:
        del velocity
        self._synth.noteoff(channel, note)

    def control_change(self, control: int, value: int, channel: int) -> None:
        self._synth.cc(channel, control, value)

    def pitch_bend(self, pitch: int, channel: int) -> None:
        # Mido pitchwheel range is [-8192, 8191], FluidSynth expects [0, 16383].
        bend_value = max(0, min(16383, pitch + 8192))
        self._synth.pitch_bend(channel, bend_value)

    def program_change(self, program: int, channel: int) -> None:
        self._synth.program_change(channel, program)

    def close(self) -> None:
        self._synth.delete()


def resolve_port(
    requested_name: Optional[str], available_ports: Iterable[str], label: str
) -> str:
    ports = list(available_ports)
    if not ports:
        raise RuntimeError(f"No {label} ports found.")

    if requested_name:
        if requested_name not in ports:
            available = ", ".join(ports)
            raise RuntimeError(
                f"{label} port '{requested_name}' not found. Available: {available}"
            )
        return requested_name

    return ports[0]


def print_ports() -> None:
    print("MIDI input ports:")
    for idx, name in enumerate(mido.get_input_names(), start=1):
        print(f"  {idx}. {name}")

    print("\nMIDI output ports:")
    for idx, name in enumerate(mido.get_output_names(), start=1):
        print(f"  {idx}. {name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Real-time MIDI keyboard listener with two playback engines: "
            "DAW/VST via MIDI out or local FluidSynth."
        )
    )
    parser.add_argument(
        "--engine",
        choices=["midi-out", "fluidsynth"],
        default="midi-out",
        help="Playback engine. Default is midi-out for DAW/VST quality.",
    )
    parser.add_argument(
        "--list-ports", action="store_true", help="List MIDI ports and exit."
    )
    parser.add_argument(
        "--input-port",
        help="MIDI input port name. If omitted, first available input is used.",
    )
    parser.add_argument(
        "--output-port",
        help="MIDI output port name for engine midi-out. If omitted, first output is used.",
    )
    parser.add_argument(
        "--soundfont",
        help="Path to .sf2 file for engine fluidsynth.",
    )
    parser.add_argument("--channel", type=int, default=0, help="Default MIDI channel 0-15.")
    parser.add_argument("--bank", type=int, default=0, help="FluidSynth preset bank.")
    parser.add_argument("--program", type=int, default=0, help="FluidSynth preset program.")
    parser.add_argument("--sample-rate", type=int, default=48000, help="Audio sample rate.")
    parser.add_argument(
        "--audio-driver",
        default=None,
        help="FluidSynth audio driver (for example dsound, wasapi, asio).",
    )
    parser.add_argument(
        "--buffer",
        type=int,
        default=64,
        help="Target audio buffer in samples (informational). Recommended: 64-128.",
    )
    parser.add_argument(
        "--latency-target-ms",
        type=float,
        default=10.0,
        help="Target end-to-end latency in milliseconds (informational).",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print incoming MIDI messages."
    )
    return parser.parse_args()


def build_engine(args: argparse.Namespace) -> AudioEngine:
    if args.engine == "midi-out":
        output_name = resolve_port(args.output_port, mido.get_output_names(), "output")
        print(f"Engine: MIDI out -> {output_name}")
        return MidiOutEngine(output_name)

    if not args.soundfont:
        raise RuntimeError("Engine 'fluidsynth' requires --soundfont path to a .sf2 file.")

    soundfont = Path(args.soundfont)
    if not soundfont.exists():
        raise RuntimeError(f"SoundFont file not found: {soundfont}")

    print(f"Engine: FluidSynth -> {soundfont}")
    return FluidSynthEngine(
        soundfont_path=str(soundfont),
        channel=args.channel,
        bank=args.bank,
        program=args.program,
        sample_rate=args.sample_rate,
        audio_driver=args.audio_driver,
    )


def handle_message(msg: mido.Message, engine: AudioEngine, default_channel: int) -> None:
    channel = getattr(msg, "channel", default_channel)

    if msg.type == "note_on":
        if msg.velocity == 0:
            engine.note_off(msg.note, 0, channel)
        else:
            engine.note_on(msg.note, msg.velocity, channel)
        return

    if msg.type == "note_off":
        engine.note_off(msg.note, msg.velocity, channel)
        return

    if msg.type == "control_change":
        engine.control_change(msg.control, msg.value, channel)
        return

    if msg.type == "pitchwheel":
        engine.pitch_bend(msg.pitch, channel)
        return

    if msg.type == "program_change":
        engine.program_change(msg.program, channel)
        return

    # Forward unsupported message types for midi-through workflow.
    engine.forward_message(msg)


def run(args: argparse.Namespace) -> None:
    if args.list_ports:
        print_ports()
        return

    if not 0 <= args.channel <= 15:
        raise RuntimeError("--channel must be in range 0..15")

    input_name = resolve_port(args.input_port, mido.get_input_names(), "input")
    engine = build_engine(args)

    print(f"Input: {input_name}")
    print(
        "Recommended audio setup: ASIO or WASAPI exclusive, "
        "buffer 64-128 samples, sample rate 48000 Hz."
    )
    print(
        f"Configured target: buffer={args.buffer} samples, "
        f"latency<={args.latency_target_ms:.1f} ms."
    )
    print("Listening for MIDI... Press Ctrl+C to stop.")

    try:
        with mido.open_input(input_name) as midi_in:
            for msg in midi_in:
                if args.verbose:
                    print(msg)
                handle_message(msg, engine, args.channel)
                time.sleep(0.0)
    finally:
        engine.close()


if __name__ == "__main__":
    try:
        run(parse_args())
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)