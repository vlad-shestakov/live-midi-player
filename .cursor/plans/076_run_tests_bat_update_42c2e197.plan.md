---
name: run tests bat update
overview: Модифицировать `run_tests.bat`, чтобы без аргументов запускался весь тестовый набор, а с аргументом — точечный запуск `unittest` (модуль/класс/тест).
todos:
  - id: update-bat-arg-branch
    content: "Добавить ветвление по аргументу в run_tests.bat: full-suite по умолчанию, targeted при наличии target"
    status: completed
  - id: keep-existing-flow
    content: Сохранить существующую логику активации venv и обработки exit code/pause
    status: completed
  - id: validate-modes
    content: Проверить default и targeted сценарии и зафиксировать критерии успеха
    status: completed
isProject: false
---

# План: модификация run_tests.bat для full и targeted запуска

## Цель
Сохранить текущий безопасный default-поток (полный suite), но добавить быстрый точечный запуск для масштабируемой разработки.

## Изменения в скрипте
- Обновить [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/run_tests.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/run_tests.bat):
  - если аргумент не передан (`%~1` пустой) — запускать полный набор:
    - `python -m unittest discover -s tests -p "test_*.py"`
  - если аргумент передан — запускать target напрямую:
    - `python -m unittest %~1`
- Добавить краткое сообщение в консоль о выбранном режиме:
  - `mode=full-suite` или `mode=targeted`, чтобы сразу понимать, что именно запустилось.
- Сохранить существующую логику:
  - переход в директорию скрипта;
  - активация `.venv`;
  - обработка `ERRORLEVEL`;
  - финальный `pause` и корректный `exit /b`.

## Поддерживаемые примеры
- Full suite (default):
  - `run_tests.bat`
- Targeted модуль:
  - `run_tests.bat tests.test_program_names`
- Targeted класс:
  - `run_tests.bat tests.test_program_names.ProgramNameFormattingTests`
- Targeted единичный тест:
  - `run_tests.bat tests.test_program_names.ProgramNameFormattingTests.test_gm_program_name_hit`

## Проверка после правки
- Прогнать 4 сценария: default + 3 targeted (модуль/класс/тест).
- Убедиться, что:
  - в каждом сценарии отображается правильный режим;
  - код возврата корректно отражает успех/ошибку;
  - поведение full-suite не изменилось.

## Критерии готовности
- Скрипт остается обратно совместимым (`run_tests.bat` работает как раньше).
- Добавлен стабильный и удобный targeted запуск одним аргументом.
- Сообщения в консоли однозначно показывают, какой режим запущен.