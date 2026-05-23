import sys
import types
import unittest


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


if __name__ == "__main__":
    unittest.main()
