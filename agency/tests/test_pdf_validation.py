# agency/tests/test_pdf_validation.py
"""
Тесты PDF-валидации (validators.validate_pdf_file + FileExtensionValidator).
"""
import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from agency.validators import validate_pdf_file


# ============================================================
# ВАЛИДНЫЙ PDF
# ============================================================

def test_valid_pdf_accepted():
    """Файл с %PDF- сигнатурой — принимается."""
    valid_pdf = SimpleUploadedFile(
        'document.pdf',
        b'%PDF-1.4\n%fake content for test\n%%EOF',
        content_type='application/pdf',
    )
    # Не должно бросить
    validate_pdf_file(valid_pdf)


# ============================================================
# ПОДДЕЛКА: .pdf с неверной сигнатурой
# ============================================================

def test_fake_pdf_rejected():
    """Файл .pdf с EXE-сигнатурой (MZ) — отклоняется."""
    fake_pdf = SimpleUploadedFile(
        'fake.pdf',
        b'MZ\x90\x00\x03\x00\x00\x00',  # EXE-сигнатура
        content_type='application/pdf',
    )
    with pytest.raises(ValidationError) as exc_info:
        validate_pdf_file(fake_pdf)
    assert '%PDF-' in str(exc_info.value)


# ============================================================
# НЕ-PDF файл
# ============================================================

def test_exe_file_rejected():
    """
    Файл с расширением .exe — отклоняется FileExtensionValidator
    (тестируется через модель BlogPost.pdf_file).
    """
    from agency.models import BlogPost

    exe_file = SimpleUploadedFile(
        'malware.exe',
        b'MZ\x90\x00\x03\x00\x00\x00',
        content_type='application/octet-stream',
    )

    # Достаём валидаторы поля pdf_file
    field = BlogPost._meta.get_field('pdf_file')
    validators = field.validators  # FileExtensionValidator + validate_pdf_file

    with pytest.raises(ValidationError):
        for validator in validators:
            validator(exe_file)