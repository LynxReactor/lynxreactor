"""
Кастомные виджеты для админ-панели LYNXREACTOR
"""

from django import forms
from django.core.exceptions import ValidationError
import json
import logging

logger = logging.getLogger(__name__)


class JSONFieldWidget(forms.Textarea):
    """
    Универсальный виджет для JSON полей с подсветкой синтаксиса
    """

    def __init__(self, attrs=None, allow_null=False, pretty=True):
        self.allow_null = allow_null
        self.pretty = pretty

        default_attrs = {
            'style': '''
                width: 100%; 
                font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace; 
                font-size: 13px; 
                min-height: 150px; 
                background: #0d1117; 
                color: #e6edf3; 
                padding: 16px; 
                border-radius: 8px; 
                border: 1px solid #30363d; 
                line-height: 1.6; 
                tab-size: 2;
            ''',
            'spellcheck': 'false',
            'class': 'vLargeTextField json-editor',
            'data-json-field': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Форматирует значение для отображения"""
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            try:
                if self.pretty:
                    return json.dumps(value, ensure_ascii=False, indent=2)
                return json.dumps(value, ensure_ascii=False)
            except TypeError:
                return str(value)
        return str(value)

    def value_from_datadict(self, data, files, name):
        """Парсит JSON из текстового поля"""
        value = data.get(name, '')
        if not value or value.strip() == '':
            return None if self.allow_null else {}

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            # Если это не JSON, но начинается с [ или { - ошибка
            if value.strip().startswith('[') or value.strip().startswith('{'):
                raise ValidationError(
                    f'❌ Ошибка в JSON: {str(e)}\n\n'
                    f'Проверьте правильность синтаксиса:\n'
                    f'• Используйте двойные кавычки для ключей и строк\n'
                    f'• Убедитесь, что нет лишних запятых\n'
                    f'• Проверьте правильность вложенных структур\n\n'
                    f'Пример правильного формата:\n'
                    f'["элемент 1", "элемент 2", "элемент 3"]'
                )
            # Возвращаем как простой текст
            return value

    class Media:
        css = {
            'all': ('admin/css/json-editor.css',)
        }
        js = ('admin/js/json-editor.js',)


class PrettyJSONWidget(forms.Textarea):
    """
    Простой виджет для JSON с автоматическим форматированием
    """

    def __init__(self, attrs=None, allow_null=False):
        self.allow_null = allow_null
        default_attrs = {
            'style': '''
                width: 100%; 
                font-family: "Consolas", "Courier New", monospace; 
                font-size: 13px; 
                min-height: 120px; 
                background: #1a1a2e; 
                color: #e0e0e0; 
                padding: 12px; 
                border-radius: 6px; 
                border: 1px solid #333;
            ''',
            'class': 'vLargeTextField'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, (dict, list)):
            try:
                if self.pretty:
                    return json.dumps(value, ensure_ascii=False, indent=2)
                return json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.debug(f'JSONFieldWidget: cannot serialize value: {e}')
                return str(value)
        return str(value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        if not value or value.strip() == '':
            return None if self.allow_null else {}
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            if value.strip().startswith('[') or value.strip().startswith('{'):
                raise ValidationError(f'❌ Некорректный JSON: {str(e)}')
            return value


class ImagePreviewWidget(forms.ClearableFileInput):
    """
    Виджет для отображения превью изображения в админке
    """

    def __init__(self, attrs=None, template_name=None, preview_width=200):
        self.preview_width = preview_width
        super().__init__(attrs, template_name)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if value and hasattr(value, 'url'):
            context['widget']['preview'] = {
                'url': value.url,
                'width': self.preview_width,
            }

        return context

    class Media:
        css = {
            'all': ('admin/css/image-preview.css',)
        }


class ColorPickerWidget(forms.TextInput):
    """
    Виджет для выбора цвета
    """

    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'color',
            'style': 'width: 60px; height: 40px; padding: 2px; cursor: pointer;',
            'class': 'color-picker'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = {
            'all': ('admin/css/color-picker.css',)
        }


class MultiLangJSONWidget(forms.Textarea):
    """Виджет для мультиязычного JSON поля"""

    def __init__(self, attrs=None):
        default_attrs = {
            'style': '''
                width: 100%; 
                font-family: "Consolas", monospace; 
                font-size: 13px; 
                min-height: 150px; 
                background: #0d1117; 
                color: #e6edf3; 
                padding: 12px; 
                border-radius: 8px; 
                border: 1px solid #30363d;
            ''',
            'class': 'vLargeTextField json-editor',
            'placeholder': '{"ru": ["Особенность 1", "Особенность 2"], "en": ["Feature 1", "Feature 2"]}'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, dict):
            try:
                return json.dumps(value, ensure_ascii=False, indent=2)
            except (TypeError, ValueError) as e:
                logger.debug(f'MultiLangJSONWidget: cannot serialize value: {e}')
                return str(value)
        return str(value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        if not value or value.strip() == '':
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}