import sys
import types
import unittest


# Убираем зависимость от реальных MIDI-пакетов и устройств при импорте тестов.
if "mido" not in sys.modules:
    sys.modules["mido"] = types.SimpleNamespace(Message=object)

import main


class FavoritesLogicTests(unittest.TestCase):
    def test_toggle_add_appends_to_end(self) -> None:
        favorites = [1, 23, 12, 125]
        added, cursor = main.toggle_favorite(favorites, 7, None)

        self.assertTrue(added)
        self.assertIsNone(cursor)
        self.assertEqual(favorites, [1, 23, 12, 125, 7])

    def test_toggle_remove_keeps_order(self) -> None:
        favorites = [1, 23, 12, 125, 7]
        added, cursor = main.toggle_favorite(favorites, 12, None)

        self.assertFalse(added)
        self.assertIsNone(cursor)
        self.assertEqual(favorites, [1, 23, 125, 7])

    def test_toggle_remove_adjusts_cursor_when_needed(self) -> None:
        favorites = [1, 23, 12, 125]
        # Курсор указывает на 12 (индекс 2); удаляем 23 (индекс 1) и сдвигаем курсор на 1.
        added, cursor = main.toggle_favorite(favorites, 23, 2)

        self.assertFalse(added)
        self.assertEqual(cursor, 1)
        self.assertEqual(favorites, [1, 12, 125])

    def test_favorite_prev_matches_pgdown_examples(self) -> None:
        favorites = [1, 23, 12, 125]

        program, index = main.favorite_prev(favorites, current_program=12, last_favorite_index=2)
        self.assertEqual(program, 23)
        self.assertEqual(index, 1)

        program, index = main.favorite_prev(favorites, current_program=1, last_favorite_index=0)
        self.assertEqual(program, 125)
        self.assertEqual(index, 3)

    def test_favorite_next_cycles_forward_in_list_order(self) -> None:
        favorites = [1, 23, 12, 125]

        program, index = main.favorite_next(favorites, current_program=125, last_favorite_index=3)
        self.assertEqual(program, 1)
        self.assertEqual(index, 0)

    def test_navigation_uses_current_program_when_cursor_missing(self) -> None:
        favorites = [1, 23, 12, 125]

        program, index = main.favorite_prev(
            favorites, current_program=12, last_favorite_index=None
        )
        self.assertEqual(program, 23)
        self.assertEqual(index, 1)

        program, index = main.favorite_next(
            favorites, current_program=12, last_favorite_index=None
        )
        self.assertEqual(program, 125)
        self.assertEqual(index, 3)

    def test_navigation_fallback_when_current_not_in_favorites(self) -> None:
        favorites = [1, 23, 12, 125]

        program, index = main.favorite_next(
            favorites, current_program=7, last_favorite_index=None
        )
        self.assertEqual(program, 1)
        self.assertEqual(index, 0)

        program, index = main.favorite_prev(
            favorites, current_program=7, last_favorite_index=None
        )
        self.assertEqual(program, 125)
        self.assertEqual(index, 3)


if __name__ == "__main__":
    unittest.main()
