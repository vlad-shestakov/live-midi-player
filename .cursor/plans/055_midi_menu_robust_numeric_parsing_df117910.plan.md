---
name: midi menu robust numeric parsing
overview: Исправить нестабильность выбора MIDI-портов в пунктах 3/4/5 из-за хрупкого парсинга list-ports в bat и подтвердить поведение ручной проверкой.
todos:
  - id: stabilize-list-parsing
    content: Сделать устойчивый парсинг list-ports в select_port_by_number без жесткой привязки к заголовкам
    status: completed
  - id: align-menu-3-4-5
    content: Проверить и выровнять обработку ошибок/возврата для пунктов 3, 4 и 5
    status: completed
  - id: manual-interactive-validation
    content: Ручной прогон 3/4/5 и сверка show-config + midi_ports.json
    status: completed
isProject: false
---

# План: устойчивый выбор MIDI-портов по номеру

## Цель
Убрать сценарий, когда пункт `3` возвращает в главное меню без выбора, и унифицировать стабильный числовой выбор портов для пунктов `3`, `4` и `5`.

## Область изменений
- [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/configure_ports.bat)
- [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/.cursor/plans/051_midi_port_numeric_selection_b6f635ac.plan.md](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/.cursor/plans/051_midi_port_numeric_selection_b6f635ac.plan.md)

## Шаги
- Переписать логику `:select_port_by_number` так, чтобы извлечение портов не зависело от точного совпадения кириллических заголовков секций.
- Сохранить существующий UX: список по номерам, валидация числа и диапазона, повторный запрос при ошибке.
- Зафиксировать корректное поведение для:
  - `:menu_set_input` (пункт `3`),
  - `:menu_set_output` (пункт `4`),
  - `:menu_set_both` (пункт `5`).
- Прогнать ручную проверку интерактивного сценария и подтвердить сохранение через `show-config` и `midi_ports.json`.

## Критерии готовности
- Пункт `3` не возвращается в меню до завершения выбора (кроме реальной ошибки/отсутствия портов).
- Пункты `4` и `5` работают на той же устойчивой логике.
- Конфигурация после выбора отражается в `main.py --show-config` и [D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json](D:/R_STUDIO/PRG/python/2026-05-23-midi-synt/midi_ports.json).