#!/usr/bin/env python3
"""
check_po.py — аудит .po файлов.

Проверяет locale/en и locale/ru на:
- fuzzy-записи (переводы с флагом "#, fuzzy" — Django их игнорирует)
- пустые msgstr (перевод не заполнен)
- obsolete-записи (устаревшие msgid, помеченные "#~")

Использование (из корня проекта):
    python scripts/i18n/check_po.py

Ожидаемый результат для чистого .po:
    Fuzzy: 0, Empty: 0, Obsolete: 0
"""
import polib
from pathlib import Path

# Корень проекта — на 2 уровня выше этого скрипта
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def check_po(path: Path) -> dict:
    """Проверяет .po файл на fuzzy, пустые и obsolete записи."""
    po = polib.pofile(str(path))

    fuzzy = [e for e in po if e.flags and 'fuzzy' in e.flags]
    empty = [
        e for e in po
        if e.msgid
        and not e.msgstr
        and not (e.msgid_plural and e.msgstr_plural)
    ]
    obsolete = po.obsolete_entries()

    return {
        'path': path,
        'total': len(po),
        'fuzzy': fuzzy,
        'empty': empty,
        'obsolete': obsolete,
    }


def print_result(result: dict, show_limit: int = 10) -> None:
    print(f"=== {result['path']} ===")
    print(f"  Всего записей: {result['total']}")
    print(f"  Fuzzy:    {len(result['fuzzy'])}")
    print(f"  Empty:    {len(result['empty'])}")
    print(f"  Obsolete: {len(result['obsolete'])}")

    if result['fuzzy']:
        print("  --- FUZZY ---")
        for e in result['fuzzy'][:show_limit]:
            loc = e.occurrences[0] if e.occurrences else ('?', 0)
            print(f"    [{loc[0]}:{loc[1]}] {e.msgid[:70]}")

    if result['empty']:
        print("  --- EMPTY ---")
        for e in result['empty'][:show_limit]:
            loc = e.occurrences[0] if e.occurrences else ('?', 0)
            print(f"    [{loc[0]}:{loc[1]}] {e.msgid[:70]}")

    if result['obsolete']:
        print(f"  --- OBSOLETE (первые {show_limit}) ---")
        for e in result['obsolete'][:show_limit]:
            print(f"    {e.msgid[:70]}")

    print()


def main() -> None:
    po_files = [
        BASE_DIR / 'locale' / 'en' / 'LC_MESSAGES' / 'django.po',
        BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.po',
    ]

    for path in po_files:
        if not path.exists():
            print(f"⚠️ Файл не найден: {path}\n")
            continue
        try:
            result = check_po(path)
            print_result(result)
        except Exception as e:
            print(f"❌ Ошибка при чтении {path}: {e}\n")


if __name__ == '__main__':
    main()