---
name: Console Color Formatting
overview: Добавить ANSI-подсветку для названий инструментов, заголовков и горячих клавиш, а также обновить стартовый информационный блок с версией из переменной и исправленным текстом.
todos:
  - id: console-colors
    content: Добавить ANSI-константы, helper-форматирование и переменную версии в main.py
    status: completed
  - id: instrument-highlighting
    content: Сделать зелёную подсветку названий инструментов в instrument/favorites выводах
    status: completed
  - id: headers-hotkeys-colors
    content: Сделать жёлтые заголовки и синие горячие клавиши в help/favorites/startup тексте
    status: completed
  - id: startup-banner
    content: "Обновить стартовый блок: **версия из переменной**, исправленный текст hotkeys без [[ ]]"
    status: completed
  - id: tests-update
    content: Обновить tests/test_program_names.py под ANSI-вывод и добавить недостающие проверки
    status: completed
isProject: false
---

# План внедрения подсветки и стартового блока

- Изменить форматирование консольного вывода в [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py):
  - Ввести константы ANSI-цветов и helper-функцию для безопасной обертки текста (`green`, `yellow`, `blue`, `reset`).
  - Добавить переменную версии приложения (например, `APP_VERSION = "1.03 (23.05.2026)"`) и использовать ее при печати стартового заголовка.
- Подсветить названия инструментов зелёным в строках, где печатается `format_program_with_name(...)`:
  - Логи `[instrument] ... program=...` (в `ProgramController.set_program` и `log_instrument_observability`).
  - Списки/сообщения избранного (`print_favorites`, `format_favorite_selected_message`).
  - Подсветка должна затрагивать только имя инструмента (например, `Marimba`, `Tubular Bells`, `Dulcimer`), а не весь фрагмент с номером программы.
- Подсветить заголовки жёлтым и комбинации клавиш синим:
  - `Избранные программы` в `print_favorites`.
  - `Быстрые клавиши` в `print_hotkeys`.
  - Сами сочетания (`+/=`, `-/`_, `*`, `PgUp/PgDown`, `p/P`, `h/H`, `Ctrl+C`) — синим в выводе help и стартовой строке `Горячие клавиши: ...`.
- Обновить стартовый блок запуска в `run(...)`:
  - Печатать заголовок в формате `MIDI синтезатор, версия <из переменной>`.
  - Исправить строку про hotkeys: Применить синюю подсветку для перечисленных hotkeys, включая `Ctrl+C` в строке `Прослушивание MIDI...`.
- Обновить и дополнить тесты в [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_program_names.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_program_names.py):
  - Адаптировать ожидаемые строки под ANSI-последовательности.
  - Проверить, что зелёная подсветка применяется к названию инструмента, жёлтая — к заголовкам, синяя — к горячим клавишам.
- Верификация после внедрения:
  - Запустить `run_tests.bat` (или точечно `tests/test_program_names.py`) и убедиться, что формат новых строк стабилен.
  - Ручная проверка реального консольного вывода при старте и переключении программ клавишами `+/=`/`-/`_ и `PgUp/PgDown`.

