// static/js/modal.js

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        const modal = document.getElementById('contactModal');
        const modalClose = document.getElementById('contactModalClose');
        const tariffSelect = document.getElementById('modalTariffSelect');
        const modalForm = document.getElementById('modalContactForm');

        if (!modal) return;

        // ============================================================
        // СБРОС ФОРМЫ
        // ВАЖНО: подзаголовок #modalSubtitle НЕ трогаем —
        // его рендерит Django через {% trans %} на нужном языке.
        // ============================================================
        function resetModalForm() {
            if (!modalForm) return;
            modalForm.reset();

            const valueGroup = document.getElementById('modalContactValueGroup');
            if (valueGroup) valueGroup.style.display = 'none';

            if (tariffSelect) tariffSelect.value = '';

            document.querySelectorAll('#modalContactForm .form-error').forEach(function(el) {
                el.classList.remove('show');
                el.textContent = '';
            });

            document.querySelectorAll('#modalContactForm .form-control').forEach(function(el) {
                el.classList.remove('error', 'success');
            });
        }

        // ============================================================
        // УСТАНОВКА ТАРИФА
        // ============================================================
        function setTariff(tariffName, tariffId) {
            if (!tariffSelect) return;

            tariffSelect.value = '';

            if (tariffId) {
                for (let i = 0; i < tariffSelect.options.length; i++) {
                    if (tariffSelect.options[i].value == tariffId) {
                        tariffSelect.value = tariffId;
                        return;
                    }
                }
            }

            if (tariffName) {
                const normalizedName = tariffName.trim().toLowerCase();
                for (let i = 0; i < tariffSelect.options.length; i++) {
                    const optionText = tariffSelect.options[i].text.trim().toLowerCase();
                    if (optionText.includes(normalizedName) || normalizedName.includes(optionText)) {
                        tariffSelect.value = tariffSelect.options[i].value;
                        return;
                    }
                }
                const firstWord = normalizedName.split(' ')[0];
                if (firstWord) {
                    for (let i = 0; i < tariffSelect.options.length; i++) {
                        const optionText = tariffSelect.options[i].text.trim().toLowerCase();
                        if (optionText.includes(firstWord)) {
                            tariffSelect.value = tariffSelect.options[i].value;
                            return;
                        }
                    }
                }
            }
        }

        // ============================================================
        // ОТКРЫТИЕ / ЗАКРЫТИЕ
        // ============================================================
        function openModal(tariffName, tariffId, serviceName) {
            resetModalForm();

            if (tariffName || tariffId) {
                setTariff(tariffName, tariffId);
            }

            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            document.body.classList.add('modal-open');
        }

        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            document.body.classList.remove('modal-open');
            resetModalForm();
        }

        // ============================================================
        // ДЕЛЕГИРОВАНИЕ КЛИКОВ (работает и для динамических элементов)
        // ============================================================
        document.addEventListener('click', function(e) {
            // 1. .open-modal — обычно у тарифов
            const openModalBtn = e.target.closest('.open-modal');
            if (openModalBtn) {
                e.preventDefault();
                e.stopPropagation();
                openModal(
                    openModalBtn.dataset.tariff || '',
                    openModalBtn.dataset.tariffId || null
                );
                return;
            }

            // 2. .js-open-contact-modal — у секций (landing, business, refactor)
            const jsOpenBtn = e.target.closest('.js-open-contact-modal');
            if (jsOpenBtn) {
                e.preventDefault();
                e.stopPropagation();
                openModal(
                    jsOpenBtn.dataset.tariff || '',
                    jsOpenBtn.dataset.tariffId || null,
                    jsOpenBtn.dataset.service || ''
                );
                return;
            }

            // 3. Специфические кнопки (hero, header, mobile)
            const headerBtn = e.target.closest('#heroContactBtn, .js-header-contact-btn, #mobileContactBtn');
            if (headerBtn) {
                e.preventDefault();
                e.stopPropagation();
                openModal();
                return;
            }
        });

        // ============================================================
        // ЗАКРЫТИЕ МОДАЛКИ
        // ============================================================

        if (modalClose) {
            modalClose.addEventListener('click', closeModal);
        }

        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeModal();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });

        // ============================================================
        // ЭКСПОРТ
        // ============================================================

        window.openModal = openModal;
        window.closeModal = closeModal;
    });
})();