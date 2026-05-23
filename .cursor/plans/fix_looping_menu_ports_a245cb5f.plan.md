---
name: fix looping menu ports
overview: Устранить возврат в главное меню для пунктов 3/4/5, переведя bat на машинно-читаемый список портов из main.py вместо хрупкого inline-парсинга.
todos:
  - id: add-machine-readable-ports-cli
    content: Добавить в main.py CLI-флаг для JSON-вывода списков MIDI-портов
    status: completed
  - id: switch-bat-to-json-source
    content: Перевести select_port_by_number в configure_ports.bat на получение портов из нового JSON-вывода
    status: completed
  - id: validate-menu-3-4-5-end-to-end
    content: Проверить интерактивные сценарии 3/4/5 и сверить show-config + midi_ports.json
    status: completed
isProject: false
---

# План: устранение зацикливания 3/4/5

## Цель
Стабилизировать пункты `3`, `4`, `5` в интерактивном меню, чтобы выбор порта по номеру всегда доходил до запроса индекса и не возвращал пользователя в главное меню без причины.

## Почему сейчас ломается
- В [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat) `:select_port_by_number` строит список через inline-команду `python -c ...` внутри `for /f`.
- Этот путь чувствителен к CMD/PowerShell quoting и ошибкам окружения; при сбое `PORT_COUNT` остается `0`, срабатывает `exit /b 1`, а в `:menu_set_input/:menu_set_output/:menu_set_both` происходит `goto menu`.

## Изменения
- В [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py):
  - добавить отдельный аргумент CLI для машинно-читаемого вывода портов (например `--list-ports-json`),
  - печатать JSON вида `{ "inputs": [...], "outputs": [...] }` и завершаться без запуска основного цикла.
- В [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat):
  - убрать inline `python -c ...` из `:select_port_by_number`,
  - получать список через новый флаг `main.py --list-ports-json`,
  - извлекать только нужный массив (`inputs` или `outputs`) и формировать `PORT_1..PORT_N`.
- Сохранить текущий UX:
  - нумерованный список,
  - проверка числового ввода и диапазона,
  - повторный запрос при ошибке,
  - возврат в меню только при реальном отсутствии портов/ошибке получения списка.

## Проверка
- Прогон меню:
  - `3` -> выбор входного индекса -> сохранение,
  - `4` -> выбор выходного индекса -> сохранение,
  - `5` -> последовательный выбор вход/выход -> единое сохранение.
- Негативные кейсы:
  - пустой ввод,
  - нечисловой ввод,
  - индекс вне диапазона.
- Валидация результата:
  - `configure_ports.bat show-config`,
  - [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json).

## Критерии готовности
- Пункты `3/4/5` больше не «мерцают» и не выкидывают в главное меню до завершения шага выбора.
- Выбранные значения стабильно сохраняются и отражаются в `show-config` и JSON-конфиге.