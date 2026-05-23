---
name: README launch guide update
overview: Обновить README на русском с пошаговым запуском именно по сценариям из диалога и готовыми командами для выбранных MIDI-портов.
todos:
  - id: rewrite-readme-structure
    content: Перестроить README в формат пошагового запуска на русском.
    status: pending
  - id: add-user-specific-command
    content: Добавить готовую команду для портов LKMK3 MIDI 0 -> Microsoft GS Wavetable Synth 0.
    status: pending
  - id: add-latency-troubleshooting
    content: Добавить раздел по задержке и рекомендации для low-latency.
    status: pending
isProject: false
---

# Обновление README по запуску из диалога

## Что будет изменено
- Актуализировать инструкцию запуска в [d:\R_STUDIO\PRG\python\2026-05-23-midi-synt\README.md](d:\R_STUDIO\PRG\python\2026-05-23-midi-synt\README.md) под фактический workflow из диалога.
- Добавить короткий раздел «Быстрый старт» с последовательностью: установка -> активация venv -> список портов -> запуск.
- Вставить готовую команду под твой выбранный набор портов:
  - input: `LKMK3 MIDI 0`
  - output: `Microsoft GS Wavetable Synth 0`

## Структура будущего README
- Описание 2 режимов (`midi-out` и `fluidsynth`) простыми словами на русском.
- Пошаговый алгоритм запуска (нумерованные шаги).
- Раздел с готовыми командами:
  - команда для твоего текущего кейса `midi-out`;
  - команда для `fluidsynth` как альтернатива.
- Раздел «Проблемы и задержка» с практичными рекомендациями (ASIO/WASAPI, 64-128 buffer, 48kHz).

## Критерии готовности
- README читается как инструкция «с нуля» без необходимости смотреть чат.
- Все команды копируются и запускаются без дополнительной правки, кроме случаев где явно указан placeholder.
- Есть отдельная подсказка, что `Microsoft GS Wavetable Synth` может давать заметную задержку и когда лучше перейти на DAW/VST.

## Файлы
- Обновляется только [d:\R_STUDIO\PRG\python\2026-05-23-midi-synt\README.md](d:\R_STUDIO\PRG\python\2026-05-23-midi-synt\README.md).