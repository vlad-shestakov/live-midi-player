---
name: filter clock verbose
overview: Точечно изменить verbose-логирование в main.py так, чтобы MIDI clock не печатался в консоль, но продолжал обрабатываться и форвардиться в движок без изменения поведения sync.
todos:
  - id: locate-verbose-print
    content: Подготовить точечную правку в цикле обработки `iter_pending()` внутри `run()` в `main.py`.
    status: completed
  - id: add-clock-log-filter
    content: "Ограничить только печать: пропускать `msg.type == \"clock\"` в `verbose`, не трогая `handle_message`."
    status: completed
  - id: validate-behavior
    content: Проверить, что `clock` исчез из лога, а маршрутизация MIDI и sync не изменились.
    status: completed
isProject: false
---

# План: скрыть clock в verbose без потери sync

## Что меняем
- В цикле обработки входящих сообщений в [d:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py](d:/R_STUDIO/PRG/python/2026-05-23-midi-synt/main.py) разделить:
  - условие печати в `verbose`;
  - фактическую обработку/форвардинг сообщения.
- Добавить фильтр только для вывода в консоль: не печатать сообщения с `msg.type == "clock"`.
- Сохранить текущий вызов `handle_message(msg, engine, args.channel)` для всех типов сообщений, включая `clock`.

## Точка изменения
- Блок в `run()` рядом с текущей логикой:
  - `if args.verbose: print(msg)`
  - `handle_message(msg, engine, args.channel)`
- Концептуально должно стать: печатать только если `args.verbose` и `msg.type != "clock"`, а затем всегда вызывать `handle_message(...)`.

## Проверка после правки
- Запуск с `--verbose`: в логе есть `note_on/note_off/...`, но нет строк `clock time=0`.
- При этом игра и синхронизация не меняются (сообщения `clock` продолжают проходить через `handle_message` -> `engine.forward_message`).
- Быстрый регресс-чек: остальные типы сообщений в `verbose` продолжают печататься как раньше.