// static/js/forms.js

/**
 * LYNXREACTOR — Обработка форм обратной связи
 * Использует FormData — работает с любой формой .cta-form, .contact-form, .modal-form.
 * Все строки интерфейса — через window.I18N (см. i18n_strings.html).
 */

(function() {
    'use strict';

    // ============================================================
    // I18N HELPER
    // ============================================================

    function t(key, fallback) {
        return (window.I18N && window.I18N[key]) || fallback || key;
    }

    // ============================================================
    // УВЕДОМЛЕНИЕ
    // ============================================================

    function notify(type, message) {
        if (typeof window.showNotification === 'function') {
            window.showNotification(type, message);
        } else {
            alert(message);
        }
    }

    // ============================================================
    // ДИНАМИЧЕСКИЕ ПОЛЯ (способы связи)
    // ============================================================

    const methodConfig = {
        phone: {
            label: t('phone_label', 'Номер телефона'),
            placeholder: t('phone_placeholder', '+375 (29) 123-45-67'),
            hint: t('phone_hint', 'Введите номер телефона с кодом страны')
        },
        telegram: {
            label: t('telegram_label', 'Telegram'),
            placeholder: t('telegram_placeholder', '@username или номер телефона'),
            hint: t('telegram_hint', 'Введите ваш Telegram')
        },
        whatsapp: {
            label: t('whatsapp_label', 'WhatsApp'),
            placeholder: t('whatsapp_placeholder', 'Номер телефона'),
            hint: t('whatsapp_hint', 'Введите номер телефона для WhatsApp')
        },
        viber: {
            label: t('viber_label', 'Viber'),
            placeholder: t('viber_placeholder', 'Номер телефона'),
            hint: t('viber_hint', 'Введите номер телефона для Viber')
        },
        email: {
            label: t('email_label', 'Email'),
            placeholder: t('email_placeholder', 'example@mail.com'),
            hint: t('email_hint', 'Введите ваш email')
        }
    };

    function initDynamicField(form) {
        const methodSelect = form.querySelector('select[name="contact_method"]');
        if (!methodSelect) return;

        const valueGroup = form.querySelector('.dynamic-field');
        if (!valueGroup) return;

        const valueInput = valueGroup.querySelector('input[name="contact_value"]');
        const valueLabel = valueGroup.querySelector('label');
        const valueHint  = valueGroup.querySelector('.form-hint');

        if (!valueInput) return;

        methodSelect.addEventListener('change', function() {
            const method = this.value;

            if (method && methodConfig[method]) {
                const config = methodConfig[method];
                valueGroup.style.display = 'block';
                if (valueLabel) valueLabel.innerHTML = config.label + ' <span class="required">*</span>';
                valueInput.placeholder = config.placeholder;
                if (valueHint) valueHint.textContent = config.hint;
                valueInput.required = true;
                valueInput.disabled = false;

                valueGroup.style.opacity = '0';
                valueGroup.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    valueGroup.style.transition = 'all 0.3s ease';
                    valueGroup.style.opacity = '1';
                    valueGroup.style.transform = 'translateY(0)';
                }, 50);
            } else {
                valueGroup.style.display = 'none';
                valueInput.required = false;
                valueInput.disabled = true;
                valueInput.value = '';
            }
        });

        if (methodSelect.value && methodConfig[methodSelect.value]) {
            methodSelect.dispatchEvent(new Event('change'));
        }
    }

    // ============================================================
    // ОТПРАВКА ФОРМЫ
    // ============================================================

    async function submitForm(form) {
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent.trim() : t('form_send_button', 'Отправить');

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const required = ['name', 'email', 'contact_method', 'contact_value', 'message'];
        const missing = required.filter(f => !data[f] || !String(data[f]).trim());

        if (missing.length > 0) {
            const labels = {
                name: t('label_name', 'Имя'),
                email: t('label_email', 'Email'),
                contact_method: t('label_contact_method', 'Способ связи'),
                contact_value: t('label_contact_value', 'Контактные данные'),
                message: t('label_message', 'Описание проекта')
            };
            notify('error', '❌ ' + t('form_fill_fields', 'Заполните поля') + ':\n• ' + missing.map(f => labels[f] || f).join('\n• '));
            return;
        }

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = t('form_sending', 'Отправка...');
        }

        form.querySelectorAll('.form-error').forEach(el => {
            el.textContent = '';
            el.classList.remove('show');
        });
        form.querySelectorAll('.form-control').forEach(el => el.classList.remove('error'));

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.getCsrfToken()
                },
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                notify('success', '✅ ' + (result.message || t('form_success', 'Заявка успешно отправлена!')));
                form.reset();

                const valueGroup = form.querySelector('.dynamic-field');
                if (valueGroup) valueGroup.style.display = 'none';

                if (window.turnstile) {
                    try { window.turnstile.reset(); } catch (e) {}
                }

                if (form.closest('#contactModal')) {
                    const modal = document.getElementById('contactModal');
                    if (modal) {
                        setTimeout(() => {
                            modal.classList.remove('active');
                            document.body.style.overflow = '';
                            document.body.classList.remove('modal-open');
                        }, 1500);
                    }
                }
            } else {
                let errorMessage = result.error || result.message || t('form_error', 'Ошибка отправки');

                if (result.errors && typeof result.errors === 'object') {
                    const fieldLabels = {
                        name: t('label_name', 'Имя'),
                        email: t('label_email', 'Email'),
                        contact_method: t('label_contact_method', 'Способ связи'),
                        contact_value: t('label_contact_value', 'Контактные данные'),
                        message: t('label_message', 'Описание проекта')
                    };

                    const lines = [];
                    Object.entries(result.errors).forEach(([field, msg]) => {
                        lines.push(`• ${fieldLabels[field] || field}: ${msg}`);

                        const input = form.querySelector(`[name="${field}"]`);
                        if (input) {
                            input.classList.add('error');
                            const errEl = input.parentNode.querySelector('.form-error');
                            if (errEl) {
                                errEl.textContent = msg;
                                errEl.classList.add('show');
                            }
                            setTimeout(() => input.classList.remove('error'), 3000);
                        }
                    });

                    errorMessage = '❌ ' + t('form_errors_in_form', 'Ошибки в форме') + ':\n' + lines.join('\n');
                }

                notify('error', errorMessage);
            }
        } catch (error) {
            console.error('Form submit error:', error);
            notify('error', '❌ ' + t('form_unexpected_error', 'Произошла ошибка. Попробуйте позже.'));
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    }

    // ============================================================
    // ДЕЛЕГИРОВАНИЕ SUBMIT
    // ============================================================

    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (!form.matches('.cta-form, .contact-form, .modal-form, #ctaForm, #contactForm, #modalContactForm')) {
            return;
        }

        e.preventDefault();
        submitForm(form);
    });

    // ============================================================
    // ИНИЦИАЛИЗАЦИЯ ДИНАМИЧЕСКИХ ПОЛЕЙ
    // ============================================================

    function initAllForms() {
        document.querySelectorAll('.cta-form, .contact-form, .modal-form').forEach(initDynamicField);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllForms);
    } else {
        initAllForms();
    }

    console.log('📝 Forms.js initialized (FormData + i18n)');
})();