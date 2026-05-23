---
name: README GitHub polish
overview: "Обновить README.md в формат главной витрины репозитория live-midi-player: сделать понятный вход, структурировать разделы и встроить релевантные скриншоты из res/scr."
todos:
  - id: readme-hero
    content: Переписать верх README в формате GitHub-витрины и встроить главный скриншот main-v02
    status: completed
  - id: readme-quickstart
    content: Собрать компактный и понятный Quick Start для Windows с блоком настройки портов и скриншотом config
    status: completed
  - id: readme-controls
    content: Добавить раздел о горячих клавишах, избранных инструментах и практическом live-использовании
    status: completed
  - id: readme-reference
    content: "Обновить справочные разделы: CLI, требования, зависимости, тесты и структура проекта"
    status: completed
isProject: false
---

# План обновления README для GitHub

## Цель
Сделать `README.md` главным презентационным файлом репозитория `live-midi-player`, сохранив практические инструкции по запуску и добавив визуальную часть для быстрого понимания проекта.

## Что будет изменено
- Переработать верхнюю часть README: новый заголовок, короткое позиционирование проекта и блок ключевых возможностей.
- Встроить главный скриншот из `[res/scr/midi-live-player-main-v02.png](res/scr/midi-live-player-main-v02.png)` сразу после вводного блока.
- Оформить раздел быстрого старта как пошаговый сценарий установки и первого запуска с командами для Windows.
- В раздел настройки добавить скриншот `[res/scr/midi-live-player-config.png](res/scr/midi-live-player-config.png)` рядом с инструкциями по `configure_ports.bat`.
- Добавить отдельный блок по управлению во время игры: горячие клавиши, избранные инструменты и поведение `Program Change`.
- Обновить и структурировать справочный блок CLI (движки, порты, полезные флаги, примеры запуска), чтобы не терять текущую техническую ценность.
- Добавить короткие служебные разделы для GitHub-публикации: требования, зависимости из `[requirements.txt](requirements.txt)`, запуск тестов из `[run_tests.bat](run_tests.bat)` и краткую структуру проекта.

## Файлы в работе
- Основной редактируемый файл: `[README.md](README.md)`.
- Источники фактов для синхронизации документации:
  - `[main.py](main.py)`
  - `[requirements.txt](requirements.txt)`
  - `[configure_ports.bat](configure_ports.bat)`
  - `[run_tests.bat](run_tests.bat)`
  - `[midi_favorites.json](midi_favorites.json)`
  - изображения в `[res/scr](res/scr)
`