from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import time
from pathlib import Path
from typing import Iterable, Literal, Optional

import mido

try:
    import msvcrt
except ImportError:
    msvcrt = None

APP_VERSION = "1.04 (23.05.2026)"

CONFIG_FILENAME = "midi_ports.json"
FAVORITES_FILENAME = "midi_favorites.json"
PROGRAM_RANGE = 128
GM_REFERENCE_TAG = "[GM reference]"
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_BLUE = "\033[96m"
ANSI_RED = "\033[31m"
GM_PROGRAM_NAMES: tuple[str, ...] = (
    "Acoustic Grand Piano",
    "Bright Acoustic Piano",
    "Electric Grand Piano",
    "Honky-tonk Piano",
    "Electric Piano 1",
    "Electric Piano 2",
    "Harpsichord",
    "Clavi",
    "Celesta",
    "Glockenspiel",
    "Music Box",
    "Vibraphone",
    "Marimba",
    "Xylophone",
    "Tubular Bells",
    "Dulcimer",
    "Drawbar Organ",
    "Percussive Organ",
    "Rock Organ",
    "Church Organ",
    "Reed Organ",
    "Accordion",
    "Harmonica",
    "Tango Accordion",
    "Acoustic Guitar (nylon)",
    "Acoustic Guitar (steel)",
    "Electric Guitar (jazz)",
    "Electric Guitar (clean)",
    "Electric Guitar (muted)",
    "Overdriven Guitar",
    "Distortion Guitar",
    "Guitar harmonics",
    "Acoustic Bass",
    "Electric Bass (finger)",
    "Electric Bass (pick)",
    "Fretless Bass",
    "Slap Bass 1",
    "Slap Bass 2",
    "Synth Bass 1",
    "Synth Bass 2",
    "Violin",
    "Viola",
    "Cello",
    "Contrabass",
    "Tremolo Strings",
    "Pizzicato Strings",
    "Orchestral Harp",
    "Timpani",
    "String Ensemble 1",
    "String Ensemble 2",
    "SynthStrings 1",
    "SynthStrings 2",
    "Choir Aahs",
    "Voice Oohs",
    "Synth Voice",
    "Orchestra Hit",
    "Trumpet",
    "Trombone",
    "Tuba",
    "Muted Trumpet",
    "French Horn",
    "Brass Section",
    "SynthBrass 1",
    "SynthBrass 2",
    "Soprano Sax",
    "Alto Sax",
    "Tenor Sax",
    "Baritone Sax",
    "Oboe",
    "English Horn",
    "Bassoon",
    "Clarinet",
    "Piccolo",
    "Flute",
    "Recorder",
    "Pan Flute",
    "Blown Bottle",
    "Shakuhachi",
    "Whistle",
    "Ocarina",
    "Lead 1 (square)",
    "Lead 2 (sawtooth)",
    "Lead 3 (calliope)",
    "Lead 4 (chiff)",
    "Lead 5 (charang)",
    "Lead 6 (voice)",
    "Lead 7 (fifths)",
    "Lead 8 (bass + lead)",
    "Pad 1 (new age)",
    "Pad 2 (warm)",
    "Pad 3 (polysynth)",
    "Pad 4 (choir)",
    "Pad 5 (bowed)",
    "Pad 6 (metallic)",
    "Pad 7 (halo)",
    "Pad 8 (sweep)",
    "FX 1 (rain)",
    "FX 2 (soundtrack)",
    "FX 3 (crystal)",
    "FX 4 (atmosphere)",
    "FX 5 (brightness)",
    "FX 6 (goblins)",
    "FX 7 (echoes)",
    "FX 8 (sci-fi)",
    "Sitar",
    "Banjo",
    "Shamisen",
    "Koto",
    "Kalimba",
    "Bag pipe",
    "Fiddle",
    "Shanai",
    "Tinkle Bell",
    "Agogo",
    "Steel Drums",
    "Woodblock",
    "Taiko Drum",
    "Melodic Tom",
    "Synth Drum",
    "Reverse Cymbal",
    "Guitar Fret Noise",
    "Breath Noise",
    "Seashore",
    "Bird Tweet",
    "Telephone Ring",
    "Helicopter",
    "Applause",
    "Gunshot",
)

def wrap_program(program: int) -> int:
    return program % PROGRAM_RANGE


def gm_program_name(program: int) -> Optional[str]:
    if 0 <= program < PROGRAM_RANGE:
        return GM_PROGRAM_NAMES[program]
    return None


def resolve_instrument_name(program: int, bank: int) -> tuple[str, bool]:
    del bank
    name = gm_program_name(program)
    if name is None:
        return "unknown", False
    return name, True


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{ANSI_RESET}"


def format_program_with_name(program: int, bank: int) -> str:
    name, is_reference = resolve_instrument_name(program, bank)
    rendered_name = colorize(name, ANSI_GREEN) if is_reference else name
    if is_reference:
        return f"{program} ({rendered_name} {GM_REFERENCE_TAG})"
    return f"{program} ({rendered_name})"


@dataclass(frozen=True)
class KeyboardAction:
    kind: Literal[
        "program_step",
        "favorite_toggle",
        "favorite_prev",
        "favorite_next",
        "print_favorites",
        "print_help",
    ]
    step: int = 0


class ProgramController:
    def __init__(
        self,
        engine: "AudioEngine",
        state: dict[int, dict[str, Optional[int]]],
        default_channel: int,
    ):
        self._engine = engine
        self._state = state
        self._default_channel = default_channel
        self.last_active_channel = default_channel

    def _ensure_channel_state(self, channel: int) -> dict[str, Optional[int]]:
        return self._state.setdefault(
            channel,
            {"bank_msb": 0, "bank_lsb": 0, "program": None},
        )

    def _current_program(self, channel_state: dict[str, Optional[int]]) -> int:
        program = channel_state.get("program")
        if isinstance(program, int):
            return wrap_program(program)
        return 0

    def current_program(self, channel: Optional[int] = None) -> int:
        target_channel = self.last_active_channel if channel is None else channel
        channel_state = self._ensure_channel_state(target_channel)
        return self._current_program(channel_state)

    def sync_from_message(self, msg: mido.Message) -> None:
        channel = getattr(msg, "channel", self._default_channel)
        channel_state = self._ensure_channel_state(channel)

        if hasattr(msg, "channel"):
            self.last_active_channel = channel

        if msg.type == "control_change":
            if msg.control == 0:
                channel_state["bank_msb"] = msg.value
            elif msg.control == 32:
                channel_state["bank_lsb"] = msg.value
            return

        if msg.type == "program_change":
            channel_state["program"] = wrap_program(msg.program)

    def change_program(self, step: int, source: str, channel: Optional[int] = None) -> None:
        target_channel = self.last_active_channel if channel is None else channel
        old_program = self.current_program(target_channel)
        self.set_program(old_program + step, source=source, channel=target_channel)

    def set_program(self, program: int, source: str, channel: Optional[int] = None) -> None:
        target_channel = self.last_active_channel if channel is None else channel
        channel_state = self._ensure_channel_state(target_channel)
        old_program = self._current_program(channel_state)
        new_program = wrap_program(program)
        bank = current_bank_value(channel_state)
        channel_state["program"] = new_program
        bank_msb = channel_state.get("bank_msb") or 0
        bank_lsb = channel_state.get("bank_lsb") or 0
        self._engine.control_change(123, 0, target_channel)  # all notes off
        self._engine.control_change(121, 0, target_channel)  # reset controllers
        self._engine.control_change(0, bank_msb, target_channel)
        self._engine.control_change(32, bank_lsb, target_channel)
        self._engine.program_change(new_program, target_channel)
        print(
            f"[instrument] source={source} ch={target_channel + 1} "
            f"program={old_program}->{format_program_with_name(new_program, bank)} "
            f"bank={bank} "
            f"(cc0={channel_state['bank_msb']}, cc32={channel_state['bank_lsb']})"
        )


def poll_keyboard_actions() -> list[KeyboardAction]:
    if msvcrt is None:
        return []

    actions: list[KeyboardAction] = []
    while msvcrt.kbhit():
        key = msvcrt.getwch()
        if key in ("\x00", "\xe0"):
            extended_key = msvcrt.getwch()
            if extended_key == "I":
                actions.append(KeyboardAction(kind="favorite_next"))
            elif extended_key == "Q":
                actions.append(KeyboardAction(kind="favorite_prev"))
            continue
        if key in ("+", "="):
            actions.append(KeyboardAction(kind="program_step", step=1))
        elif key in ("-", "_"):
            actions.append(KeyboardAction(kind="program_step", step=-1))
        elif key == "*":
            actions.append(KeyboardAction(kind="favorite_toggle"))
        elif key in ("p", "P", "з", "З"):
            actions.append(KeyboardAction(kind="print_favorites"))
        elif key in ("h", "H", "р", "Р"):
            actions.append(KeyboardAction(kind="print_help"))
    if actions:
        has_plain_action = any(
            action.kind
            in ("program_step", "favorite_toggle", "print_favorites", "print_help")
            for action in actions
        )
        has_favorite_nav = any(
            action.kind in ("favorite_prev", "favorite_next") for action in actions
        )
        if has_plain_action and has_favorite_nav:
            actions = [
                action
                for action in actions
                if action.kind not in ("favorite_prev", "favorite_next")
            ]
    return actions


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


def default_favorites_path() -> Path:
    return Path(__file__).resolve().parent / FAVORITES_FILENAME


def _normalize_favorites(programs: Iterable[object]) -> list[int]:
    normalized: list[int] = []
    for value in programs:
        if not isinstance(value, int) or not 0 <= value < PROGRAM_RANGE:
            continue
        if value not in normalized:
            normalized.append(value)
    return normalized


def load_favorites(favorites_path: Path) -> list[int]:
    if not favorites_path.exists():
        return []

    try:
        with favorites_path.open("r", encoding="utf-8") as favorites_file:
            raw = json.load(favorites_file)
    except json.JSONDecodeError:
        print(
            f"{colorize('Предупреждение:', ANSI_RED)} "
            f"некорректный JSON избранных ({favorites_path}). "
            "Используется пустой список."
        )
        return []

    if not isinstance(raw, dict):
        print(
            f"{colorize('Предупреждение:', ANSI_RED)} "
            f"формат избранных ({favorites_path}) не распознан. "
            "Используется пустой список."
        )
        return []

    programs = raw.get("programs")
    if not isinstance(programs, list):
        print(
            f"{colorize('Предупреждение:', ANSI_RED)} "
            f"в избранных ({favorites_path}) нет списка 'programs'. "
            "Используется пустой список."
        )
        return []

    return _normalize_favorites(programs)


def save_favorites(favorites_path: Path, programs: Iterable[int]) -> None:
    payload = {"schema_version": 1, "programs": _normalize_favorites(programs)}
    with favorites_path.open("w", encoding="utf-8") as favorites_file:
        json.dump(payload, favorites_file, ensure_ascii=False, indent=2)
        favorites_file.write("\n")


def toggle_favorite(
    favorites: list[int], program: int, last_favorite_index: Optional[int]
) -> tuple[bool, Optional[int]]:
    if program in favorites:
        removed_index = favorites.index(program)
        favorites.pop(removed_index)
        if last_favorite_index is None:
            return False, None
        if last_favorite_index == removed_index:
            return False, None
        if last_favorite_index > removed_index:
            return False, last_favorite_index - 1
        return False, last_favorite_index

    favorites.append(program)
    return True, last_favorite_index


def _favorite_target_index(
    favorites: list[int],
    current_program: int,
    last_favorite_index: Optional[int],
    direction: int,
) -> int:
    if not favorites:
        raise ValueError("favorites list is empty")

    if last_favorite_index is not None and 0 <= last_favorite_index < len(favorites):
        return (last_favorite_index + direction) % len(favorites)

    if current_program in favorites:
        base_index = favorites.index(current_program)
        return (base_index + direction) % len(favorites)

    return 0 if direction > 0 else len(favorites) - 1


def favorite_next(
    favorites: list[int], current_program: int, last_favorite_index: Optional[int]
) -> tuple[int, int]:
    index = _favorite_target_index(favorites, current_program, last_favorite_index, 1)
    return favorites[index], index


def favorite_prev(
    favorites: list[int], current_program: int, last_favorite_index: Optional[int]
) -> tuple[int, int]:
    index = _favorite_target_index(favorites, current_program, last_favorite_index, -1)
    return favorites[index], index


def print_favorites(programs: list[int]) -> None:
    favorites_title = colorize("Избранные программы", ANSI_YELLOW)
    if not programs:
        print(f"{favorites_title}: <пусто>")
        return
    print(f"{favorites_title} ({len(programs)}):")
    for index, program in enumerate(programs, start=1):
        print(f"  {index}. {format_program_with_name(program, bank=0)}")


def format_favorite_selected_message(
    program: int, selected_index: int, total_favorites: int
) -> str:
    return (
        f"[favorites] выбрана программа {format_program_with_name(program, bank=0)} "
        f"({selected_index}/{total_favorites})"
    )


def format_ready_instrument_message(channel: int, program: int, bank: int) -> str:
    return (
        f"Готов к игре: ch={channel + 1} "
        f"program={format_program_with_name(program, bank)} bank={bank}"
    )


def print_hotkeys() -> None:
    print(colorize("Быстрые клавиши:", ANSI_YELLOW))
    print(f"  {colorize('+ или =', ANSI_BLUE)} : Program +1")
    print(f"  {colorize('- или _', ANSI_BLUE)} : Program -1")
    print(
        f"  {colorize('*', ANSI_BLUE)}       : "
        "Добавить/удалить текущую программу в избранном"
    )
    print(
        f"  {colorize('PgUp', ANSI_BLUE)}    : "
        "Следующая избранная программа (по списку)"
    )
    print(
        f"  {colorize('PgDown', ANSI_BLUE)}  : "
        "Предыдущая избранная программа (по списку)"
    )
    print(f"  {colorize('p/P', ANSI_BLUE)}     : Показать список избранных программ")
    print(f"  {colorize('h/H', ANSI_BLUE)}     : Показать список быстрых клавиш")
    print(f"  {colorize('Ctrl+C', ANSI_BLUE)}  : Остановить программу")


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
            f"{colorize('Предупреждение:', ANSI_RED)} "
            f"сохраненный порт ({label}) '{config_value}' недоступен. "
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
        "--favorites",
        default=str(default_favorites_path()),
        help="Путь к JSON-файлу избранных программ.",
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
        "--program-up-cc",
        type=int,
        default=None,
        help="CC (0-127), который переключает program на +1 для текущего канала.",
    )
    parser.add_argument(
        "--program-down-cc",
        type=int,
        default=None,
        help="CC (0-127), который переключает program на -1 для текущего канала.",
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
    # Keep output channel stable regardless of incoming controller channel.
    channel = default_channel

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


def midi_program_step_from_trigger(
    msg: mido.Message,
    up_cc: Optional[int],
    down_cc: Optional[int],
) -> int:
    if msg.type != "control_change" or msg.value == 0:
        return 0

    if up_cc is not None and msg.control == up_cc:
        return 1
    if down_cc is not None and msg.control == down_cc:
        return -1
    return 0


def build_channel_instrument_state() -> dict[int, dict[str, Optional[int]]]:
    return {
        channel: {"bank_msb": 0, "bank_lsb": 0, "program": None}
        for channel in range(16)
    }


def initialize_channel_defaults(
    state: dict[int, dict[str, Optional[int]]],
    bank: int,
    program: int,
) -> None:
    bank_msb = (bank >> 7) & 0x7F
    bank_lsb = bank & 0x7F
    initial_program = wrap_program(program)
    for channel_state in state.values():
        channel_state["bank_msb"] = bank_msb
        channel_state["bank_lsb"] = bank_lsb
        channel_state["program"] = initial_program


def current_bank_value(channel_state: dict[str, Optional[int]]) -> int:
    bank_msb = channel_state.get("bank_msb") or 0
    bank_lsb = channel_state.get("bank_lsb") or 0
    return (bank_msb << 7) + bank_lsb


def log_instrument_observability(
    msg: mido.Message,
    default_channel: int,
    state: dict[int, dict[str, Optional[int]]],
) -> None:
    channel = getattr(msg, "channel", default_channel)
    channel_state = state.setdefault(
        channel,
        {"bank_msb": 0, "bank_lsb": 0, "program": None},
    )

    if msg.type == "control_change" and msg.control in (0, 32):
        if msg.control == 0:
            channel_state["bank_msb"] = msg.value
            print(
                f"[instrument] ch={channel + 1} cc0(bank_msb)={msg.value} "
                f"bank={current_bank_value(channel_state)}"
            )
            return
        channel_state["bank_lsb"] = msg.value
        print(
            f"[instrument] ch={channel + 1} cc32(bank_lsb)={msg.value} "
            f"bank={current_bank_value(channel_state)}"
        )
        return

    if msg.type == "program_change":
        channel_state["program"] = msg.program
        bank = current_bank_value(channel_state)
        print(
            f"[instrument] ch={channel + 1} "
            f"program={format_program_with_name(msg.program, bank)} "
            f"bank={bank} "
            f"(cc0={channel_state['bank_msb']}, cc32={channel_state['bank_lsb']})"
        )
        return

    if msg.type == "note_on" and msg.velocity > 0:
        # Reflect actual synth output channel (same routing as handle_message).
        observed_channel = default_channel
        observed_state = state.setdefault(
            observed_channel,
            {"bank_msb": 0, "bank_lsb": 0, "program": None},
        )
        current_program = observed_state["program"]
        if isinstance(current_program, int):
            program_repr = format_program_with_name(current_program, current_bank_value(observed_state))
        else:
            program_repr = f"{current_program} (unknown)"
        print(
            f"[play] ch={observed_channel + 1} note={msg.note} vel={msg.velocity} "
            f"program={program_repr} bank={current_bank_value(observed_state)}"
        )


def run(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    favorites_path = Path(args.favorites)

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
    if args.program_up_cc is not None and not 0 <= args.program_up_cc <= 127:
        raise RuntimeError("--program-up-cc должен быть в диапазоне 0..127")
    if args.program_down_cc is not None and not 0 <= args.program_down_cc <= 127:
        raise RuntimeError("--program-down-cc должен быть в диапазоне 0..127")
    if (
        args.program_up_cc is not None
        and args.program_down_cc is not None
        and args.program_up_cc == args.program_down_cc
    ):
        raise RuntimeError("--program-up-cc и --program-down-cc не должны совпадать")

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

    print(f"{colorize('MIDI синтезатор', ANSI_YELLOW)}, версия {APP_VERSION}")
    engine = build_engine(args, output_name)
    favorites = load_favorites(favorites_path)
    last_favorite_index: Optional[int] = None
    channel_state = build_channel_instrument_state()
    initialize_channel_defaults(channel_state, args.bank, args.program)
    program_controller = ProgramController(engine, channel_state, args.channel)

    print(f"Вход: {input_name}")
    if output_name:
        print(f"Выход: {output_name}")
    if args.program_up_cc is not None or args.program_down_cc is not None:
        print(
            "MIDI-триггеры program: "
            f"up_cc={args.program_up_cc if args.program_up_cc is not None else '-'} "
            f"down_cc={args.program_down_cc if args.program_down_cc is not None else '-'}"
        )
    print(
        "Рекомендуемая аудиоконфигурация: ASIO или WASAPI exclusive, "
        "буфер 64-128 сэмплов, частота 48000 Гц."
    )
    print(
        f"Целевые параметры: buffer={args.buffer} сэмплов, "
        f"latency<={args.latency_target_ms:.1f} мс."
    )
    print(
        f"Горячие клавиши: {colorize('+/=', ANSI_BLUE)} Program +1, "
        f"{colorize('-/_', ANSI_BLUE)} Program -1, "
        f"{colorize('*', ANSI_BLUE)} toggle избранного, "
        f"{colorize('PgUp/PgDown', ANSI_BLUE)} выбор по избранным, "
        f"{colorize('p/P', ANSI_BLUE)} список избранных, "
        f"{colorize('h/H', ANSI_BLUE)} помощь."
    )
    print(
        format_ready_instrument_message(
            args.channel,
            wrap_program(args.program),
            args.bank,
        )
    )
    print(f"Файл избранных: {favorites_path} (загружено: {len(favorites)})")
    print(f"Прослушивание MIDI... Нажмите {colorize('Ctrl+C', ANSI_BLUE)} для остановки.")

    try:
        with mido.open_input(input_name) as midi_in:
            while True:
                handled_any = False
                for msg in midi_in.iter_pending():
                    handled_any = True
                    program_controller.sync_from_message(msg)
                    program_controller.last_active_channel = args.channel
                    if args.verbose:
                        if msg.type != "clock":
                            print(msg)
                        log_instrument_observability(msg, args.channel, channel_state)
                    step = midi_program_step_from_trigger(
                        msg,
                        args.program_up_cc,
                        args.program_down_cc,
                    )
                    if step != 0:
                        trigger_source = f"midi_cc{msg.control}"
                        msg_channel = getattr(msg, "channel", args.channel)
                        program_controller.change_program(
                            step,
                            source=trigger_source,
                            channel=msg_channel,
                        )
                        continue
                    handle_message(msg, engine, args.channel)
                keyboard_actions = poll_keyboard_actions()
                if keyboard_actions:
                    handled_any = True
                for action in keyboard_actions:
                    if action.kind == "program_step" and action.step != 0:
                        keyboard_channel = args.channel
                        program_controller.change_program(
                            action.step,
                            source="keyboard",
                            channel=keyboard_channel,
                        )
                        continue

                    if action.kind == "favorite_toggle":
                        keyboard_channel = args.channel
                        current_program = program_controller.current_program(
                            channel=keyboard_channel
                        )
                        added, last_favorite_index = toggle_favorite(
                            favorites,
                            current_program,
                            last_favorite_index,
                        )
                        save_favorites(favorites_path, favorites)
                        toggle_action = (
                            "добавлена в избранные"
                            if added
                            else "удалена из избранных"
                        )
                        print(
                            f"[favorites] program={format_program_with_name(current_program, bank=0)} "
                            f"{toggle_action}"
                        )
                        continue

                    if action.kind in ("favorite_prev", "favorite_next"):
                        if not favorites:
                            print("Нет избранных, добавьте в избранные через *")
                            continue
                        keyboard_channel = args.channel
                        current_program = program_controller.current_program(
                            channel=keyboard_channel
                        )
                        if action.kind == "favorite_prev":
                            favorite_program, last_favorite_index = favorite_prev(
                                favorites,
                                current_program,
                                last_favorite_index,
                            )
                            source = "favorite_prev"
                        else:
                            favorite_program, last_favorite_index = favorite_next(
                                favorites,
                                current_program,
                                last_favorite_index,
                            )
                            source = "favorite_next"
                        program_controller.set_program(
                            favorite_program,
                            source=source,
                            channel=keyboard_channel,
                        )
                        print(
                            format_favorite_selected_message(
                                favorite_program,
                                last_favorite_index + 1,
                                len(favorites),
                            )
                        )
                        continue

                    if action.kind == "print_favorites":
                        print_favorites(favorites)
                        continue

                    if action.kind == "print_help":
                        print_hotkeys()
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