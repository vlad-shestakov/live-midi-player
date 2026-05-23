---
name: menu item 5 numeric ports
overview: Переделать пункт 5 интерактивного меню configure_ports.bat на выбор входного и выходного MIDI-порта по номеру из списков с повторным запросом при ошибках.
todos:
  - id: rewrite-menu-item-5
    content: Переделать :menu_set_both на два вызова :select_port_by_number (input/output) и единое сохранение --set-config
    status: completed
  - id: preserve-error-flow
    content: Добавить/проверить возврат в меню при errorlevel 1 на любом шаге выбора
    status: cancelled
  - id: manual-checks-item-5
    content: Прогнать интерактивно пункт 5 и сверить show-config + midi_ports.json
    status: cancelled
isProject: false
---

# План: числовой выбор портов в пункте 5

## Цель
Обновить пункт `5` в интерактивном меню так, чтобы пользователь выбирал оба порта (входной и выходной) по номеру, без ручного ввода точных имен.

## Что изменить
- В [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat) переписать `:menu_set_both`:
  - вместо `set /p INPUT_NAME=...` и `set /p OUTPUT_NAME=...` вызывать существующую подпрограмму `:select_port_by_number` дважды:
    - сначала `"input"` -> `INPUT_NAME`,
    - затем `"output"` -> `OUTPUT_NAME`.
  - после успешного выбора обоих значений вызывать существующее сохранение:
    - `main.py --set-config --input-port "..." --output-port "..."`.

## Переиспользование текущей логики
- Использовать уже реализованную подпрограмму выбора по индексу `:select_port_by_number` из [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat), чтобы не дублировать:
  - разбор `main.py --list-ports`,
  - построение нумерованного списка,
  - проверку диапазона и числового ввода,
  - цикл повторного запроса.
- Сохранение оставить через [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py) (`--set-config`), чтобы валидация имен портов происходила в одном месте.

## Ошибки и поведение
- Если выбор входного порта не удался (`errorlevel 1`) — возвращаться в меню без попытки выбора выходного.
- Если входной выбран, но не удался выбор выходного — возвращаться в меню без сохранения изменений.
- Сохранять конфигурацию только когда оба выбора успешны.

## Проверка
- Ручной сценарий в `configure_ports.bat`:
  - пункт `5`: выбрать валидные индексы для входа и выхода — значения должны сохраниться.
  - ввести нечисловой индекс или индекс вне диапазона на любом шаге — должен быть повторный запрос.
  - при отсутствии входных или выходных портов — корректное сообщение и возврат в меню.
- Подтвердить результат через `show-config` и файл [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json).