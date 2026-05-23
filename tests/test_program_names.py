import sys
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO


# Avoid dependency on real MIDI packages/devices during test import.
if "mido" not in sys.modules:
    sys.modules["mido"] = types.SimpleNamespace(Message=object)

import main


class ProgramNameFormattingTests(unittest.TestCase):
    def test_gm_program_name_hit(self) -> None:
        self.assertEqual(main.gm_program_name(48), "String Ensemble 1")

    def test_format_program_with_name_uses_reference_marker(self) -> None:
        self.assertEqual(
            main.format_program_with_name(48, bank=0),
            "48 (String Ensemble 1 [GM reference])",
        )

    def test_non_gm_bank_still_uses_gm_reference_fallback(self) -> None:
        self.assertEqual(
            main.format_program_with_name(16, bank=8192),
            "16 (Drawbar Organ [GM reference])",
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
                "Избранные программы (8):\n"
                "  1. 127 (Gunshot [GM reference])\n"
                "  2. 9 (Glockenspiel [GM reference])\n"
                "  3. 19 (Church Organ [GM reference])\n"
                "  4. 123 (Bird Tweet [GM reference])\n"
                "  5. 114 (Steel Drums [GM reference])\n"
                "  6. 0 (Acoustic Grand Piano [GM reference])\n"
                "  7. 5 (Electric Piano 2 [GM reference])\n"
                "  8. 13 (Xylophone [GM reference])\n"
            ),
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
            "program=6->7 (Clavi [GM reference])",
            rendered,
        )
        self.assertNotIn("Harpsichord", rendered)

    def test_format_favorite_selected_message_includes_full_name(self) -> None:
        self.assertEqual(
            main.format_favorite_selected_message(9, selected_index=2, total_favorites=8),
            "[favorites] выбрана программа 9 (Glockenspiel [GM reference]) (2/8)",
        )


if __name__ == "__main__":
    unittest.main()
