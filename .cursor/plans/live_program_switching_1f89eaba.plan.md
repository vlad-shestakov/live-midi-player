---
name: Live program switching
overview: "Добавить в MIDI-слушатель живое переключение Program Change во время игры: с клавиатуры ПК и через MIDI-контролы, с применением к последнему активному каналу."
todos:
  - id: controller
    content: Добавить ProgramController для last-active channel и циклического изменения program ±1 (127->0, 0->127)
    status: pending
  - id: keyboard-input
    content: Интегрировать неблокирующий захват '+'/'-' в основном цикле run()
    status: pending
  - id: midi-triggers
    content: Добавить MIDI-триггеры program up/down через control_change и связать с ProgramController
    status: pending
  - id: observability
    content: Добавить понятные логи источника смены и итогового program/channel
    status: pending
  - id: smoke-test
    content: Проверить сценарии keyboard + MIDI trigger + обычный program_change
    status: pending
isProject: false
---

# План: live смена program во время игры

## Что добавляем
- Ввести единый `ProgramController`, который хранит текущее состояние по каналам (`program`, `bank`, `last_active_channel`) и умеет циклически менять `program` на `±1` (`127 -> 0`, `0 -> 127`).
- Подключить 2 источника команд:
  - клавиатура ПК (`+` / `-` в консоли),
  - MIDI-контролы (например, отдельные `control_change`-команды как триггеры `program_up/program_down`).
- Применять смену инструмента к **последнему активному MIDI-каналу** (по последним `note_on`/сообщениям), и сразу отправлять `program_change` в движок.

## Где меняем код
- [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py)
  - Расширить цикл `run()` для приема внешних команд смены программы без блокировки MIDI-цикла.
  - В `handle_message()`/наблюдаемости добавить обновление `last_active_channel`.
  - Добавить обработку MIDI-триггеров (по настраиваемым CC).
  - Логировать событие смены: источник (`keyboard`/`midi`), канал, старый/новый program.

## Детали поведения
- Границы: циклический wrap-around в диапазоне `0..127` (`127 + 1 => 0`, `0 - 1 => 127`).
- Изменение отправляется как `engine.program_change(new_program, target_channel)`.
- Сообщение в консоль в стиле текущих логов (`[instrument] ...`).
- По умолчанию оставить текущую совместимость: если триггеры не включены, поведение старого MIDI-пайплайна не ломается.

## Проверка
- Запустить как обычно (`start_MIDI.bat`) и убедиться, что:
  - `+` увеличивает `program`, `-` уменьшает;
  - смена идет на last-active channel;
  - входящий обычный `program_change` с MIDI все еще работает;
  - логи показывают корректный канал и номер программы.