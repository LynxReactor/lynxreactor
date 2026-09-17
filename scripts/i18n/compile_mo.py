#!/usr/bin/env python3
"""
compile_mo.py — компиляция .po → .mo через polib.

Альтернатива `python manage.py compilemessages`.
Полезно, если системный gettext недоступен или не работает на Windows.

Использование (из корня проекта):
    python scripts/i18n/compile_mo.py
"""
import os
import sys
from pathlib import Path

try:
    import polib
except ImportError:
    print('📦 Установка polib...')
    os.system('pip install polib')
    import polib

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def compile_po_to_mo(lang_code: str) -> bool:
    """Компиляция .po в .mo через polib."""
    po_path = BASE_DIR / 'locale' / lang_code / 'LC_MESSAGES' / 'django.po'
    mo_path = BASE_DIR / 'locale' / lang_code / 'LC_MESSAGES' / 'django.mo'

    if not po_path.exists():
        print(f'❌ {po_path} не найден')
        return False

    if po_path.stat().st_size < 10:
        print(f'⚠️ {po_path} слишком маленький, возможно нет переводов')
        return False

    try:
        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        print(f'✅ {mo_path} создан ({po_path.stat().st_size} байт)')
        return True
    except Exception as e:
        print(f'❌ Ошибка для {lang_code}: {e}')
        return False


def main() -> None:
    print('🔨 Компиляция переводов...')
    print('=' * 50)

    locale_dir = BASE_DIR / 'locale'
    if not locale_dir.exists():
        print('❌ Директория locale не найдена')
        print('Создайте директорию: mkdir locale')
        sys.exit(1)

    langs = ['ru', 'en']
    success_count = 0

    for lang in langs:
        print(f'📝 Компиляция {lang}...')
        if compile_po_to_mo(lang):
            success_count += 1

    print('=' * 50)
    if success_count == len(langs):
        print('🎉 Все переводы скомпилированы!')
        print('Перезапустите сервер: python manage.py runserver')
    else:
        print(f'⚠️ Скомпилировано {success_count} из {len(langs)} языков')


if __name__ == '__main__':
    main()