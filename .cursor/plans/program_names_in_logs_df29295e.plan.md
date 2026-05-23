---
name: program names in logs
overview: Добавить отображение имени инструмента рядом с номером `program` в runtime-логах и при ручном переключении, с fallback на General MIDI и явной пометкой, когда имя справочное.
todos:
  - id: add-program-name-resolver
    content: Добавить helper/модуль резолва program->name с GM fallback и меткой reference
    status: completed
  - id: wire-logs
    content: Подключить форматирование имени в ProgramController.set_program и log_instrument_observability
    status: completed
  - id: tests-program-names
    content: Добавить unit-тесты на резолвер и формат строки program с fallback
    status: completed
  - id: verify-runtime-output
    content: Проверить вывод в verbose и убедиться в обратной совместимости логов
    status: completed
isProject: false
---

# План: названия инструментов по program

## Что меняем
- Ввести единый резолвер имени инструмента по `(bank, program)` в [main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py):
  - сначала пробуем точное имя из доступного каталога (если позже появится источник банка/саундфонта);
  - если точного имени нет, используем GM fallback для `bank=0, program=0..127`;
  - если имя взято из GM fallback, добавляем метку `"[GM reference]"`.
- Добавить GM-словарь (128 программ) как источник справочных имен в [main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py) или вынести в отдельный модуль [midi_program_names.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_program_names.py) и импортировать.

## Где встраиваем в вывод
- Обновить лог при `program_change` в `log_instrument_observability(...)` в [main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py), чтобы формат стал вида:
  - `program=48 (Strings Ensemble 1)`
  - или `program=48 (Strings Ensemble 1 [GM reference])`, когда это fallback.
- Обновить лог ручного переключения в `ProgramController.set_program(...)` в [main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py), чтобы UI/горячие клавиши показывали тот же формат имени.
- Опционально (для консистентности) расширить `[play] ...` строку в `note_on`, чтобы при verbose было видно не только номер, но и имя активного тембра.

## Форматирование и правила
- Добавить маленький helper, например `format_program_with_name(program, bank, source_hint)`:
  - возвращает уже готовую строку `"48 (Strings Ensemble 1)"`;
  - не меняет существующий numeric `program` в состоянии, только presentation layer;
  - сохраняет обратную совместимость логов (ключевые поля `program=... bank=...` остаются).
- Для неизвестных/вне диапазона значений оставить безопасный вывод:
  - `program=<num> (unknown)` без падений.

## Тесты
- Расширить тесты в [tests/test_favorites_logic.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_favorites_logic.py) отдельным блоком для чистых helper-функций (или создать [tests/test_program_names.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/tests/test_program_names.py)):
  - GM-hit: `program=48, bank=0 -> Strings Ensemble 1` без/с меткой по выбранному правилу;
  - non-GM-bank fallback: `bank!=0` -> GM reference с пометкой;
  - unknown/invalid safety cases.
- Прогон: `python -m unittest` (или таргетно по новому test-модулю).

## Проверка результата
- В verbose-режиме при входящем `program_change` видим строку `program=N (Name)`.
- При переключении `+/-` и по избранным видим тот же формат имени.
- Если имя не подтверждено конкретным каталогом устройства/банка, выводится явная пометка `GM reference`.
