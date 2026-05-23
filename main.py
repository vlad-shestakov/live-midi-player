from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, Optional

import mido

CONFIG_FILENAME = "midi_ports.json"


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
                "Для движка 'fluidsynth' требуется пакет 'pyfluidsynth'. "
                "Установите зависимости из requirements.txt."
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


def default_config_path() -> Path:
    return Path(__file__).resolve().parent / CONFIG_FILENAME


def load_port_config(config_path: Path) -> dict[str, Optional[str]]:
    if not config_path.exists():
        return {"input_port": None, "output_port": None}

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            raw = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Некорректный JSON в файле конфигурации: {config_path}") from exc

    input_port = raw.get("input_port")
    output_port = raw.get("output_port")
    return {
        "input_port": input_port if isinstance(input_port, str) and input_port else None,
        "output_port": output_port
        if isinstance(output_port, str) and output_port
        else None,
    }


def save_port_config(
    config_path: Path,
    input_port: Optional[str],
    output_port: Optional[str],
) -> None:
    payload = {"input_port": input_port or "", "output_port": output_port or ""}
    with config_path.open("w", encoding="utf-8") as config_file:
        json.dump(payload, config_file, ensure_ascii=False, indent=2)
        config_file.write("\n")


def print_ports() -> tuple[list[str], list[str]]:
    inputs = list(mido.get_input_names())
    outputs = list(mido.get_output_names())

    print("Входные MIDI-порты:")
    for idx, name in enumerate(inputs, start=1):
        print(f"  {idx}. {name}")

    print("\nВыходные MIDI-порты:")
    for idx, name in enumerate(outputs, start=1):
        print(f"  {idx}. {name}")

    return inputs, outputs


def print_ports_json(kind: Optional[str] = None) -> None:
    inputs = list(mido.get_input_names())
    outputs = list(mido.get_output_names())

    if kind == "input":
        print(json.dumps(inputs, ensure_ascii=False, indent=2))
        return

    if kind == "output":
        print(json.dumps(outputs, ensure_ascii=False, indent=2))
        return

    print(json.dumps({"inputs": inputs, "outputs": outputs}, ensure_ascii=False, indent=2))


def resolve_port(
    cli_value: Optional[str],
    config_value: Optional[str],
    available_ports: Iterable[str],
    label: str,
) -> str:
    ports = list(available_ports)
    if not ports:
        raise RuntimeError(f"Не найдены MIDI-порты ({label}).")

    if cli_value:
        if cli_value not in ports:
            available = ", ".join(ports)
            raise RuntimeError(
                f"Порт ({label}) '{cli_value}' не найден. Доступные: {available}"
            )
        return cli_value

    if config_value:
        if config_value in ports:
            return config_value
        print(
            f"Предупреждение: сохраненный порт ({label}) '{config_value}' недоступен. "
            f"Используется резервный вариант '{ports[0]}'."
        )

    return ports[0]


def show_saved_config(config_path: Path) -> None:
    config = load_port_config(config_path)
    print(f"Файл конфигурации: {config_path}")
    print(f"Сохраненный входной порт : {config.get('input_port') or '<не задан>'}")
    print(f"Сохраненный выходной порт: {config.get('output_port') or '<не задан>'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Слушатель MIDI-клавиатуры в реальном времени с двумя движками "
            "воспроизведения: DAW/VST через MIDI Out или локальный FluidSynth."
        )
    )
    parser.add_argument(
        "--engine",
        choices=["midi-out", "fluidsynth"],
        default="midi-out",
        help="Движок воспроизведения. По умолчанию midi-out для качества DAW/VST.",
    )
    parser.add_argument(
        "--list-ports", action="store_true", help="Показать MIDI-порты и выйти."
    )
    parser.add_argument(
        "--list-ports-json",
        action="store_true",
        help="Показать MIDI-порты в JSON-формате и выйти.",
    )
    parser.add_argument(
        "--ports-kind",
        choices=["input", "output"],
        help="Ограничить вывод --list-ports-json списком input/output.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Показать сохраненную конфигурацию входного/выходного портов и выйти.",
    )
    parser.add_argument(
        "--set-config",
        action="store_true",
        help="Сохранить --input-port и/или --output-port в конфигурацию и выйти.",
    )
    parser.add_argument(
        "--config",
        default=str(default_config_path()),
        help="Путь к JSON-файлу конфигурации MIDI-портов.",
    )
    parser.add_argument(
        "--input-port",
        help="Имя входного MIDI-порта. Если не указано, берется первый доступный.",
    )
    parser.add_argument(
        "--output-port",
        help="Имя выходного MIDI-порта для движка midi-out. Если не указано, берется первый доступный.",
    )
    parser.add_argument(
        "--soundfont",
        help="Путь к .sf2-файлу для движка fluidsynth.",
    )
    parser.add_argument(
        "--channel", type=int, default=0, help="MIDI-канал по умолчанию: 0-15."
    )
    parser.add_argument("--bank", type=int, default=0, help="Банк пресета FluidSynth.")
    parser.add_argument(
        "--program", type=int, default=0, help="Номер пресета FluidSynth."
    )
    parser.add_argument(
        "--sample-rate", type=int, default=48000, help="Частота дискретизации аудио."
    )
    parser.add_argument(
        "--audio-driver",
        default=None,
        help="Аудиодрайвер FluidSynth (например: dsound, wasapi, asio).",
    )
    parser.add_argument(
        "--buffer",
        type=int,
        default=64,
        help="Целевой аудиобуфер в сэмплах (информационно). Рекомендуется: 64-128.",
    )
    parser.add_argument(
        "--latency-target-ms",
        type=float,
        default=10.0,
        help="Целевая сквозная задержка в миллисекундах (информационно).",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Печатать входящие MIDI-сообщения."
    )
    parser.add_argument(
        "--save-ports",
        action="store_true",
        help="Сохранить выбранные входной/выходной порты в конфигурацию перед запуском.",
    )
    return parser.parse_args()


def update_saved_config(args: argparse.Namespace, config_path: Path) -> None:
    if not args.input_port and not args.output_port:
        raise RuntimeError(
            "Используйте --input-port и/или --output-port вместе с --set-config."
        )

    current = load_port_config(config_path)
    input_names = list(mido.get_input_names())
    output_names = list(mido.get_output_names())

    new_input = current.get("input_port")
    new_output = current.get("output_port")

    if args.input_port:
        new_input = resolve_port(args.input_port, None, input_names, "входной")
    if args.output_port:
        new_output = resolve_port(args.output_port, None, output_names, "выходной")

    save_port_config(config_path, new_input, new_output)
    print(f"Конфигурация сохранена в {config_path}")
    print(f"Текущий входной порт : {new_input or '<не задан>'}")
    print(f"Текущий выходной порт: {new_output or '<не задан>'}")


def build_engine(args: argparse.Namespace, output_name: Optional[str]) -> AudioEngine:
    if args.engine == "midi-out":
        if not output_name:
            raise RuntimeError(
                "Не удалось определить выходной порт для движка midi-out."
            )
        print(f"Движок: MIDI out -> {output_name}")
        return MidiOutEngine(output_name)

    if not args.soundfont:
        raise RuntimeError(
            "Для движка 'fluidsynth' необходимо указать --soundfont с путем к .sf2-файлу."
        )

    soundfont = Path(args.soundfont)
    if not soundfont.exists():
        raise RuntimeError(f"Файл SoundFont не найден: {soundfont}")

    print(f"Движок: FluidSynth -> {soundfont}")
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
    config_path = Path(args.config)

    if args.list_ports:
        print_ports()
        return

    if args.list_ports_json:
        print_ports_json(args.ports_kind)
        return

    if args.show_config:
        show_saved_config(config_path)
        return

    if args.set_config:
        update_saved_config(args, config_path)
        return

    if not 0 <= args.channel <= 15:
        raise RuntimeError("--channel должен быть в диапазоне 0..15")

    config = load_port_config(config_path)
    input_names = list(mido.get_input_names())
    input_name = resolve_port(
        args.input_port,
        config.get("input_port"),
        input_names,
        "входной",
    )

    output_name: Optional[str] = None
    if args.engine == "midi-out":
        output_names = list(mido.get_output_names())
        output_name = resolve_port(
            args.output_port,
            config.get("output_port"),
            output_names,
            "выходной",
        )

    if args.save_ports:
        save_port_config(
            config_path,
            input_name,
            output_name if args.engine == "midi-out" else config.get("output_port"),
        )
        print(f"Выбранные порты сохранены в {config_path}")

    engine = build_engine(args, output_name)

    print(f"Вход: {input_name}")
    if output_name:
        print(f"Выход: {output_name}")
    print(
        "Рекомендуемая аудиоконфигурация: ASIO или WASAPI exclusive, "
        "буфер 64-128 сэмплов, частота 48000 Гц."
    )
    print(
        f"Целевые параметры: buffer={args.buffer} сэмплов, "
        f"latency<={args.latency_target_ms:.1f} мс."
    )
    print("Прослушивание MIDI... Нажмите Ctrl+C для остановки.")

    try:
        with mido.open_input(input_name) as midi_in:
            while True:
                handled_any = False
                for msg in midi_in.iter_pending():
                    handled_any = True
                    if args.verbose:
                        print(msg)
                    handle_message(msg, engine, args.channel)
                if not handled_any:
                    time.sleep(0.001)
    finally:
        engine.close()


if __name__ == "__main__":
    try:
        run(parse_args())
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    except Exception as exc:
        print(f"Ошибка: {exc}")
        raise SystemExit(1)