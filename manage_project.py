#!/usr/bin/env python3
"""
manage_project.py — обёртка над manage.py для типовых операций.

Управление проектом LYNXREACTOR: setup, dev, prod, i18n, tests.

Использование:
    python manage_project.py <command>

Команды:
    setup        — первоначальная настройка (venv, миграции, superuser)
    dev          — запуск в режиме разработки (Django + Celery)
    prod         — запуск в проде (collectstatic, migrate, gunicorn)
    install      — установка зависимостей из requirements.txt
    translate    — обновление переводов (makemessages + compilemessages)
    check_i18n   — аудит .po файлов (fuzzy/empty/obsolete + selfmsgstr)
    reset_db     — сброс БД (flush + migrate + superuser)
    fixtures     — создание фикстур
    sitemap      — генерация sitemap
    indexnow     — отправка URL в IndexNow
    telegram     — тест Telegram-бота
    test         — запуск всех тестов (pytest)
    test_fast    — только изменённые тесты
    coverage     — тесты с покрытием
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent


def run_command(command, description=None, check=True):
    """Выполняет команду с выводом описания."""
    if description:
        print(f"\n{'=' * 60}")
        print(f"📌 {description}")
        print('=' * 60)

    print(f"▶️ {command}\n")

    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, cwd=BASE_DIR,
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if check and result.returncode != 0:
        print(f"⚠️ Команда завершилась с кодом {result.returncode}")

    return result


# ============================================================
# SETUP
# ============================================================

def setup_project():
    """Первоначальная настройка проекта."""
    commands = [
        ('python -m venv venv', 'Создание виртуального окружения'),
        ('pip install -r requirements.txt', 'Установка зависимостей (prod)'),
        ('pip install -r requirements-dev.txt', 'Установка зависимостей (dev)'),
        ('python manage.py migrate', 'Применение миграций'),
        ('python manage.py createsuperuser', 'Создание суперпользователя'),
        ('python manage.py collectstatic --noinput', 'Сборка статики'),
        ('python manage.py compilemessages', 'Компиляция переводов'),
    ]

    print('\n🚀 НАСТРОЙКА ПРОЕКТА LYNXREACTOR')
    print('=' * 60)

    for command, desc in commands:
        run_command(command, desc)


# ============================================================
# DEV / PROD
# ============================================================

def run_dev():
    """Запуск в режиме разработки."""
    print('\n🔧 ЗАПУСК В РЕЖИМЕ РАЗРАБОТКИ')
    print('=' * 60)

    try:
        import redis
        r = redis.from_url('redis://localhost:6379/0')
        r.ping()
        print('✅ Redis работает')
        start_celery = True
    except Exception:
        print('⚠️ Redis не найден, Celery будет работать в EAGER режиме')
        start_celery = False

    if start_celery:
        run_command(
            'start cmd /k celery -A lynxreactor worker -l info',
            'Запуск Celery worker',
        )
        run_command(
            'start cmd /k celery -A lynxreactor beat -l info',
            'Запуск Celery beat',
        )

    run_command('python manage.py runserver', 'Запуск Django сервера')


def run_prod():
    """Запуск в режиме продакшена."""
    print('\n🚀 ЗАПУСК В РЕЖИМЕ ПРОДАКШЕНА')
    print('=' * 60)

    commands = [
        ('python manage.py collectstatic --noinput', 'Сборка статики'),
        ('python manage.py migrate', 'Применение миграций'),
        ('python manage.py compilemessages', 'Компиляция переводов'),
        ('gunicorn lynxreactor.wsgi:application --bind 0.0.0.0:8000', 'Запуск Gunicorn'),
    ]

    for command, desc in commands:
        run_command(command, desc)


# ============================================================
# INSTALL
# ============================================================

def install_requirements():
    """Установка зависимостей."""
    print('\n📦 УСТАНОВКА ЗАВИСИМОСТЕЙ')
    print('=' * 60)

    if not (BASE_DIR / 'venv').exists():
        print('⚠️ Виртуальное окружение не найдено. Создаем...')
        run_command('python -m venv venv', 'Создание виртуального окружения')

    run_command('pip install -r requirements.txt', 'Зависимости prod')
    run_command('pip install -r requirements-dev.txt', 'Зависимости dev')


# ============================================================
# I18N
# ============================================================

def update_translations():
    """Обновление переводов."""
    print('\n🌍 ОБНОВЛЕНИЕ ПЕРЕВОДОВ')
    print('=' * 60)

    commands = [
        ('python manage.py makemessages -l ru', 'Регенерация .po (RU)'),
        ('python manage.py makemessages -l en', 'Регенерация .po (EN)'),
        ('python manage.py compilemessages', 'Компиляция .mo'),
    ]

    for command, desc in commands:
        run_command(command, desc)


def check_i18n():
    """Аудит .po файлов через scripts/i18n/."""
    print('\n🔍 АУДИТ ПЕРЕВОДОВ')
    print('=' * 60)

    scripts = [
        ('python scripts/i18n/check_po.py', 'Аудит .po (fuzzy / empty / obsolete)'),
        ('python scripts/i18n/check_po_selfmsgstr.py', 'Поиск msgstr == msgid (RU)'),
        ('python scripts/i18n/check_i18n.py', 'Проверка строк EN / RU'),
    ]

    for command, desc in scripts:
        run_command(command, desc, check=False)


def compile_mo():
    """Компиляция .po → .mo через polib (fallback)."""
    print('\n🔨 КОМПИЛЯЦИЯ .mo (polib)')
    print('=' * 60)

    run_command('python scripts/i18n/compile_mo.py', 'Компиляция через polib')


# ============================================================
# DATABASE
# ============================================================

def reset_database():
    """Сброс базы данных."""
    print('\n⚠️ СБРОС БАЗЫ ДАННЫХ')
    print('=' * 60)

    confirm = input('Вы уверены? (y/n): ')
    if confirm.lower() != 'y':
        print('❌ Отменено')
        return

    commands = [
        ('python manage.py flush --noinput', 'Очистка БД'),
        ('python manage.py migrate', 'Применение миграций'),
        ('python manage.py createsuperuser', 'Создание суперпользователя'),
    ]

    for command, desc in commands:
        run_command(command, desc)


def create_fixtures():
    """Создание фикстур."""
    print('\n💾 СОЗДАНИЕ ФИКСТУР')
    print('=' * 60)

    (BASE_DIR / 'fixtures').mkdir(exist_ok=True)

    commands = [
        ('python manage.py dumpdata agency > fixtures/agency_data.json', 'Данные приложения'),
        (
            'python manage.py dumpdata --exclude auth.permission --exclude contenttypes > fixtures/full_dump.json',
            'Полный дамп',
        ),
    ]

    for command, desc in commands:
        run_command(command, desc)


# ============================================================
# SEO
# ============================================================

def generate_sitemap():
    """Генерация sitemap."""
    print('\n🗺️ ГЕНЕРАЦИЯ SITEMAP')
    print('=' * 60)
    run_command('python manage.py sitemap', 'Генерация sitemap')


def send_to_indexnow():
    """Отправка в IndexNow."""
    print('\n📤 ОТПРАВКА В INDEXNOW')
    print('=' * 60)
    run_command('python manage.py indexnow_submit --all', 'Отправка всех URL')


# ============================================================
# TELEGRAM
# ============================================================

def test_telegram():
    """Тестирование Telegram бота."""
    print('\n🤖 ТЕСТИРОВАНИЕ TELEGRAM БОТА')
    print('=' * 60)
    run_command('python manage.py test_telegram', 'Тестирование')


# ============================================================
# TESTS
# ============================================================

def run_tests():
    """Запуск всех тестов через pytest."""
    print('\n🧪 ЗАПУСК ТЕСТОВ (pytest)')
    print('=' * 60)
    run_command('pytest agency/tests/ -v', 'Все тесты')


def run_tests_fast():
    """Запуск только изменённых тестов (pytest -x, fail fast)."""
    print('\n⚡ БЫСТРЫЙ ЗАПУСК ТЕСТОВ')
    print('=' * 60)
    run_command('pytest agency/tests/ -x --ff', 'Fail fast + только упавшие')


def run_coverage():
    """Запуск тестов с покрытием."""
    print('\n📊 ТЕСТЫ С ПОКРЫТИЕМ')
    print('=' * 60)
    run_command(
        'pytest agency/tests/ --cov=agency --cov-report=term-missing --cov-report=html',
        'Coverage',
    )


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Управление проектом LYNXREACTOR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        'command',
        choices=[
            'setup', 'dev', 'prod', 'install',
            'translate', 'check_i18n', 'compile_mo',
            'reset_db', 'fixtures',
            'sitemap', 'indexnow', 'telegram',
            'test', 'test_fast', 'coverage',
        ],
        help='Команда для выполнения',
    )

    args = parser.parse_args()

    commands = {
        'setup': setup_project,
        'dev': run_dev,
        'prod': run_prod,
        'install': install_requirements,
        'translate': update_translations,
        'check_i18n': check_i18n,
        'compile_mo': compile_mo,
        'reset_db': reset_database,
        'fixtures': create_fixtures,
        'sitemap': generate_sitemap,
        'indexnow': send_to_indexnow,
        'telegram': test_telegram,
        'test': run_tests,
        'test_fast': run_tests_fast,
        'coverage': run_coverage,
    }

    commands[args.command]()


if __name__ == '__main__':
    main()