# agency/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_cf_turnstile.fields import TurnstileCaptchaField
from .models import ContactRequest, Tariff, BlogCategory
import re


class ContactForm(forms.ModelForm):
    """
    Форма обратной связи с динамическими полями и Turnstile
    """

    captcha = TurnstileCaptchaField(label=_('Verification'))

    contact_method = forms.ChoiceField(
        choices=ContactRequest.CONTACT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control contact-method-select',
            'id': 'contactMethod',
            'required': 'required'
        }),
        label=_('Select primary contact method')
    )

    contact_value = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'contactValue',
            'placeholder': _('Enter contact details')
        }),
        label=_('Contact details')
    )

    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.filter(is_active=True),
        required=False,
        empty_label=_('Select tariff'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'tariffSelect'
        }),
        label=_('Interested tariff')
    )

    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'userName',
                'placeholder': _('Your name'),
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'userEmail',
                'placeholder': 'example@mail.com',
                'required': 'required'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'projectDescription',
                'placeholder': _('Describe your project...'),
                'rows': 5,
                'required': 'required'
            }),
        }
        labels = {
            'name': _('Your name'),
            'email': 'Email',
            'message': _('Describe your project'),
        }
        help_texts = {
            'name': _('Enter your full name'),
            'email': _('We will send a response to this email'),
            'message': _('Describe your project in detail'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tariff'].required = False
        self.fields['contact_method'].required = True

        # Добавляем классы для стилей
        for field_name, field in self.fields.items():
            if field_name not in ['captcha', 'contact_method', 'tariff']:
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_contact_value(self):
        """Валидация контактных данных"""
        # Если contact_method провалил валидацию — не дублируем ошибку
        if 'contact_method' not in self.cleaned_data:
            return ''

        contact_method = self.cleaned_data['contact_method']
        contact_value = self.cleaned_data.get('contact_value', '').strip()

        if not contact_value:
            raise ValidationError(_('Please enter contact details'))

        # Валидация для телефона
        if contact_method == 'phone':
            cleaned = re.sub(r'[^\d+]', '', contact_value)
            if len(cleaned) < 10:
                raise ValidationError(_('Please enter a valid phone number (minimum 10 digits)'))

        # Валидация для email (дополнительная, т.к. пользователь может ввести email в это поле)
        if contact_method == 'email':
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', contact_value):
                raise ValidationError(_('Please enter a valid email address'))

        return contact_value

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError(_('Please enter your name'))
        if len(name) < 2:
            raise ValidationError(_('Name must be at least 2 characters long'))
        return name

    def clean_email(self):
        """Email валидируется через EmailField, дополнительная проверка не нужна"""
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError(_('Please enter your email'))
        # EmailField уже сделал валидацию, но оставляем проверку на наличие
        return email

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise ValidationError(_('Please describe your project'))
        if len(message) < 10:
            raise ValidationError(_('Project description must be at least 10 characters long'))
        return message

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.contact_method = self.cleaned_data.get('contact_method', '')
        instance.contact_value = self.cleaned_data.get('contact_value', '')
        instance.tariff = self.cleaned_data.get('tariff')

        if instance.contact_method == 'phone':
            instance.phone = instance.contact_value

        if commit:
            instance.save()

        return instance


class AjaxContactForm(ContactForm):
    """
    Версия ContactForm для AJAX endpoint.

    Отличия от родителя:
    - Нет поля captcha — Turnstile валидируется отдельно в ajax_contact.
      Это позволяет не дублировать логику проверки CF.

    Вся остальная валидация унаследована:
    - name (min 2, max from model)
    - email (EmailField)
    - message (min 10)
    - contact_method (choices)
    - contact_value (max_length + валидация по методу)
    - tariff (queryset is_active=True)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Удаляем captcha-поле — Turnstile в ajax_contact проверяется вручную
        self.fields.pop('captcha', None)


class TariffForm(forms.Form):
    """Форма выбора тарифа"""

    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.filter(is_active=True),
        required=False,
        empty_label=_('Select tariff'),
        widget=forms.Select(attrs={
            'class': 'form-control tariff-select',
            'onchange': 'this.form.submit()'
        })
    )


class BlogSearchForm(forms.Form):
    """Форма поиска по блогу"""

    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles...'),
            'aria-label': _('Search')
        })
    )

    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label=_('All categories'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = BlogCategory.objects.filter(is_active=True)


class AdminContactForm(forms.ModelForm):
    """Форма для админки - управление заявками"""

    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'phone', 'message', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'vTextField'}),
            'email': forms.EmailInput(attrs={'class': 'vTextField'}),
            'phone': forms.TextInput(attrs={'class': 'vTextField'}),
            'message': forms.Textarea(attrs={'class': 'vLargeTextField', 'rows': 10}),
            'status': forms.Select(attrs={'class': 'vSelectField'}),
        }

    # ============================================================
    # SUBSCRIBE FORM
    # ============================================================


class SubscribeForm(forms.Form):
    """Форма подписки на обновления блога."""

    email = forms.EmailField(
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control subscribe-input',
            'placeholder': _('Your email'),
            'autocomplete': 'email',
            'required': 'required',
        }),
        label=_('Email'),
    )

    source = forms.CharField(
        required=False,
        max_length=50,
        initial='blog_detail',
        widget=forms.HiddenInput(),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError(_('Please enter your email'))
        return email