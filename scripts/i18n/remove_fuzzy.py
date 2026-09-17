#!/usr/bin/env python3
"""
remove_fuzzy.py — удаление флага "#, fuzzy" из шапки .po.

⚠️ ВНИМАНИЕ: этот скрипт удаляет "#, fuzzy" ТОЛЬКО из шапки файла
(до первого msgid). Fuzzy-флаги на конкретных записях НЕ удаляются.

Если нужно снять fuzzy со всех записей — используйте Poedit
или `msgattrib --clear-fuzzy`.

Использование (из корня проекта):
    python scripts/i18n/remove_fuzzy.py
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    for lang in ('ru', 'en'):
        po_path = BASE_DIR / 'locale' / lang / 'LC_MESSAGES' / 'django.po'

        if not po_path.exists():
            print(f'❌ {po_path} не найден')
            continue

        with open(po_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        removed = 0
        header_done = False

        for line in lines:
            if not header_done and line.strip() == '#, fuzzy':
                removed += 1
                continue

            if not header_done and line.strip() == 'msgid ""':
                header_done = True

            new_lines.append(line)

        with open(po_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print(f'✅ {lang}: удалено строк "#, fuzzy" из шапки: {removed}')


if __name__ == '__main__':
    main()