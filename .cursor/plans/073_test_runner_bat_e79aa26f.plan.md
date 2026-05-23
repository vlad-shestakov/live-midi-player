---
name: test runner bat
overview: Добавить батник в стиле существующего `start_MIDI.bat` для запуска автотестов через `unittest` в активированном виртуальном окружении.
todos:
  - id: draft-bat-structure
    content: "Скопировать структуру start_MIDI.bat: cd, .venv check, activation, validation"
    status: completed
  - id: wire-test-command
    content: Подставить запуск unittest discover и обработку кода возврата
    status: completed
  - id: verify-runner
    content: Проверить запуск run_tests.bat и ожидаемый вывод тестов
    status: completed
isProject: false
---

# План: bat для запуска тестов

## Что сделаем
- Добавим новый файл [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/run_tests.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/run_tests.bat) по структуре, близкой к [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/start_MIDI.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/start_MIDI.bat).
- Сохраним ту же логику подготовки среды: переход в директорию скрипта, проверка `.venv`, активация окружения, валидация активации.
- Вместо запуска `main.py` выполним команду тестов для текущего набора: `python -m unittest discover -s tests -p "test_*.py"`.

## Детали батника
- Сообщения об ошибках и `exit /b 1`, если `.venv` не найдено или не активировалось.
- Явный вывод о старте тестов и итоговый код возврата.
- По завершении добавить `pause`, чтобы окно не закрывалось сразу при запуске двойным кликом.

## Проверка
- Запуск `run_tests.bat` из проводника/терминала.
- Ожидаемо: отображается прогон тестов из [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_favorites_logic.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_favorites_logic.py), затем `OK` и успешный код выхода.
- При сломанном/отсутствующем `.venv` — понятное сообщение и корректный неуспешный код.