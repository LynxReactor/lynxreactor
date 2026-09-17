#!/usr/bin/env python3
"""
translate_po.py — автоперевод RU .po по словарю.

Читает locale/ru/LC_MESSAGES/django.po, для записей с msgstr == msgid
(или пустым msgstr) подставляет перевод из DICTIONARY.

Технические бренды (Email, Telegram, WhatsApp, Viber, LinkedIn, ...)
намеренно НЕ включены — оставляем латиницей.

Использование (из корня проекта):
    python scripts/i18n/translate_po.py --dry-run    # только показать
    python scripts/i18n/translate_po.py              # применить (создаёт бэкап)
"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

import polib

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ============================================================
# СЛОВАРЬ ПЕРЕВОДОВ
# ============================================================
DICTIONARY = {
    # --- Модели: общие поля ---
    "Date created": "Дата создания",
    "Date updated": "Дата обновления",
    "Active": "Активно",
    "Order": "Порядок",
    "Name": "Название",
    "Title": "Заголовок",
    "Subtitle": "Подзаголовок",
    "Description": "Описание",
    "Category": "Категория",
    "Icon": "Иконка",
    "Logo": "Логотип",
    "URL": "URL",
    "URL slug": "URL-слаг",
    "Image": "Изображение",
    "Link": "Ссылка",
    "Text": "Текст",
    "Note": "Примечание",
    "Rating": "Рейтинг",
    "Message": "Сообщение",
    "Status": "Статус",
    "Language": "Язык",
    "Source": "Источник",
    "Phone": "Телефон",
    "Address": "Адрес",
    "Page": "Страница",
    "Preview": "Превью",
    "No image": "Нет изображения",
    # ... (весь остальной словарь из вашего translate_po.py)
}


def translate_po(path: Path, dry_run: bool = False) -> dict:
    po = polib.pofile(str(path))

    stats = {
        'total': len(po),
        'translated': 0,
        'skipped_already_ru': 0,
        'skipped_no_dict': 0,
        'missing_from_dict': [],
    }

    for entry in po:
        if not entry.msgid:
            continue

        if entry.msgstr and entry.msgstr != entry.msgid:
            stats['skipped_already_ru'] += 1
            continue

        if entry.msgid_plural:
            continue

        if entry.msgid not in DICTIONARY:
            if entry.msgid.isascii():
                stats['missing_from_dict'].append(entry.msgid)
            continue

        new_msgstr = DICTIONARY[entry.msgid]
        if new_msgstr != entry.msgstr:
            entry.msgstr = new_msgstr
            stats['translated'] += 1

            if dry_run:
                print(f"  {entry.msgid!r} → {new_msgstr!r}")

    if not dry_run:
        backup_path = path.with_suffix(
            f".po.bak-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy(path, backup_path)
        print(f"💾 Бэкап: {backup_path}")

        po.save()
        print(f"✅ Сохранён: {path}")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description='Автоперевод RU .po')
    parser.add_argument('--dry-run', action='store_true',
                        help='Показать, что будет изменено (без сохранения)')
    parser.add_argument('--path',
                        default=str(BASE_DIR / 'locale' / 'ru' / 'LC_MESSAGES' / 'django.po'),
                        help='Путь к .po файлу')
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"❌ Файл не найден: {path}")
        return

    print(f"📖 Чтение: {path}")
    print(f"📊 Словарь: {len(DICTIONARY)} записей")
    print(f"🔧 Режим: {'DRY-RUN' if args.dry_run else 'ПРИМЕНЕНИЕ'}")
    print()

    stats = translate_po(path, dry_run=args.dry_run)

    print()
    print("=" * 60)
    print(f"Всего записей:       {stats['total']}")
    print(f"Переведено:          {stats['translated']}")
    print(f"Уже переведено:      {stats['skipped_already_ru']}")
    print(f"Нет в словаре:       {len(stats['missing_from_dict'])}")

    if stats['missing_from_dict']:
        print()
        print("⚠️  Записи, которых нет в словаре (первые 20):")
        for msgid in stats['missing_from_dict'][:20]:
            print(f"    {msgid!r}")
        if len(stats['missing_from_dict']) > 20:
            print(f"    ... и ещё {len(stats['missing_from_dict']) - 20}")
    print("=" * 60)


if __name__ == '__main__':
    main()