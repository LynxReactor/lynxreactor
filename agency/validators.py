# agency/validators.py

from django.core.exceptions import ValidationError


def validate_features(value):
    """
    Валидация поля Tariff.features.
    Ожидается: {"ru": ["Особенность 1"], "en": ["Feature 1"]}
    """
    if value is None or value == '':
        return

    if not isinstance(value, dict):
        raise ValidationError('Ожидается объект вида {"ru": [...], "en": [...]}')

    for lang in ('ru', 'en'):
        if lang in value:
            items = value[lang]
            if not isinstance(items, list):
                raise ValidationError(f'Ключ "{lang}" должен быть массивом строк')
            for i, item in enumerate(items):
                if not isinstance(item, str):
                    raise ValidationError(
                        f'Элемент #{i + 1} в "{lang}" должен быть строкой'
                    )


def validate_technologies(value):
    """
    Валидация поля PortfolioItem.technologies.

    Поддерживает два формата:
    - ["Python", "Django", "PostgreSQL"]  (legacy)
    - {"ru": ["Python", "Django"], "en": ["Python", "Django"]}  (текущий)
    """
    if value is None or value == '':
        return

    # Формат {ru: [...], en: [...]}
    if isinstance(value, dict):
        for lang in ('ru', 'en'):
            if lang in value:
                items = value[lang]
                if not isinstance(items, list):
                    raise ValidationError(f'Ключ "{lang}" должен быть массивом строк')
                for i, item in enumerate(items):
                    if not isinstance(item, str):
                        raise ValidationError(
                            f'Элемент #{i + 1} в "{lang}" должен быть строкой'
                        )
        return

    # Формат ["Python", "Django"]
    if not isinstance(value, list):
        raise ValidationError(
            'Ожидается массив строк или объект {ru: [...], en: [...]}'
        )
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f'Элемент #{i + 1} должен быть строкой')


def validate_tags(value):
    """
    Валидация поля BlogPost.tags.
    Ожидается: ["python", "django", "seo"]
    """
    if value is None or value == '':
        return

    if not isinstance(value, list):
        raise ValidationError('Ожидается массив строк, например ["python", "django"]')

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f'Элемент #{i + 1} должен быть строкой')


def validate_pdf_file(file):
    """
    Проверка, что загруженный файл — настоящий PDF.

    Проверяем:
    1. Расширение .pdf (через FileExtensionValidator в поле).
    2. PDF-сигнатуру: файл должен начинаться с %PDF-.

    Это защищает от переименования .exe → .pdf.
    """
    if not file:
        return

    # Читаем первые 5 байт
    try:
        file.seek(0)
        header = file.read(5)
        file.seek(0)  # вернуть указатель
    except Exception as e:
        raise ValidationError(f'Не удалось прочитать файл: {e}')

    if header[:5] != b'%PDF-':
        raise ValidationError(
            'Файл не является PDF. Ожидается сигнатура %PDF- в начале файла.'
        )