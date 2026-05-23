import sys
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO


# Убираем зависимость от реальных MIDI-пакетов и устройств при импорте тестов.
if "mido" not in sys.modules:
    sys.modules["mido"] = types.SimpleNamespace(Message=object)

import main


class ProgramNameFormattingTests(unittest.TestCase):
    def _poll_actions_from_keys(self, keys: list[str]) -> list[main.KeyboardAction]:
        class StubMsvcrt:
            def __init__(self, source_keys: list[str]) -> None:
                self._keys = list(source_keys)

            def kbhit(self) -> bool:
                return bool(self._keys)

            def getwch(self) -> str:
                return self._keys.pop(0)

        original_msvcrt = main.msvcrt
        main.msvcrt = StubMsvcrt(keys)
        try:
            return main.poll_keyboard_actions()
        finally:
            main.msvcrt = original_msvcrt

    def test_gm_program_name_hit(self) -> None:
        self.assertEqual(main.gm_program_name(48), "String Ensemble 1")

    def test_format_program_with_name_uses_reference_marker(self) -> None:
        self.assertEqual(
            main.format_program_with_name(48, bank=0),
            (
                f"48 ({main.ANSI_GREEN}String Ensemble 1{main.ANSI_RESET} "
                "[GM reference])"
            ),
        )

    def test_non_gm_bank_still_uses_gm_reference_fallback(self) -> None:
        self.assertEqual(
            main.format_program_with_name(16, bank=8192),
            f"16 ({main.ANSI_GREEN}Drawbar Organ{main.ANSI_RESET} [GM reference])",
        )

    def test_out_of_range_program_formats_as_unknown(self) -> None:
        self.assertEqual(main.format_program_with_name(130, bank=0), "130 (unknown)")

    def test_print_favorites_renders_numbered_list_with_names(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            main.print_favorites([127, 9, 19, 123, 114, 0, 5, 13])

        self.assertEqual(
            output.getvalue(),
            (
                f"{main.ANSI_YELLOW}Избранные инструменты{main.ANSI_RESET} (8):\n"
                f"  1. {main.ANSI_BLUE}F1{main.ANSI_RESET} - "
                f"127 ({main.ANSI_GREEN}Gunshot{main.ANSI_RESET} [GM reference])\n"
                f"  2. {main.ANSI_BLUE}F2{main.ANSI_RESET} - "
                f"9 ({main.ANSI_GREEN}Glockenspiel{main.ANSI_RESET} [GM reference])\n"
                f"  3. {main.ANSI_BLUE}F3{main.ANSI_RESET} - "
                f"19 ({main.ANSI_GREEN}Church Organ{main.ANSI_RESET} [GM reference])\n"
                f"  4. {main.ANSI_BLUE}F4{main.ANSI_RESET} - "
                f"123 ({main.ANSI_GREEN}Bird Tweet{main.ANSI_RESET} [GM reference])\n"
                f"  5. {main.ANSI_BLUE}F5{main.ANSI_RESET} - "
                f"114 ({main.ANSI_GREEN}Steel Drums{main.ANSI_RESET} [GM reference])\n"
                f"  6. {main.ANSI_BLUE}F6{main.ANSI_RESET} - "
                f"0 ({main.ANSI_GREEN}Acoustic Grand Piano{main.ANSI_RESET} [GM reference])\n"
                f"  7. {main.ANSI_BLUE}F7{main.ANSI_RESET} - "
                f"5 ({main.ANSI_GREEN}Electric Piano 2{main.ANSI_RESET} [GM reference])\n"
                f"  8. {main.ANSI_BLUE}F8{main.ANSI_RESET} - "
                f"13 ({main.ANSI_GREEN}Xylophone{main.ANSI_RESET} [GM reference])\n"
                "\n"
                f"  {main.ANSI_BLUE}*{main.ANSI_RESET}       : "
                "Добавить/удалить текущую программу в избранном\n"
                f"  {main.ANSI_BLUE}PgUp{main.ANSI_RESET}    : "
                "Следующая избранная программа (по списку)\n"
                f"  {main.ANSI_BLUE}PgDown{main.ANSI_RESET}  : "
                "Предыдущая избранная программа (по списку)\n"
            ),
        )

    def test_print_favorites_uses_shift_hotkeys_and_omits_hotkeys_after_twenty(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            main.print_favorites([111] * 22)

        rendered = output.getvalue()
        rendered_program = main.format_program_with_name(111, bank=0)
        self.assertIn(
            f"  19. {main.ANSI_BLUE}Shift-F9{main.ANSI_RESET} - "
            f"{rendered_program}\n",
            rendered,
        )
        self.assertIn(
            f"  20. {main.ANSI_BLUE}Shift-F10{main.ANSI_RESET} - "
            f"{rendered_program}\n",
            rendered,
        )
        self.assertIn(
            f"  21. {rendered_program}\n",
            rendered,
        )
        self.assertIn(
            f"  22. {rendered_program}\n",
            rendered,
        )

    def test_set_program_log_shows_name_only_for_new_program(self) -> None:
        class StubEngine(main.AudioEngine):
            def note_on(self, note: int, velocity: int, channel: int) -> None:
                return None

            def note_off(self, note: int, velocity: int, channel: int) -> None:
                return None

            def control_change(self, control: int, value: int, channel: int) -> None:
                return None

            def pitch_bend(self, pitch: int, channel: int) -> None:
                return None

            def program_change(self, program: int, channel: int) -> None:
                return None

        state = main.build_channel_instrument_state()
        state[10]["program"] = 6
        controller = main.ProgramController(StubEngine(), state, default_channel=10)

        output = StringIO()
        with redirect_stdout(output):
            controller.set_program(7, source="keyboard", channel=10)

        rendered = output.getvalue()
        self.assertIn(
            (
                "program=6->7 "
                f"({main.ANSI_GREEN}Clavi{main.ANSI_RESET} [GM reference])"
            ),
            rendered,
        )
        self.assertNotIn("Harpsichord", rendered)

    def test_format_favorite_selected_message_includes_full_name(self) -> None:
        self.assertEqual(
            main.format_favorite_selected_message(9, selected_index=2, total_favorites=8),
            (
                "[favorites] выбрана программа 9 "
                f"({main.ANSI_GREEN}Glockenspiel{main.ANSI_RESET} [GM reference]) (2/8)"
            ),
        )

    def test_format_ready_instrument_message_includes_program_name(self) -> None:
        self.assertEqual(
            main.format_ready_instrument_message(channel=0, program=5, bank=0),
            (
                "Готов к игре: ch=1 "
                f"program=5 ({main.ANSI_GREEN}Electric Piano 2{main.ANSI_RESET} "
                "[GM reference]) bank=0"
            ),
        )

    def test_print_hotkeys_uses_colored_header_and_shortcuts(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            main.print_hotkeys()

        rendered = output.getvalue()
        self.assertIn(
            f"{main.ANSI_YELLOW}Быстрые клавиши:{main.ANSI_RESET}",
            rendered,
        )
        self.assertIn(f"{main.ANSI_BLUE}+ или ={main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}- или _{main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}F1..F10{main.ANSI_RESET}", rendered)
        self.assertIn(
            f"{main.ANSI_BLUE}Shift+F1..Shift+F10{main.ANSI_RESET}",
            rendered,
        )
        self.assertIn(f"{main.ANSI_BLUE}PgUp{main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}PgDown{main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}p/P{main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}h/H{main.ANSI_RESET}", rendered)
        self.assertIn(f"{main.ANSI_BLUE}Ctrl+C{main.ANSI_RESET}", rendered)

    def test_poll_keyboard_actions_maps_f_keys_to_favorite_indexes(self) -> None:
        actions = self._poll_actions_from_keys(
            ["\x00", ";", "\x00", "D", "\x00", "T", "\x00", "]"]
        )
        self.assertEqual(
            [(action.kind, action.favorite_index) for action in actions],
            [
                ("favorite_select_index", 1),
                ("favorite_select_index", 10),
                ("favorite_select_index", 11),
                ("favorite_select_index", 20),
            ],
        )

    def test_poll_keyboard_actions_supports_alternative_f_key_codes(self) -> None:
        actions = self._poll_actions_from_keys(["\x00", "K", "\x00", "G"])
        self.assertEqual(
            [(action.kind, action.favorite_index) for action in actions],
            [("favorite_select_index", 1), ("favorite_select_index", 10)],
        )

    def test_format_missing_favorite_message_includes_requested_position(self) -> None:
        self.assertEqual(
            main.format_missing_favorite_message(12),
            "Нет избранной программы №12, добавьте в избранные через *",
        )

    def test_resolve_port_warning_prefix_is_red(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            resolved = main.resolve_port(
                cli_value=None,
                config_value="LKMK3 MIDI 0",
                available_ports=["DJM-450 0"],
                label="входной",
            )

        self.assertEqual(resolved, "DJM-450 0")
        self.assertEqual(
            output.getvalue(),
            (
                f"{main.ANSI_RED}Предупреждение:{main.ANSI_RESET} "
                "сохраненный порт (входной) 'LKMK3 MIDI 0' недоступен. "
                "Используется резервный вариант 'DJM-450 0'.\n"
            ),
        )

    def test_initialize_channel_defaults_applies_to_all_channels(self) -> None:
        state = main.build_channel_instrument_state()
        main.initialize_channel_defaults(state, bank=257, program=130)

        for channel in range(16):
            self.assertEqual(state[channel]["bank_msb"], 2)
            self.assertEqual(state[channel]["bank_lsb"], 1)
            self.assertEqual(state[channel]["program"], 2)


if __name__ == "__main__":
    unittest.main()
