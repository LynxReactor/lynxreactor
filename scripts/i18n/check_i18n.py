#!/usr/bin/env python3
"""
check_i18n.py — быстрая проверка переводов конкретных строк.

Загружает Django, переключает язык и показывает переводы
заданных строк для EN и RU.

Использование (из корня проекта):
    python scripts/i18n/check_i18n.py

Зачем:
    Быстро убедиться, что .po/.mo применились.
    Если строка на EN возвращает саму себя — перевод отсутствует.
"""
import os
import sys
from pathlib import Path

# Корень проекта — чтобы Django нашёл lynxreactor/settings/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lynxreactor.settings.dev')

import django  # noqa: E402
django.setup()

from django.utils import translation  # noqa: E402
from django.utils.translation import gettext  # noqa: E402


TEST_STRINGS = [
    'Your email',
    'Сменить тему',
    'Номер телефона',
    'Введите ваш email',
    'Подписаться',
    'Подпишитесь на обновления',
]


def main() -> None:
    with translation.override('en'):
        print('=== EN translations ===')
        for s in TEST_STRINGS:
            print(f'  {s!r}  ->  {gettext(s)!r}')

    print()

    with translation.override('ru'):
        print('=== RU translations ===')
        for s in TEST_STRINGS:
            print(f'  {s!r}  ->  {gettext(s)!r}')


if __name__ == '__main__':
    main()