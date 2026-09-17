#!/usr/bin/env python3
"""
check_po_selfmsgstr.py — поиск "непереведённых" записей в RU .po.

Ищет записи, где msgstr == msgid. Для RU это означает, что
перевод отсутствует (msgid случайно скопирован в msgstr).

Для EN такой сценарий — норма (msgid уже на английском).

Использование (из корня проекта):
    python scripts/i18n/check_po_selfmsgstr.py

Ожидаемый результат для чистого RU .po:
    Осталось ~12 записей (бренды: Email, Telegram, WhatsApp, ...)
"""
import polib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def check_selfmsgstr(path: Path) -> dict:
    po = polib.pofile(str(path))

    # Только непустые записи + ASCII msgid
    same = [
        e for e in po
        if e.msgid
        and e.msgstr == e.msgid
        and e.msgid.isascii()
    ]

    ascii_total = [e for e in po if e.msgid and e.msgid.isascii()]

    return {
        'path': path,
        'total': len(po),
        'ascii_total': len(ascii_total),
        'same': same,
    }


def print_result(result: dict, show_limit: int = 30) -> None:
    print(f"=== {result['path']} ===")
    print(f"  Всего записей:                 {result['total']}")
    print(f"  С ASCII msgid:                 {result['ascii_total']}")
    print(f"  msgstr == msgid (подозрительно): {len(result['same'])}")

    if result['same']:
        print(f"  --- СПИСОК (первые {show_limit}) ---")
        for e in result['same'][:show_limit]:
            loc = e.occurrences[0] if e.occurrences else ('?', 0)
            print(f"    [{loc[0]}:{loc[1]}] {e.msgid[:70]}")
    print()


def main() -> None:
    path = BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.po'
    if not path.exists():
        print(f"⚠️ Файл не найден: {path}")
        return
    try:
        result = check_selfmsgstr(path)
        print_result(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    main()